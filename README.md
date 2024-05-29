# Stock Portfolio and Newsletter

This project provides a tool for creating a stock portfolio and generating a weekly newsletter containing financial information and recent news about selected stocks.

## Features

- Fetches current stock prices and changes using Yahoo Finance
- Retrieves recent news articles related to the stocks using News API
- Generates a report with stock performance and news summary using GPT-4
- Sends the report via email

## Requirements

- Python 3.x
- `requests` library
- `openai` library
- `yfinance` library
- `tkinter` library
- News API key from [newsapi.org](https://newsapi.org/)
- OpenAI API key from [openai.com](https://openai.com/)
- SMTP server details for sending emails

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Stock-Portfolio-and-Newsletter.git
    cd Stock-Portfolio-and-Newsletter
    ```

2. Install the required libraries:
    ```bash
    pip install requests openai yfinance
    ```

3. Set up your API keys and email credentials:
    - Create a `.env` file in the root directory
    - Add your API keys and email credentials in the following format:
        ```
        NEWS_API_KEY=your_news_api_key
        OPENAI_API_KEY=your_openai_api_key
        SMTP_SERVER=smtp.your-email-provider.com
        SMTP_PORT=587
        SMTP_USERNAME=your_email_username
        SMTP_PASSWORD=your_email_password
        FROM_EMAIL=your_email@example.com
        TO_EMAIL=recipient_email@example.com
        ```

## Usage

Run the script and follow the prompts to enter stock tickers and units:
```bash
python main.py
```

The generated report will be printed in the console and sent via email.

## Contributing

Feel free to submit pull requests to enhance the functionality or fix issues.