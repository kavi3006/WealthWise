import nltk
from nltk.chat.util import Chat, reflections
import pandas as pd
import numpy as np

# Download NLTK data files if not already installed
nltk.download("punkt")

class FinancialChatbot:
    def __init__(self, user_data):
        self.df = user_data
        # Ensure proper data types
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df["Month"] = self.df["Date"].dt.to_period("M")
        self.df["Amount"] = self.df["Amount"].abs()
        
    def get_total_spending(self, category=None):
        if category:
            return self.df[(self.df["Transaction Type"] == "debit") & 
                         (self.df["Category"] == category)]["Amount"].sum()
        return self.df[self.df["Transaction Type"] == "debit"]["Amount"].sum()
    
    def get_total_income(self):
        return self.df[self.df["Transaction Type"] == "credit"]["Amount"].sum()
    
    def get_category_spending(self):
        return self.df[self.df["Transaction Type"] == "debit"].groupby("Category")["Amount"].sum()
    
    def get_monthly_spending(self):
        return self.df[self.df["Transaction Type"] == "debit"].groupby("Month")["Amount"].sum()
    
    def get_spending_advice(self):
        total_spent = self.get_total_spending()
        total_income = self.get_total_income()
        savings_rate = (total_income - total_spent) / total_income * 100 if total_income > 0 else 0
        
        category_spending = self.get_category_spending()
        highest_category = category_spending.idxmax()
        highest_amount = category_spending.max()
        
        advice = []
        
        if savings_rate < 20:
            advice.append("Your savings rate is below recommended 20%. Consider reducing discretionary spending.")
        else:
            advice.append(f"Great job! You're saving {savings_rate:.1f}% of your income.")
            
        advice.append(f"Your highest spending category is {highest_category} (${highest_amount:,.2f}).")
        
        return advice
    
    def process_query(self, query):
        query = query.lower()
        
        # Total spending
        if "total spending" in query or "how much did i spend" in query:
            total = self.get_total_spending()
            return f"Your total spending is ${total:,.2f}"
        
        # Category specific spending
        for category in self.df["Category"].unique():
            if category.lower() in query and "spending" in query:
                amount = self.get_total_spending(category)
                return f"Your spending in {category} is ${amount:,.2f}"
        
        # Income related queries
        if "income" in query or "earnings" in query:
            income = self.get_total_income()
            return f"Your total income is ${income:,.2f}"
        
        # Savings and advice
        if "savings" in query or "advice" in query or "tips" in query:
            advice = self.get_spending_advice()
            return "\n".join(advice)
        
        # Monthly spending
        if "monthly" in query and "spending" in query:
            monthly = self.get_monthly_spending()
            latest_month = monthly.index[-1]
            latest_spending = monthly.iloc[-1]
            return f"Your spending in {latest_month} was ${latest_spending:,.2f}"
        
        # Default response
        return ("I can help you with:\n"
                "- Total spending\n"
                "- Category-specific spending\n"
                "- Income information\n"
                "- Monthly spending\n"
                "- Financial advice\n"
                "\nTry asking something like 'What's my total spending?' or 'How much did I spend on groceries?'")

# Define a set of chatbot responses
def spent_on_category(match):
    category_spend = df[df['Description'].str.contains(match[2], case=False, na=False)]['Amount'].sum()
    return f"You spent ${category_spend} on {match[2]}."

def total_spending(match):
    return f"Your total spending is ${df['Amount'].sum()}"

def save_money(match):
    return "Try reducing unnecessary expenses like entertainment, dining out, and impulse purchases."

def spending_in_month(match):
    month_spend = df[df['Month'] == match[1]]['Amount'].sum()
    return f"In {match[1]} month, you spent ${month_spend}"

def spent_on_specific_category(match):
    category_spend = df[df['Category'].str.contains(match[1], case=False, na=False)]['Amount'].sum()
    return f"You spent ${category_spend} on {match[1]}."

# Adjusting regex patterns to handle more general cases
pairs = [
    # Match for total spending
    (r"(.*) spent on (.*)", [spent_on_category]),

    # Match for total spending
    (r"(.*) total spending(.*)", [total_spending]),

    # Match for saving tips
    (r"How can I save money\??", [save_money]),

    # Monthly spending query
    (r"(.*) in (.*) month", [spending_in_month]),

    # Query for specific categories
    (r"(.*) on (.*)\?", [spent_on_specific_category])
]

# Create chatbot instance
chatbot = Chat(pairs, reflections)

# Remove the infinite loop since we're using Streamlit for interaction
def get_response(user_input):
    response = chatbot.respond(user_input)
    return response if response else "Sorry, I didn't understand that. Please ask something else."
