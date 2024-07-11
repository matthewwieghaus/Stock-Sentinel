
# Stock Sentinel

This project allows you to manage a stock portfolio, fetch financial data and news, and generate detailed financial analysis reports using OpenAI's GPT-4 model.

## Features

- Fetch stock data from Yahoo Finance
- Retrieve relevant news articles using the News API
- Generate detailed financial analyses using OpenAI's GPT-4 model
- Send a weekly portfolio update via email

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/stock-portfolio-newsletter.git
   cd stock-portfolio-newsletter
   ```

2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the `.env.example`:
   ```sh
   cp .env.example .env
   ```

5. Populate the `.env` file with your API keys and email credentials.

## Usage

1. Run the main script:
   ```sh
   python main.py
   ```

2. Follow the prompts to enter your stock tickers and units.

## Sample Output
![image](https://github.com/user-attachments/assets/4702e794-45de-4310-a0fc-c70272d0fd2f)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
