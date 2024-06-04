import openai
import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
import pandas as pd

# Fetch credentials from environment variables
load_dotenv()

# Fetch from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize the News API client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

NEWS_DOMAINS = [
    "yahoofinance.com",
    "cnbc.com",
    "barrons.com",
    "marketwatch.com",
    "bloomberg.com",
    "nasdaq.com",
    "reuters.com",
    "wsj.com"
]

CSV_FILE = "portfolio.csv"

def get_company_name(ticker):
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    return stock_info.get('shortName', 'Unknown Company')

def fetch_stock_news(company_name):
    try:
        all_articles = newsapi.get_everything(
            q=company_name,
            domains=','.join(NEWS_DOMAINS),
            language='en',
            sort_by='relevancy'
        )
        if all_articles['status'] == 'ok':
            return all_articles
        else:
            raise Exception(f"News API error: {all_articles.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to fetch news for {company_name}: {e}")
        return None

def analyze_data_with_gpt4(prompt, max_tokens=300):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing detailed and cohesive analyses of stock news."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def fetch_stock_data(stock_ticker):
    stock = yf.Ticker(stock_ticker)
    stock_info = stock.info

    company_name = stock_info.get('shortName', 'Unknown Company')
    current_price = stock_info.get('currentPrice')
    previous_close = stock_info.get('regularMarketPreviousClose')
    market_cap = stock_info.get('marketCap')
    pe_ratio = stock_info.get('trailingPE')
    eps = stock_info.get('trailingEps')
    dividend_yield = stock_info.get('dividendYield')

    if current_price is not None and previous_close is not None:
        dollar_gain = current_price - previous_close
        percent_gain = (dollar_gain / previous_close) * 100
    else:
        dollar_gain = None
        percent_gain = None
    
    return company_name, current_price, dollar_gain, percent_gain, market_cap, pe_ratio, eps, dividend_yield

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(FROM_EMAIL, TO_EMAIL, text)
    server.quit()

def get_user_input():
    portfolio = {}
    newsletter_only = []

    # Load existing data from CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        for index, row in df.iterrows():
            if pd.notnull(row['Units']):
                portfolio[row['Ticker']] = int(row['Units'])
            else:
                newsletter_only.append(row['Ticker'])

    def submit():
        for i in range(len(entries)):
            ticker = entries[i][0].get().strip()
            units = entries[i][1].get().strip()
            if ticker:
                if units:
                    try:
                        portfolio[ticker] = int(units)
                    except ValueError:
                        print(f"Invalid units for {ticker}. Skipping.")
                else:
                    newsletter_only.append(ticker)
        root.destroy()

        # Save data to CSV
        data = {'Ticker': list(portfolio.keys()) + newsletter_only, 'Units': list(portfolio.values()) + [None] * len(newsletter_only)}
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE, index=False)

    root = tk.Tk()
    root.title("Stock Input")

    tk.Label(root, text="Enter Stock Tickers and Units (Optional)").grid(row=0, column=0, columnspan=2)

    entries = []
    for i in range(10):  # Allow up to 10 tickers
        ticker_entry = tk.Entry(root)
        ticker_entry.grid(row=i+1, column=0)
        units_entry = tk.Entry(root)
        units_entry.grid(row=i+1, column=1)
        entries.append((ticker_entry, units_entry))

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.grid(row=11, column=0, columnspan=2)

    root.mainloop()

    return portfolio, newsletter_only

def main():
    global portfolio, newsletter_only
    portfolio = {}
    newsletter_only = []

    portfolio, newsletter_only = get_user_input()

    total_value = 0
    portfolio_summary = "<h2>Portfolio Summary</h2>"
    email_body = ""

    for stock_ticker, units in portfolio.items():
        try:
            # Fetch stock data from Yahoo Finance
            company_name, current_price, dollar_gain, percent_gain, market_cap, pe_ratio, eps, dividend_yield = fetch_stock_data(stock_ticker)
            
            if current_price is not None:
                stock_value = current_price * units
                total_value += stock_value
                portfolio_summary += (f"<p><b>{company_name}</b> ({stock_ticker}): "
                                      f"{units} units @ {current_price:.2f} USD/unit = {stock_value:.2f} USD</p>")
            else:
                portfolio_summary += f"<p><b>{stock_ticker}</b> - Price information not available</p>"

        except Exception as e:
            portfolio_summary += f"<p>An error occurred with {stock_ticker}: {e}</p><hr>"

    for stock_ticker in portfolio.keys() | set(newsletter_only):
        try:
            # Fetch company name for accurate news search
            company_name = get_company_name(stock_ticker)
            # Fetch news data
            news_data = fetch_stock_news(company_name)
            if news_data is None:
                email_body += f"<p>Failed to fetch news for {company_name} ({stock_ticker}).</p><hr>"
                continue

            articles = news_data.get("articles", [])
            if not articles:
                email_body += f"<p>No news articles found for {company_name} ({stock_ticker}).</p>"
                continue

            # Fetch stock data again to include in the prompt
            company_name, current_price, dollar_gain, percent_gain, market_cap, pe_ratio, eps, dividend_yield = fetch_stock_data(stock_ticker)

            # Prepare a prompt for GPT-4
            prompt = (
                f"Write a detailed financial analysis like a Wall Street Journal article for {company_name} ({stock_ticker}). "
                f"Include the most important and interesting financial metrics from the following: Current Price: {current_price}, Dollar Gain: {dollar_gain}, Percent Gain: {percent_gain}, Market Cap: {market_cap}, P/E Ratio: {pe_ratio}, EPS: {eps}, Dividend Yield: {dividend_yield}. "
                f"The summary should be around 200 words and focus on the most important and interesting news articles.\n\n"
                f"Recent news articles:\n"
            )
            for article in articles[:5]:  # Limiting to the top 5 articles
                prompt += f"Title: {article['title']}\n"
                if 'content' in article and article['content']:
                    prompt += f"Content: {article['content']}\n"
                elif 'description' in article and article['description']:
                    prompt += f"Description: {article['description']}\n"
                else:
                    prompt += "No content or description available.\n"
            
            # Analyze data with GPT-4
            analysis = analyze_data_with_gpt4(prompt, max_tokens=2000)
            
            # Format the section header
            if stock_ticker in portfolio and current_price is not None and dollar_gain is not None and percent_gain is not None:
                header = (f"<b>{company_name}</b> "
                          f"{current_price:.2f} USD "
                          f"{dollar_gain:+.2f} USD "
                          f"({percent_gain:+.2f}%)")
            else:
                header = f"<b>{company_name}</b> ({stock_ticker}) - News Analysis"
            
            # Append the section to the email body
            email_body += f"<p>{header}</p><p>{analysis}</p><hr>"

        except Exception as e:
            email_body += f"<p>An error occurred with {stock_ticker}: {e}</p><hr>"

    if email_body:
        # Prepare the email content
        email_subject = "Weekly Portfolio Update"
        portfolio_summary += f"<p><b>Total Portfolio Value:</b> {total_value:.2f} USD</p>"
        full_email_body = portfolio_summary + "<hr>" + email_body
        send_email(email_subject, full_email_body)
        print("Email sent successfully!")
        print(full_email_body)
    else:
        print("No content to send.")

if __name__ == "__main__":
    main()
