import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Telecom Bot", layout="wide")

# -------------------------
# SAMPLE DATA
# -------------------------
data = {
    "Provider": ["Jio", "Airtel", "Vi", "BSNL", "Jio", "Airtel"],
    "Price (₹)": [299, 349, 249, 199, 399, 499],
    "Validity (days)": [28, 28, 24, 30, 56, 84],
    "Data (GB/day)": [1.5, 2, 1, 1, 2.5, 3],
    "Calls": ["Unlimited"] * 6
}

df = pd.DataFrame(data)

# -------------------------
# GLOBAL CSS
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
    padding: 50px;
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
        AI-powered assistant for telecom plan comparison & smart recommendations
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =========================
# FILTER SECTION
# =========================
st.subheader("🔎 Filters")

col1, col2 = st.columns(2)

with col1:
    max_budget = st.slider("Max Budget (₹)", 100, 1000, 500)

with col2:
    provider_filter = st.selectbox(
        "Select Provider",
        ["All"] + list(df["Provider"].unique())
    )

filtered_df = df[df["Price (₹)"] <= max_budget]

if provider_filter != "All":
    filtered_df = filtered_df[filtered_df["Provider"] == provider_filter]

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =========================
# ASK BOT SECTION (OLLAMA)
# =========================
st.subheader("💬 Ask Telecom Bot")

user_query = st.text_input("Ask anything about telecom plans...")

if user_query:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": f"User has these plans available:\n{filtered_df.to_string()}\n\nQuestion: {user_query}",
                "stream": False
            },
            timeout=60
        )

        result = response.json()["response"]
        st.success(result)

    except:
        st.error("⚠️ Ollama is not running. Please start Ollama using: ollama serve")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =========================
# AVAILABLE PLANS
# =========================
st.subheader("📋 Available Plans")

st.dataframe(filtered_df, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =========================
# PRICE VS DATA GRAPH
# =========================
st.subheader("📊 Price vs Data")

if not filtered_df.empty:
    fig, ax = plt.subplots()
    ax.scatter(filtered_df["Price (₹)"], filtered_df["Data (GB/day)"])
    ax.set_xlabel("Price (₹)")
    ax.set_ylabel("Data (GB/day)")
    ax.set_title("Price vs Data Relationship")
    st.pyplot(fig)
else:
    st.warning("No plans match selected filters.")