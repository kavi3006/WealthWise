import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from model import apply_kmeans_clustering
import joblib
import os
from user_credentials import verify_credentials, USERS
from chatbot import FinancialChatbot
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="WealthWise",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main content styling */
    .main {
        padding: 0 !important;
        background-color: #1a1a2e !important;
        color: white !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1a1a2e;
        color: white;
    }
    
    /* Card styling */
    .metric-card {
        background-color: #1E1E3F;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        color: white;
    }
    
    /* Chart containers */
    .chart-container {
        background-color: #1E1E3F;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
    }
    
    /* Navigation menu items */
    .nav-item {
        padding: 10px;
        color: white;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background-color: rgba(75, 111, 255, 0.1);
    }

    /* Transaction list styling */
    .transaction-item {
        background-color: #1E1E3F;
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        color: white;
    }

    /* Search bar styling */
    .search-container {
        padding: 10px;
        background-color: #1E1E3F;
        border-radius: 8px;
        margin: 10px 0;
        color: white;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #1E1E3F;
        border-radius: 8px;
        padding: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px;
        color: white;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4B6FFF !important;
        color: white !important;
    }

    /* Override Streamlit's default styling */
    .stApp {
        background-color: #1a1a2e;
    }

    .css-1y4p8pa {
        max-width: none !important;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: white !important;
    }

    [data-testid="stMetricLabel"] {
        color: white !important;
    }

    /* Button styling */
    .stButton > button {
        background-color: #4B6FFF;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }

    .stButton > button:hover {
        background-color: #3955CC;
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #1E1E3F;
        color: white;
        border: 1px solid #3A3A4F;
    }

    /* Select box styling */
    .stSelectbox > div > div > div {
        background-color: #1E1E3F;
        color: white;
    }

    /* Plotly chart background */
    .js-plotly-plot .plotly .main-svg {
        background-color: transparent !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'expense_tracking'

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None

def login():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None

# Login Page
def show_login_page():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            .stApp {
                background-color: #1E1E2F;
            }
            
            .split-container {
                display: flex;
                min-height: 100vh;
                margin: -4rem -4rem -4rem -4rem;
            }
            
            .illustration-side {
                flex: 1;
                background-color: #1E1E3F;
                padding: 2rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            
            .login-side {
                flex: 1;
                background-color: #1E1E2F;
                padding: 4rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            .login-form {
                max-width: 400px;
                margin: 0 auto;
                width: 100%;
            }
            
            .form-label {
                color: white;
                font-size: 1rem;
                font-weight: 500;
                margin-bottom: 0.5rem;
                display: block;
            }
            
            .login-input {
                width: 100%;
                padding: 12px 16px;
                background-color: #2A2A3F;
                border: 1px solid #3A3A4F;
                border-radius: 8px;
                color: white;
                font-size: 1rem;
                margin-bottom: 1rem;
            }
            
            .login-input::placeholder {
                color: #666;
            }
            
            .remember-me {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 1rem 0;
            }
            
            .login-button {
                width: 100%;
                padding: 12px;
                background-color: #4B6FFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                margin-top: 1rem;
            }
            
            .login-button:hover {
                background-color: #3955CC;
            }
            
            @media (max-width: 768px) {
                .split-container {
                    flex-direction: column;
                }
                .illustration-side {
                    min-height: 300px;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="small")

    with col1:
        st.markdown("""
            <div class="illustration-side">
                <svg viewBox="0 0 600 400" style="width: 100%; max-width: 500px;">
                    <defs>
                        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#4B6FFF;stop-opacity:0.8" />
                            <stop offset="100%" style="stop-color:#4B6FFF;stop-opacity:0.2" />
                        </linearGradient>
                    </defs>
                    <path d="M100,200 L200,150 L300,250 L400,100 L500,200" 
                          stroke="url(#grad1)" 
                          stroke-width="4" 
                          fill="none"/>
                    <rect x="50" y="300" width="80" height="100" fill="#FFB347" opacity="0.8"/>
                    <rect x="150" y="250" width="80" height="150" fill="#4B6FFF" opacity="0.8"/>
                    <rect x="250" y="200" width="80" height="200" fill="#98FB98" opacity="0.8"/>
                    <rect x="350" y="150" width="80" height="250" fill="#FF6B6B" opacity="0.8"/>
                </svg>
                <h1 style="color: white; margin-top: 2rem; text-align: center;">WealthWise</h1>
                <p style="color: #B8B8D1; text-align: center;">Your Personal Finance Dashboard</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.form("login_form"):
            st.markdown("""
                <div class="login-side">
                    <div class="login-form">
                        <h2 style="color: white; margin-bottom: 2rem;">Welcome Back</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if verify_credentials(username, password):
                    st.session_state.logged_in = True
                    st.session_state.user_id = USERS[username]["user_id"]
                    st.session_state.user_name = USERS[username]["name"]
                    st.rerun()
                else:
                    st.error("Invalid username or password")

# Load and process data
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "personal_transactions.csv")
    
    # Read CSV with specific date parsing
    df = pd.read_csv(CSV_PATH)
    
    # Convert Date column to datetime with error handling
    try:
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    except ValueError:
        # If specific format fails, try with mixed format
        df["Date"] = pd.to_datetime(df["Date"], format='mixed', dayfirst=True)
    
    # Extract month and ensure Amount is properly handled
    df["Month"] = df["Date"].dt.to_period("M")
    df["Amount"] = df["Amount_INR"].abs()
    
    return df

def show_expense_tracking():
    st.title("Track Your Expenses")
    
    df = load_data()
    user_df = df[df['User_ID'] == st.session_state.user_id]
    
    # Calculate totals
    total_income = user_df[user_df['Transaction Type'] == 'credit']['Amount_INR'].sum()
    total_expenses = user_df[user_df['Transaction Type'] == 'debit']['Amount_INR'].sum()
    net_amount = total_income - total_expenses
    
    # Total metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Total Income</div>
                <div style="color: white; font-size: 1.8em; font-weight: 600; margin: 10px 0;">₹{total_income:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Total Expenses</div>
                <div style="color: white; font-size: 1.8em; font-weight: 600; margin: 10px 0;">₹{total_expenses:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Net Amount</div>
                <div style="color: white; font-size: 1.8em; font-weight: 600; margin: 10px 0;">₹{net_amount:,.2f}</div>
                <div style="color: {'#4CAF50' if net_amount >= 0 else '#FF4B4B'}; font-size: 0.9em;">
                    {'↑' if net_amount >= 0 else '↓'} ₹{abs(net_amount):,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Monthly Trends
    st.subheader("Monthly Trends")
    monthly_data = user_df.pivot_table(
        index='Month',
        columns='Transaction Type',
        values='Amount_INR',
        aggfunc='sum'
    ).fillna(0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_data.index.astype(str),
        y=monthly_data['credit'],
        name='Income',
        line=dict(color='#4B6FFF', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=monthly_data.index.astype(str),
        y=monthly_data['debit'],
        name='Expenses',
        line=dict(color='#FF4B4B', width=2)
    ))
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white'),
            title='Amount (₹)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Latest Transactions and Spent by Category in two columns
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.subheader("Latest Transactions")
        recent_transactions = user_df.sort_values('Date', ascending=False).head(5)
        
        for _, tx in recent_transactions.iterrows():
            st.markdown(f"""
                <div style="background-color: #1E1E3F; padding: 15px; border-radius: 8px; margin: 8px 0; border: 1px solid rgba(75, 111, 255, 0.1);">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <div style="font-weight: 500; color: white;">{tx['Category']}</div>
                            <div style="color: white; font-size: 0.9em;">{tx['Date'].strftime('%B %d, %Y')}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 500; color: white;">{tx['Account Name']}</div>
                            <div style="color: {'#4B6FFF' if tx['Transaction Type'] == 'credit' else '#FF4B4B'}; font-weight: 500;">
                                ₹{tx['Amount_INR']:,.2f}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Spent by Category")
        category_spending = user_df[user_df['Transaction Type'] == 'debit'].groupby('Category')['Amount_INR'].sum()
        category_spending = category_spending.sort_values(ascending=True)
        
        for category, amount in category_spending.items():
            color = '#4B6FFF'
            st.markdown(f"""
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="color: white;">{category}</span>
                        <span style="color: white;">₹{amount:,.0f}</span>
                    </div>
                    <div style="background-color: rgba(75, 111, 255, 0.1); height: 8px; border-radius: 4px; position: relative;">
                        <div style="position: absolute; left: 0; top: 0; height: 100%; width: {(amount/category_spending.max())*100}%; background-color: {color}; border-radius: 4px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Spending Clusters Analysis
    st.subheader("Spending Pattern Analysis")
    
    # Apply clustering to user's transactions
    clustered_df = apply_kmeans_clustering(user_df)
    
    # Calculate cluster statistics
    cluster_stats = clustered_df.groupby('Cluster_Label').agg({
        'Amount_INR': ['count', 'mean', 'sum']
    }).round(2)
    cluster_stats.columns = ['Number of Transactions', 'Average Amount', 'Total Amount']
    
    # Create two columns for visualization
    cluster_col1, cluster_col2 = st.columns([1, 1])
    
    with cluster_col1:
        # Cluster distribution
        cluster_counts = clustered_df['Cluster_Label'].value_counts()
        fig = go.Figure(data=[
            go.Bar(
                x=cluster_counts.index,
                y=cluster_counts.values,
                marker_color=['#4B6FFF', '#F2B84B', '#FF4B4B'],
                text=cluster_counts.values,
                textposition='auto',
            )
        ])
        fig.update_layout(
            title="Distribution of Spending Patterns",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='white'),
                title='Number of Transactions'
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with cluster_col2:
        # Cluster statistics
        st.markdown("""
            <div style="background-color: #1E1E3F; padding: 15px; border-radius: 8px; margin-top: 40px;">
                <div style="color: white; font-weight: 500; margin-bottom: 10px;">Cluster Statistics</div>
                <table style="width: 100%; color: white; font-size: 0.9em;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <th style="text-align: left; padding: 8px 0;">Cluster</th>
                        <th style="text-align: right;">Transactions</th>
                        <th style="text-align: right;">Avg Amount</th>
                    </tr>
        """, unsafe_allow_html=True)
        
        for cluster in ['Low Spend', 'Medium Spend', 'High Spend']:
            if cluster in cluster_stats.index:
                stats = cluster_stats.loc[cluster]
                st.markdown(f"""
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;">{cluster}</td>
                        <td style="text-align: right;">{int(stats['Number of Transactions'])}</td>
                        <td style="text-align: right;">₹{stats['Average Amount']:,.2f}</td>
                    </tr>
                """, unsafe_allow_html=True)
        
        st.markdown("</table></div>", unsafe_allow_html=True)

    # Scatter plot of transactions by cluster
    st.subheader("Transaction Distribution by Spending Pattern")
    
    fig = go.Figure()
    colors = {'Low Spend': '#4B6FFF', 'Medium Spend': '#F2B84B', 'High Spend': '#FF4B4B'}
    
    for cluster in clustered_df['Cluster_Label'].unique():
        cluster_data = clustered_df[clustered_df['Cluster_Label'] == cluster]
        fig.add_trace(go.Scatter(
            x=cluster_data['Date'],
            y=cluster_data['Amount_INR'],
            mode='markers',
            name=cluster,
            marker=dict(
                color=colors[cluster],
                size=8,
                opacity=0.7
            )
        ))
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title="Amount (₹)",
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white')
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        ),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def show_transaction_history():
    st.title("Transaction History")
    
    df = load_data()
    user_df = df[df['User_ID'] == st.session_state.user_id]
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        transaction_types = ["All"] + sorted(user_df['Transaction Type'].unique().tolist())
        selected_type = st.selectbox("Transaction Type", transaction_types)
    with col2:
        categories = ["All"] + sorted(user_df['Category'].unique().tolist())
        selected_category = st.selectbox("Category", categories)
    
    # Filter the transactions
    filtered_df = user_df.copy()
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df['Transaction Type'] == selected_type]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    # Recent transactions
    st.subheader("Recent Transactions")
    recent_transactions = filtered_df.sort_values('Date', ascending=False)
    
    for _, tx in recent_transactions.iterrows():
        st.markdown(f"""
            <div class="transaction-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: white;">{tx['Category']}</h4>
                        <p style="color: white;">{tx['Date'].strftime('%B %d, %Y')}</p>
                    </div>
                    <div style="text-align: right;">
                        <h4 style="color: {'#4B6FFF' if tx['Transaction Type'] == 'credit' else '#FF4B4B'}">${tx['Amount_INR']:,.2f}</h4>
                        <p style="color: white;">{tx['Transaction Type'].title()}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_income_expense():
    st.title("Income vs Expense")
    
    df = load_data()
    user_df = df[df['User_ID'] == st.session_state.user_id]
    
    # Summary metrics
    income_expense = user_df.groupby('Transaction Type')['Amount_INR'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Total Income</div>
                <div style="color: white; font-size: 1.8em; font-weight: 600;">₹{income_expense.get('credit', 0):,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Total Expenses</div>
                <div style="color: white; font-size: 1.8em; font-weight: 600;">₹{income_expense.get('debit', 0):,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        net_amount = income_expense.get('credit', 0) - income_expense.get('debit', 0)
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Net Amount</div>
                <div style="color: white; font-size: 1.8em; font-weight: 600;">₹{net_amount:,.2f}</div>
                <div style="color: {'#4CAF50' if net_amount >= 0 else '#FF4B4B'}; font-size: 0.9em;">
                    {'↑' if net_amount >= 0 else '↓'} ₹{abs(net_amount):,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Income vs Expense Overview
    st.subheader("Income vs Expense Overview")
    fig = go.Figure(data=[
        go.Pie(
            labels=income_expense.index,
            values=income_expense.values,
            hole=.3,
            marker_colors=['#4B6FFF', '#FF4B4B']
        )
    ])
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            font=dict(color='white')
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly comparison
    st.subheader("Monthly Comparison")
    monthly_data = user_df.pivot_table(
        index='Month',
        columns='Transaction Type',
        values='Amount_INR',
        aggfunc='sum'
    ).fillna(0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Income',
        x=monthly_data.index.astype(str),
        y=monthly_data['credit'],
        marker_color='#4B6FFF'
    ))
    fig.add_trace(go.Bar(
        name='Expenses',
        x=monthly_data.index.astype(str),
        y=monthly_data['debit'],
        marker_color='#FF4B4B'
    ))
    fig.update_layout(
        barmode='group',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def show_reports_analysis():
    st.title("Reports and Analysis")
    
    df = load_data()
    user_df = df[df['User_ID'] == st.session_state.user_id]
    
    # Category breakdown
    st.subheader("Spending by Category")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category_spending = user_df[user_df['Transaction Type'] == 'debit'].groupby('Category')['Amount_INR'].sum()
        
        # Use Set3 color palette from seaborn
        colors = sns.color_palette("Set3", n_colors=len(category_spending)).as_hex()
        
        fig = px.pie(
            values=category_spending.values,
            names=category_spending.index,
            hole=0.3,
            color_discrete_sequence=colors
        )
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            legend=dict(
                bgcolor='rgba(30, 30, 63, 0.8)',
                bordercolor='white',
                borderwidth=1,
                font=dict(color='white', size=10),
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.1
            ),
            margin=dict(t=30, b=30, l=30, r=150)  # Adjust margins to accommodate legend
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display category-wise spending as a table
        st.markdown("### Category Details")
        category_data = pd.DataFrame({
            'Category': category_spending.index,
            'Amount (₹)': category_spending.values,
            '% of Total': (category_spending.values / category_spending.sum() * 100).round(1)
        })
        category_data = category_data.sort_values('Amount (₹)', ascending=False)
        
        # Format the amounts with commas and add ₹ symbol
        category_data['Amount (₹)'] = category_data['Amount (₹)'].apply(lambda x: f'₹{x:,.2f}')
        category_data['% of Total'] = category_data['% of Total'].apply(lambda x: f'{x}%')
        
        st.dataframe(
            category_data,
            hide_index=True,
            use_container_width=True
        )
    
    # Spending Clusters
    st.subheader("Spending Clusters")
    clustered_df = apply_kmeans_clustering(user_df)
    
    # Bar chart showing distribution of clusters
    fig = go.Figure(data=[
        go.Bar(
            x=clustered_df['Cluster_Label'].value_counts().index,
            y=clustered_df['Cluster_Label'].value_counts().values,
            marker_color=['#4B6FFF', '#FF4B4B', '#4CAF50']
        )
    ])
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Spending Cluster",
        yaxis_title="Number of Transactions",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot showing individual transactions by cluster
    st.subheader("Transaction Distribution by Cluster")
    fig = go.Figure()
    
    # Add scatter points for each cluster
    for cluster_label in clustered_df['Cluster_Label'].unique():
        cluster_data = clustered_df[clustered_df['Cluster_Label'] == cluster_label]
        fig.add_trace(go.Scatter(
            x=cluster_data.index,
            y=cluster_data['Amount_INR'],
            mode='markers',
            name=cluster_label,
            marker=dict(
                size=8,
                opacity=0.7
            )
        ))
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Transaction Index",
        yaxis_title="Amount (₹)",
        legend=dict(
            title="Cluster",
            font=dict(color='white')
        ),
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Add cluster statistics
    st.subheader("Cluster Statistics")
    cluster_stats = clustered_df.groupby('Cluster_Label').agg({
        'Amount_INR': ['count', 'mean', 'sum']
    }).round(2)
    cluster_stats.columns = ['Number of Transactions', 'Average Amount', 'Total Amount']
    st.dataframe(cluster_stats, use_container_width=True)

def show_debt_management():
    st.title("Debt Management")
    # Add debt management content here

def show_saving_goals():
    st.title("Saving Goals")
    # Add saving goals content here

def show_bill_reminders():
    st.title("Bill Reminders")
    # Add bill reminders content here

def show_goal_tracking():
    st.title("Goal Tracking")
    # Add goal tracking content here

def show_profile():
    st.title("My Profile")
    
    df = load_data()
    user_df = df[df['User_ID'] == st.session_state.user_id]
    
    # Calculate important metrics
    total_income = user_df[user_df['Transaction Type'] == 'credit']['Amount_INR'].sum()
    total_expenses = user_df[user_df['Transaction Type'] == 'debit']['Amount_INR'].sum()
    net_balance = total_income - total_expenses
    
    # Calculate monthly averages
    monthly_income = user_df[user_df['Transaction Type'] == 'credit'].groupby('Month')['Amount_INR'].sum().mean()
    monthly_expenses = user_df[user_df['Transaction Type'] == 'debit'].groupby('Month')['Amount_INR'].sum().mean()
    
    # Get top spending categories
    top_categories = user_df[user_df['Transaction Type'] == 'debit'].groupby('Category')['Amount_INR'].sum().nlargest(3)
    
    # Get recent transactions
    recent_transactions = user_df.sort_values('Date', ascending=False).head(3)
    
    # Profile header with user info
    st.markdown(f"""
        <div style="background-color: rgba(0,0,0,0); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="background-color: #4B6FFF; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                    {st.session_state.user_name[0].upper()}
                </div>
                <div>
                    <h2 style="margin: 0;">{st.session_state.user_name}</h2>
                    <p style="margin: 0; color: #666;">User ID: {st.session_state.user_id}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Account Summary Section
    st.subheader("Account Summary")
    
    # Key Metrics in Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Net Balance</div>
                <div style="color: {'#4CAF50' if net_balance >= 0 else '#FF5252'}; font-size: 1.8em; font-weight: 600; margin: 10px 0;">₹{net_balance:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Monthly Income</div>
                <div style="color: #4CAF50; font-size: 1.8em; font-weight: 600; margin: 10px 0;">₹{monthly_income:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 20px; border-radius: 10px; border: 1px solid rgba(75, 111, 255, 0.1);">
                <div style="color: white; font-size: 0.9em;">Monthly Expenses</div>
                <div style="color: #FF5252; font-size: 1.8em; font-weight: 600; margin: 10px 0;">₹{monthly_expenses:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Top Spending Categories
    st.subheader("Top Spending Categories")
    fig = go.Figure(data=[
        go.Bar(
            x=top_categories.values,
            y=top_categories.index,
            orientation='h',
            marker_color='#4B6FFF'
        )
    ])
    fig.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Transactions
    st.subheader("Recent Transactions")
    for _, tx in recent_transactions.iterrows():
        amount_color = "#4CAF50" if tx['Transaction Type'] == 'credit' else "#FF5252"
        st.markdown(f"""
            <div style="background-color: #1E1E3F; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {amount_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: white;">{tx['Description']}</div>
                        <div style="color: white; font-size: 0.9em;">{tx['Category']} • {tx['Date'].strftime('%d %b %Y')}</div>
                    </div>
                    <div style="color: {amount_color}; font-weight: 600;">₹{tx['Amount_INR']:,.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_chatbot():
    st.title("Financial Assistant 🤖")
    
    # Initialize session state for chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize chatbot with user data
    df = load_data()
    user_df = df[df['User_ID'] == st.session_state.user_id]
    chatbot = FinancialChatbot(user_df)
    
    # Demo questions
    st.markdown("""
        <div style="background-color: rgba(75, 111, 255, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="color: #4B6FFF; margin-top: 0;">Sample Questions You Can Ask:</h4>
            <ul style="color: white;">
                <li>What's my total spending?</li>
                <li>How much did I spend on groceries?</li>
                <li>What's my total income?</li>
                <li>Can you give me financial advice?</li>
                <li>What's my monthly spending?</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Chat interface
    user_input = st.text_input("Ask me anything about your finances:", key="user_query")
    
    # Process the query when user hits enter
    if user_input and user_input not in [msg['user'] for msg in st.session_state.chat_history]:
        # Get response from chatbot
        response = chatbot.process_query(user_input)
        
        # Add to chat history
        st.session_state.chat_history.append({
            'user': user_input,
            'bot': response
        })
    
    # Display chat history
    for message in st.session_state.chat_history:
        # User message
        st.markdown(f"""
            <div style="margin-top: 20px;">
                <div style="background-color: #1E1E3F; color: white; padding: 10px 15px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; display: inline-block; max-width: 70%;">
                    {message['user']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Bot response
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="background-color: #4B6FFF; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; display: inline-block; float: right; max-width: 70%;">
                    {message['bot']}
                </div>
                <div style="clear: both;"></div>
            </div>
        """, unsafe_allow_html=True)
    
    # Add a clear chat button
    if st.session_state.chat_history:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# Main dashboard
def show_dashboard():
    # Sidebar navigation
    with st.sidebar:
        st.image("logo.jpeg", width=3000)
        
        nav_items = {
            "🏠 Expense Tracking": "expense_tracking",
            "📊 Reports and Analysis": "reports_analysis",
            "📝 Transaction History": "transaction_history",
            "💸 Income vs Expense": "income_expense",
            "🤖 Financial Assistant": "chatbot"
        }
        
        for label, page in nav_items.items():
            if st.sidebar.button(label, key=page, use_container_width=True):
                st.session_state.current_page = page
        
        st.markdown("---")
        st.markdown("### My Account")
        if st.sidebar.button("👤 Profile", key="profile", use_container_width=True):
            st.session_state.current_page = "profile"
        
        st.markdown("### System")
        if st.sidebar.button("🚪 Logout", key="logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Main content based on navigation
    if st.session_state.current_page == "expense_tracking":
        show_expense_tracking()
    elif st.session_state.current_page == "income_expense":
        show_income_expense()
    elif st.session_state.current_page == "transaction_history":
        show_transaction_history()
    elif st.session_state.current_page == "reports_analysis":
        show_reports_analysis()
    elif st.session_state.current_page == "chatbot":
        show_chatbot()
    elif st.session_state.current_page == "profile":
        show_profile()

# Main app logic
def main():
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main() 