import streamlit as st

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Telecom Bot",
    layout="wide"
)

# -------------------------
# GLOBAL CSS (Minimal Divider)
# -------------------------
st.markdown("""
<style>
.section-divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #d6dbe6, transparent);
    margin: 60px 0;
}

.hero-section {
    background: linear-gradient(to right, #e3f2fd, #f8fbff);
    padding: 40px;
    border-radius: 18px;
    text-align: center;
}

.hero-title {
    color: #1f3c88;
    font-size: 42px;
    font-weight: 700;
}

.hero-subtitle {
    color: #4a5568;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HERO SECTION
# =========================
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📱 Telecom Bot</div>
    <div class="hero-subtitle">
        Your AI-powered assistant for telecom plans, pricing, benefits & smart recommendations
    </div>
</div>
""", unsafe_allow_html=True)

# 🔥 Divider AFTER HERO
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# =========================
# ASK TELECOM BOT SECTION
# =========================
st.subheader("💬 Ask Telecom Bot")

user_query = st.text_input("Ask anything about telecom plans...")

if user_query:
    st.write("AI Response will appear here...")

# 🔥 Divider AFTER ASK BOT
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# =========================
# AVAILABLE PLANS SECTION
# =========================
st.subheader("📋 Available Plans")

# Replace with your real dataframe
st.write("Plans table goes here...")

# 🔥 Divider AFTER AVAILABLE PLANS
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# =========================
# CHARTS SECTION
# =========================
st.subheader("📊 Price vs Data")

# Replace with your real chart
st.write("Chart will appear here...")