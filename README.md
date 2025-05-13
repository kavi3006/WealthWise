# WealthWise

WealthWise is an intelligent financial analysis and dashboard application that helps users track, analyze, and understand their personal finances through interactive visualizations and AI-powered insights.

## Features

- 📊 Interactive Dashboard: Visualize your financial data with dynamic charts and graphs
- 🤖 AI-Powered Analysis: Get intelligent insights about your spending patterns
- 💬 Chatbot Assistant: Interact with an AI chatbot for financial queries
- 📈 Transaction Analysis: Analyze your spending habits and financial trends
- 🔍 Pattern Recognition: Identify spending patterns using machine learning

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/WealthWise.git
cd WealthWise
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the dashboard:
```bash
streamlit run dashboard.py
```

2. Access the dashboard in your web browser at `http://localhost:8501`

## User Credentials

The application uses a secure credential system to manage user access. User credentials are stored in `user_credentials.py`. To set up your credentials:

1. Open `user_credentials.py`
2. Add your credentials in the following format:
```python
credentials = {
    user1 - 
    "username": "aaditya",
    "password": "aaditya"

    user2 - 
    "username": "kavi",
    "password": "kavi"

    user3 - 
    "username": "virnit",
    "password": "virnit"

    user4 - 
    "username": "padam",
    "password": "padam"

    user5 - 
    "username": "tappu",
    "password": "tappu"
}
```

For security reasons:
- Use strong passwords
- Never commit your actual credentials to version control
- Keep your credentials file private
- Consider using environment variables for sensitive information

## Project Structure

- `dashboard.py`: Main Streamlit dashboard application
- `model.py`: Machine learning models for financial analysis
- `chatbot.py`: AI chatbot implementation
- `user_credentials.py`: User authentication and credentials management
- `kmeans_model.pkl`: Pre-trained clustering model
- `personal_transactions.csv`: Sample transaction data

## Dependencies

- streamlit==1.32.0
- pandas==2.2.1
- matplotlib==3.8.3
- seaborn==0.13.2
- plotly==5.19.0
- scikit-learn==1.5.0
- joblib==1.3.2
- nltk==3.8.1
- numpy==1.26.4

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any questions or suggestions, please open an issue in the GitHub repository. 