# Stock Newsletter Generator

This project is a Python-based tool that allows users to generate a weekly stock newsletter. It fetches stock data from Yahoo Finance, retrieves relevant news articles, and generates a summary using OpenAI's GPT-4 model. The generated newsletter is then sent via email.

## Features

- Fetch stock data from Yahoo Finance
- Retrieve relevant news articles using the News API
- Generate detailed financial analyses using OpenAI's GPT-4 model
- Send the generated newsletter via email
- User-friendly Tkinter interface to input, update, and modify stock tickers and units

## Requirements

- Python 3.7+
- `openai`
- `yfinance`
- `smtplib`
- `tkinter`
- `python-dotenv`
- `newsapi-python`
- `pandas`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/stock-newsletter.git
    cd stock-newsletter
    ```

2. Install the required Python packages:
    ```bash
    pip install openai yfinance python-dotenv newsapi-python pandas
    ```

3. Create a `.env` file in the project directory and add the following environment variables:
    ```
    OPENAI_API_KEY=your_openai_api_key
    NEWS_API_KEY=your_news_api_key
    SMTP_SERVER=smtp.office365.com
    SMTP_PORT=587
    SMTP_USERNAME=your_smtp_username
    SMTP_PASSWORD=your_smtp_password
    FROM_EMAIL=your_email@example.com
    TO_EMAIL=recipient_email@example.com
    ```

## Usage

1. Run the script:
    ```bash
    python main.py
    ```

2. The Tkinter interface will open, displaying existing data from the `portfolio.csv` file if it exists. You can enter new stock tickers and units or update existing ones.

3. After entering the stock tickers and units, click the "Submit" button. The data will be saved to `portfolio.csv`.

4. The script will fetch the stock data and news articles, generate the newsletter, and send it via email.

## Updating Stock Data Using Tkinter Interface

The Tkinter interface allows you to update existing stock tickers and units. Here's how it works:

- If a `portfolio.csv` file exists, the interface will pre-fill the entries with existing data.
- You can modify the existing data or add new stock tickers and units.
- If you leave the units field empty for a ticker, it will be included only in the newsletter portion and not in the portfolio summary.
- Click "Submit" to save the changes and close the interface. The updated data will be saved back to `portfolio.csv`.

## CSV File Structure

The `portfolio.csv` file has the following structure:
```
Ticker,Units
AAPL,10
GOOGL,5
MSFT,
```

- `Ticker`: The stock ticker symbol.
- `Units`: The number of units (optional).

## Example

After running the script and updating the data using the Tkinter interface, the script will generate an email with a portfolio summary and detailed financial analyses of the specified stocks.