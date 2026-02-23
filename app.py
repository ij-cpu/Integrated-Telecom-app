import streamlit as st

st.set_page_config(page_title="Telecom Bot", layout="wide")

# -----------------------
# GLOBAL CSS
# -----------------------
st.markdown("""
<style>
.divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #d6dbe6, transparent);
    margin: 50px 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# HERO SECTION
# -----------------------
st.markdown("""
<div style="
    background: linear-gradient(to right, #dfe9f3, #cfd9df);
    padding: 40px;
    border-radius: 16px;
    text-align: center;
">
    <h1 style="color:#2c3e75;">📱 Telecom Bot</h1>
    <p style="color:#4a5568;">
        Your AI-powered assistant for telecom plans, pricing, benefits & smart recommendations
    </p>
</div>
""", unsafe_allow_html=True)

# 🔥 Divider After Hero
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# -----------------------
# ASK TELECOM BOT SECTION
# -----------------------
st.subheader("💬 Ask Telecom Bot")

user_query = st.text_input("Ask anything about telecom plans...")

if user_query:
    st.write("AI Response will appear here...")

# 🔥 Divider
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# -----------------------
# AVAILABLE PLANS SECTION
# -----------------------
st.subheader("📋 Available Plans")

st.write("Table of plans goes here...")

# 🔥 Divider
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# -----------------------
# PRICE VS DATA SECTION
# -----------------------
st.subheader("📊 Price vs Data")

st.write("Chart will appear here...")