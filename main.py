import openai
import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import ttk
import os
from newsapi import NewsApiClient
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import re

# Load environment variables from .env file
load_dotenv()

# Initialize variables from .env
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
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

COLOR_PALETTE = ['#03045E', '#023E8A', '#0077B6', '#0096C7', '#00B4D8', 
                 '#48CAE4', '#90E0EF', '#ADE8F4', '#CAF0F8']

def get_company_name(ticker):
    """Fetches the company name for a given stock ticker."""
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    return stock_info.get('shortName', 'Unknown Company')

def fetch_stock_news(company_name):
    """Fetches the latest news articles for a given company name."""
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

def bold_numbers(text):
    """Bold all numbers and their surrounding symbols in the given text."""
    return re.sub(r'(\S*\d+\S*)', r'<b>\1</b>', text)

def analyze_data_with_gpt4(prompt, max_tokens=300):
    """Uses OpenAI's GPT-4 to generate a financial analysis based on the given prompt."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing detailed and cohesive analyses of stock news."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        analysis = response.choices[0].message.content
        return bold_numbers(analysis) # Bold the numbers in the analysis
    except Exception as e:
        return f"An error occurred: {e}"

def fetch_stock_data(stock_ticker):
    """Fetches the stock data for a given stock ticker."""
    stock = yf.Ticker(stock_ticker)
    stock_info = stock.info

    company_name = stock_info.get('shortName', 'Unknown Company')
    current_price = round(stock_info.get('currentPrice', 0), 2)
    previous_close = round(stock_info.get('regularMarketPreviousClose', 0), 2)
    market_cap = stock_info.get('marketCap')
    pe_ratio = stock_info.get('trailingPE')
    eps = stock_info.get('trailingEps')
    dividend_yield = stock_info.get('dividendYield')

    if current_price is not None and previous_close is not None:
        dollar_gain = round(current_price - previous_close, 2)
        percent_gain = round((dollar_gain / previous_close) * 100, 2)
    else:
        dollar_gain = None
        percent_gain = None
    
    return company_name, current_price, dollar_gain, percent_gain, market_cap, pe_ratio, eps, dividend_yield

def send_email(subject, body, inline_images=[]):
    """Sends an email with the given subject and body."""
    msg = MIMEMultipart('related')
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_text = MIMEText(body, 'html')
    msg_alternative.attach(msg_text)

    for image in inline_images:
        with open(image['path'], 'rb') as f:
            img_data = f.read()
        img = MIMEText(img_data, 'base64')
        img.add_header('Content-ID', f'<{image["cid"]}>')
        img.add_header('Content-Disposition', 'inline', filename=image['path'])
        msg.attach(img)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(FROM_EMAIL, TO_EMAIL, text)
    server.quit()

def get_user_input():
    """Prompts the user to enter stock tickers and units."""
    portfolio = {}
    newsletter_only = []

    # Load existing data from CSV
    existing_data = []
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        for index, row in df.iterrows():
            existing_data.append((row['Ticker'], str(row['Units']) if pd.notnull(row['Units']) else ''))

    def submit():
        portfolio.clear()
        newsletter_only.clear()
        for entry in entries:
            ticker = entry[0].get().strip()
            units = entry[1].get().strip()
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

    def add_row():
        ticker_entry = ttk.Entry(main_frame, justify='center', style="TEntry")
        units_entry = ttk.Entry(main_frame, justify='center', style="TEntry")
        row_position = len(entries) + 1
        ticker_entry.grid(row=row_position, column=0, padx=5, pady=5)
        units_entry.grid(row=row_position, column=1, padx=5, pady=5)
        entries.append((ticker_entry, units_entry))
        main_frame.grid_rowconfigure(row_position, weight=1)

        # Move the buttons down
        add_row_button.grid(row=row_position + 1, column=0, columnspan=2, pady=10)
        submit_button.grid(row=row_position + 2, column=0, columnspan=2, pady=10)

    root = tk.Tk()
    root.title("Stock Input")
    root.geometry("400x600")  # Increased window size

    # Set a consistent color scheme
    root.configure(bg='#03045E')

    # Define custom styles
    style = ttk.Style()
    style.configure("TLabel", font=('Helvetica', 12, 'bold'), background='#03045E', foreground='#FFFFFF', padding=5)
    style.configure("TEntry", font=('Helvetica', 12, 'bold'), padding=5, relief="solid", bordercolor='#00B4D8', borderwidth=2)
    style.configure("TButton", font=('Helvetica', 12, 'bold'), padding=5, relief="solid", bordercolor='#00B4D8', borderwidth=2)
    style.configure("TFrame", background='#03045E')

    # Main frame
    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Title label
    ttk.Label(main_frame, text="Enter Stock Tickers and Units (Optional)", style="TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))

    entries = []
    for i in range(5):  # Start with 5 rows
        ticker_entry = ttk.Entry(main_frame, justify='center', style="TEntry")
        units_entry = ttk.Entry(main_frame, justify='center', style="TEntry")
        if i < len(existing_data):
            ticker, units = existing_data[i]
            ticker_entry.insert(0, ticker)
            units_entry.insert(0, units)
        ticker_entry.grid(row=i+1, column=0, padx=5, pady=5)
        units_entry.grid(row=i+1, column=1, padx=5, pady=5)
        entries.append((ticker_entry, units_entry))

    add_row_button = ttk.Button(main_frame, text="Add Row", command=add_row, style="TButton")
    add_row_button.grid(row=6, column=0, columnspan=2, pady=10)

    submit_button = ttk.Button(main_frame, text="Submit", command=submit, style="TButton")
    submit_button.grid(row=7, column=0, columnspan=2, pady=10)

    # Center the main frame
    for i in range(8):
        main_frame.grid_rowconfigure(i, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

    root.mainloop()

    return portfolio, newsletter_only

def generate_pie_chart(portfolio_data):
    """Generates a pie chart of the portfolio holdings."""
    labels = portfolio_data.keys()
    sizes = portfolio_data.values()
    colors = ['#03045E', '#023E8A', '#0077B6', '#0096C7', '#00B4D8', 
              '#48CAE4', '#90E0EF', '#ADE8F4', '#CAF0F8']

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontweight': 'bold'}, colors=colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Change the color of the numbers to white
    for autotext in autotexts:
        autotext.set_color('white')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()

    return image_base64

def main():
    """Main function to run the application."""
    global portfolio, newsletter_only
    portfolio = {}
    newsletter_only = []

    portfolio, newsletter_only = get_user_input()

    total_value = 0
    portfolio_values = {}
    portfolio_summary = "<h2>Portfolio Summary</h2>"
    email_body = ""

    for stock_ticker, units in portfolio.items():
        try:
            # Fetch stock data from Yahoo Finance
            company_name, current_price, dollar_gain, percent_gain, market_cap, pe_ratio, eps, dividend_yield = fetch_stock_data(stock_ticker)
            
            if current_price is not None:
                stock_value = current_price * units
                total_value += stock_value
                portfolio_values[company_name] = stock_value
                portfolio_summary += (f"<p><b>{company_name}</b> ({stock_ticker}): "
                                      f"{units:,} units @ {current_price:,.2f} USD/unit = {stock_value:,.2f} USD</p>")
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
            
            # Bold dollar and percentage values in analysis
            analysis = analysis.replace('$', '<b>$</b>').replace('%', '<b>%</b>')

            # Format the section header
            if stock_ticker in portfolio and current_price is not None and dollar_gain is not None and percent_gain is not None:
                header = (f"<b>{company_name}</b> "
                          f"{current_price:,.2f} USD "
                          f"{dollar_gain:+,.2f} USD "
                          f"({percent_gain:+,.2f}%)")
            else:
                header = f"<b>{company_name}</b> ({stock_ticker}) - News Analysis"
            
            # Append the section to the email body
            email_body += f"<p>{header}</p><p>{analysis}</p><hr>"

        except Exception as e:
            email_body += f"<p>An error occurred with {stock_ticker}: {e}</p><hr>"

    if email_body:
        # Prepare the email content
        email_subject = "Stock Sentinel"
        portfolio_summary += f"<p><b>Total Portfolio Value:</b> {total_value:,.2f} USD</p>"

        # Generate the pie chart
        chart_base64 = generate_pie_chart(portfolio_values)

        # Embed the chart in the email body
        full_email_body = portfolio_summary + "<hr>" + f'<img src="data:image/png;base64,{chart_base64}">' + "<hr>" + email_body
        send_email(email_subject, full_email_body)
        print("Email sent successfully!")
        print(full_email_body)
    else:
        print("No content to send.")

if __name__ == "__main__":
    main()