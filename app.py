import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import random

# --- 1. PAGE CONFIG ---
# Force sidebar to start expanded
st.set_page_config(
    page_title="Smart Budget Coach", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. ULTIMATE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', sans-serif;
        background-color: #0e1117;
        color: #ffffff;
    }

    /* --- SIDEBAR LOCK: REMOVE COLLAPSE BUTTON --- */
    [data-testid="sidebar-button"], [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* --- LOGIN UI: NO SCROLL & ABSOLUTE TOP --- */
    [data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 0px !important; padding-bottom: 0px !important; }
    
    /* Disable scrolling only on the login screen */
    .login-lock { 
        overflow: hidden !important; 
        height: 100vh !important; 
        position: fixed;
        width: 100%;
    }

    .top-pinned-login {
        position: fixed;
        top: 0px; 
        left: 0; 
        width: 100%;
        display: flex; 
        flex-direction: column; 
        align-items: center;
        z-index: 9999;
        padding-top: 30px; /* Space from very top */
    }

    .main-title { 
        font-size: 3.8rem; font-weight: 800; 
        background: linear-gradient(90deg, #3B82F6, #10B981); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        margin: 0; line-height: 1;
    }
    .sub-title { font-size: 0.9rem; color: #9CA3AF; letter-spacing: 5px; text-transform: uppercase; margin-top: 5px; margin-bottom: 15px; }

    /* BACKGROUND LOGOS */
    .bg-icon {
        position: fixed; font-size: 5rem; opacity: 0.3; z-index: 0;
        user-select: none; pointer-events: none;
        animation: floatMotion 20s infinite linear;
    }
    @keyframes floatMotion {
        0% { transform: translateY(110vh) rotate(0deg); }
        100% { transform: translateY(-20vh) rotate(360deg); }
    }

    /* --- DASHBOARD: PREMIUM CARDS --- */
    .m-card { padding: 25px; border-radius: 20px; color: white; margin-bottom: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); }
    .c-green { background: #10B981; }  
    .c-blue { background: #2563EB; }   
    .c-red { background: #EF4444; }    
    .c-purple { background: #8B5CF6; } 
    .m-label { font-size: 0.9rem; opacity: 0.9; }
    .m-value { font-size: 2.2rem; font-weight: 700; margin: 5px 0; }
    .m-trend { font-size: 0.8rem; opacity: 0.8; }

    .report-box { 
        background: #1f2937; padding: 25px; border-radius: 15px; 
        border-left: 5px solid #8B5CF6; margin-top: 20px; 
    }

    /* Input Box Styles */
    div[data-baseweb="input"] { background-color: #1f2937 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE BACKEND ---
DB_NAME = 'budget_smart_pro.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tx 
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, category TEXT, type TEXT, amount REAL, note TEXT)''')
    conn.commit()
    conn.close()

def add_tx(user, date, cat, ttype, amt, note):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tx (username, date, category, type, amount, note) VALUES (?,?,?,?,?,?)", 
              (user, date, cat, ttype, amt, note))
    conn.commit()
    conn.close()

def get_user_df(user):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM tx WHERE username = ?", conn, params=(user,))
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

init_db()

# --- 4. LOGIN SCREEN (TOP PINNED & NO SCROLL) ---
if 'username' not in st.session_state:
    st.markdown('<div class="login-lock">', unsafe_allow_html=True)
    icons = ["💰", "💹", "🏠", "✈️", "🎁", "💡", "🍔", "🚗"] * 2
    for emoji in icons:
        st.markdown(f'<div class="bg-icon" style="left: {random.randint(0, 95)}%; animation-duration: {random.randint(12, 20)}s;">{emoji}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="top-pinned-login">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Smart Budget Coach</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Your Budget Assistant</p>', unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        u_name = st.text_input("", placeholder="Type your name...", key="login_name", label_visibility="collapsed")
        if st.button("ENTER DASHBOARD →", use_container_width=True):
            if u_name.strip():
                st.session_state.username = u_name.strip()
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- 5. DASHBOARD PAGE (RESTORE SCROLLING) ---
st.markdown("<style>html, body { overflow: auto !important; height: auto !important; }</style>", unsafe_allow_html=True)

current_user = st.session_state.username
df = get_user_df(current_user)

# --- SIDEBAR: Watermark & Always Open ---
with st.sidebar:
    st.title(f"👤 {current_user}")
    if st.button("Logout"):
        del st.session_state.username
        st.rerun()
    
    st.divider()
    st.subheader("Add Transaction")
    with st.form("entry_form", clear_on_submit=True):
        t_date = st.date_input("Date", datetime.now())
        t_type = st.selectbox("Type", ["Income", "Expense"])
        t_cat = st.selectbox("Category", ["Salary", "Food", "Shopping", "Transport", "Bills", "Health", "Other"])
        t_amt = st.number_input("Amount (₹)", min_value=0.0, value=None, placeholder="0.00")
        t_note = st.text_input("Note", placeholder="Transaction details...")
        if st.form_submit_button("Save Transaction", use_container_width=True):
            if t_amt and t_amt > 0:
                add_tx(current_user, t_date.strftime("%Y-%m-%d"), t_cat, t_type, t_amt, t_note)
                st.rerun()

# --- DASHBOARD CONTENT ---
st.markdown(f"## Welcome back, {current_user}! 👋")
st.markdown("<p style='color:#9CA3AF;'>Let's analyze your financial health today.</p>", unsafe_allow_html=True)

if df.empty:
    st.info("Log your daily transactions in the sidebar to build your dashboard.")
else:
    inc_tot = df[df['type'] == 'Income']['amount'].sum()
    exp_tot = df[df['type'] == 'Expense']['amount'].sum()
    bal_tot = inc_tot - exp_tot
    sav_tot = bal_tot if bal_tot > 0 else 0

    # COLOR CARDS
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="m-card c-green"><div class="m-label">Total Balance</div><div class="m-value">₹{bal_tot:,.0f}</div><div class="m-trend">↑ 12% vs last month</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="m-card c-blue"><div class="m-label">Monthly Income</div><div class="m-value">₹{inc_tot:,.0f}</div><div class="m-trend">↑ 8.2% vs last month</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="m-card c-red"><div class="m-label">Monthly Expenses</div><div class="m-value">₹{exp_tot:,.0f}</div><div class="m-trend">↓ 3.1% vs last month</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="m-card c-purple"><div class="m-label">Savings This Month</div><div class="m-value">₹{sav_tot:,.0f}</div><div class="m-trend">↑ 18.7% vs last month</div></div>', unsafe_allow_html=True)

    # VISUALS
    c_left, c_right = st.columns([1.5, 1])
    with c_left:
        st.subheader("Expense Overview")
        exp_only = df[df['type'] == 'Expense']
        if not exp_only.empty:
            exp_grouped = exp_only.groupby(['date', 'category'])['amount'].sum().reset_index()
            
            # --- THE FIX: Changed to a Bar Chart to handle single-day entries cleanly ---
            fig = px.bar(exp_grouped, x='date', y='amount', color='category', template="plotly_dark")
            
            # Formatting the x-axis to prevent zooming into milliseconds
            fig.update_xaxes(tickformat="%b %d, %Y", dtick="D1")
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                height=350,
                margin=dict(l=0, r=0, t=20, b=0) # Tighter margins
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with c_right:
        st.subheader("Monthly Summary")
        if not exp_only.empty:
            pie_data = exp_only.groupby('category')['amount'].sum().reset_index()
            fig_pie = go.Figure(data=[go.Pie(labels=pie_data['category'], values=pie_data['amount'], hole=.7)])
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=350, margin=dict(t=20, b=20))
            fig_pie.add_annotation(text=f"₹{exp_tot:,.0f}<br><span style='font-size:12px'>Total Spent</span>", showarrow=False, font=dict(size=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    # MONTHLY REPORT BLOCK
    st.divider()
    st.subheader("📊 Smart Coach Report")
    save_rate = (sav_tot / inc_tot * 100) if inc_tot > 0 else 0
    st.markdown(f"""
    <div class="report-box">
        <h4 style='margin:0; color:#8B5CF6;'>Financial Health Insight</h4>
        <p style='margin:10px 0;'>Your current savings rate is <b>{save_rate:.1f}%</b>. 
        Aim for 20% to reach your long-term goals. Focus on optimizing 'Other' category expenses next month.</p>
        <div style='display:flex; gap:20px; font-size:0.9rem; opacity:0.8;'>
            <span>🎯 Savings Target: ₹{inc_tot*0.2:,.0f}</span>
            <span>✅ Status: {'On Track' if save_rate >= 20 else 'Review Expenses'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # RECENT TRANSACTIONS
    st.write("")
    st.subheader("📝 Transaction History")
    st.dataframe(
        df.sort_values(by='date', ascending=False), 
        use_container_width=True, 
        column_config={
            "id": None, "username": None,
            "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
            "date": st.column_config.DateColumn("Date")
        }
    )