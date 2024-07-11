
# Stock Sentinel

Stock Sentinel is a comprehensive stock portfolio management and financial analysis application. It allows users to manage stock portfolios, fetch real-time financial data, retrieve relevant news articles, and generate detailed financial analysis reports.

## Features

-Real-Time Data Fetching: Retrieves stock data from Yahoo Finance.
-News Integration: Fetches relevant news articles using the News API.
-Advanced Analysis: Uses OpenAI's GPT-4 model to generate in-depth, professional-grade analysis of stock performance.
-User-Friendly Interface: Developed a Tkinter-based GUI for easy input and management of stock tickers and units.
-Automated Reporting: Generates and emails weekly portfolio summaries and detailed stock analysis reports.

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
