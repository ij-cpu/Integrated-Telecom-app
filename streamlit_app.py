import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

from data.plans import telecom_plans
from bot.quiz_engine import get_quiz_question, evaluate_answer, get_score_summary
from agent.triage_agent import run_triage_agent

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Telecom Bot", layout="wide")

# -------------------------
# DATA
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
    margin: 40px 0;
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
.urgency-high {
    background-color: #ffe0e0;
    border-left: 5px solid #e53935;
    padding: 12px 16px;
    border-radius: 8px;
    color: #b71c1c;
    font-weight: 600;
}
.urgency-medium {
    background-color: #fff8e1;
    border-left: 5px solid #f9a825;
    padding: 12px 16px;
    border-radius: 8px;
    color: #e65100;
    font-weight: 600;
}
.urgency-low {
    background-color: #e8f5e9;
    border-left: 5px solid #43a047;
    padding: 12px 16px;
    border-radius: 8px;
    color: #1b5e20;
    font-weight: 600;
}
.entity-box {
    background-color: #f0f4ff;
    border-radius: 10px;
    padding: 14px;
    margin-top: 10px;
}
.quiz-question {
    background-color: #f3f0ff;
    border-left: 5px solid #7c3aed;
    padding: 16px;
    border-radius: 10px;
    font-size: 17px;
    font-weight: 500;
    color: #1e1e2f;
}
.score-card {
    background: linear-gradient(135deg, #e0f7fa, #f3e5f5);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HERO
# -------------------------
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📱 Telecom Bot</div>
    <div class="hero-subtitle">
        AI-powered assistant for plans, support triage, and telecom learning
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3 = st.tabs([
    "📋 Plans & Chatbot",
    "🎓 Quiz Tutor",
    "🚨 Triage Agent"
])

# =========================
# TAB 1: EXISTING FEATURES
# =========================
with tab1:

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

    st.subheader("💬 Ask Telecom Bot")
    user_query = st.text_input("Ask anything about telecom plans...")
    if user_query:
        try:
            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "gemma3:1b",
                    "prompt": f"Here are telecom plans:\n{filtered_df.to_string()}\n\nUser question: {user_query}",
                    "stream": False
                },
                timeout=60
            )
            st.success(response.json()["response"])
        except:
            st.error("⚠️ Ollama is not connected.")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("📋 Available Plans")
    st.dataframe(filtered_df, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

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


# =========================
# TAB 2: QUIZ TUTOR
# =========================
with tab2:

    st.subheader("🎓 Telecom Quiz Tutor")
    st.caption("Test your knowledge of telecom plans. Get instant AI feedback and explanations.")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Quiz settings
    col1, col2 = st.columns(2)
    with col1:
        quiz_provider = st.selectbox(
            "Focus on provider",
            ["All", "Jio", "Airtel", "Vi"],
            key="quiz_provider"
        )
    with col2:
        total_questions = st.selectbox(
            "Number of questions",
            [3, 5, 10],
            key="quiz_total"
        )

    # Session state init
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_count" not in st.session_state:
        st.session_state.quiz_count = 0
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "quiz_done" not in st.session_state:
        st.session_state.quiz_done = False
    if "answer_submitted" not in st.session_state:
        st.session_state.answer_submitted = False

    # Start quiz
    if not st.session_state.quiz_active and not st.session_state.quiz_done:
        if st.button("▶️ Start Quiz", use_container_width=True):
            st.session_state.quiz_active = True
            st.session_state.quiz_score = 0
            st.session_state.quiz_count = 0
            st.session_state.feedback = None
            st.session_state.answer_submitted = False
            st.session_state.current_question = get_quiz_question(quiz_provider)
            st.rerun()

    # Active quiz
    if st.session_state.quiz_active and not st.session_state.quiz_done:

        q = st.session_state.current_question
        progress = st.session_state.quiz_count / total_questions
        st.progress(progress, text=f"Question {st.session_state.quiz_count + 1} of {total_questions}")

        st.markdown(f'<div class="quiz-question">❓ {q["question"]}</div>', unsafe_allow_html=True)
        st.markdown("")

        user_answer = st.text_input(
            "Your answer:",
            key=f"answer_{st.session_state.quiz_count}",
            placeholder="Type your answer here..."
        )

        if not st.session_state.answer_submitted:
            if st.button("✅ Submit Answer", use_container_width=True):
                if user_answer.strip():
                    with st.spinner("Evaluating your answer..."):
                        is_correct, feedback = evaluate_answer(
                            q["question"],
                            q["answer"],
                            user_answer,
                            q["plan"]
                        )
                    if is_correct:
                        st.session_state.quiz_score += 1
                    st.session_state.feedback = (is_correct, feedback)
                    st.session_state.answer_submitted = True
                    st.rerun()
                else:
                    st.warning("Please type an answer before submitting.")

        # Show feedback
        if st.session_state.answer_submitted and st.session_state.feedback:
            is_correct, feedback = st.session_state.feedback
            if is_correct:
                st.success(f"✅ Correct! {feedback}")
            else:
                st.error(f"❌ Incorrect. {feedback}")

            if st.session_state.quiz_count + 1 >= total_questions:
                next_label = "🏁 See Results"
            else:
                next_label = "➡️ Next Question"

            if st.button(next_label, use_container_width=True):
                st.session_state.quiz_count += 1
                if st.session_state.quiz_count >= total_questions:
                    st.session_state.quiz_done = True
                    st.session_state.quiz_active = False
                else:
                    st.session_state.current_question = get_quiz_question(quiz_provider)
                    st.session_state.feedback = None
                    st.session_state.answer_submitted = False
                st.rerun()

    # Results screen
    if st.session_state.quiz_done:
        level, msg, percentage = get_score_summary(
            st.session_state.quiz_score,
            total_questions
        )
        st.markdown(f"""
        <div class="score-card">
            <h2>{level}</h2>
            <h3>Score: {st.session_state.quiz_score} / {total_questions} ({percentage}%)</h3>
            <p>{msg}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        if st.button("🔄 Restart Quiz", use_container_width=True):
            st.session_state.quiz_active = False
            st.session_state.quiz_done = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_count = 0
            st.session_state.current_question = None
            st.session_state.feedback = None
            st.session_state.answer_submitted = False
            st.rerun()


# =========================
# TAB 3: TRIAGE AGENT
# =========================
with tab3:

    st.subheader("🚨 Telecom Support Triage Agent")
    st.caption("Paste any customer complaint or query. The agent will classify urgency, extract key details, and draft a response.")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Example messages
    st.markdown("**💡 Try an example:**")
    ex_col1, ex_col2, ex_col3 = st.columns(3)

    with ex_col1:
        if st.button("📵 Network outage", use_container_width=True):
            st.session_state.triage_input = "My Airtel SIM has had no network since yesterday. My number is 9876543210. This is urgent, I'm losing business!"

    with ex_col2:
        if st.button("💸 Wrong charge", use_container_width=True):
            st.session_state.triage_input = "I was charged ₹499 on 12/01/2025 but I only subscribed to the ₹299 Jio plan. Please refund immediately."

    with ex_col3:
        if st.button("📋 Plan inquiry", use_container_width=True):
            st.session_state.triage_input = "Can you tell me which Jio plan gives the most data for under ₹300?"

    if "triage_input" not in st.session_state:
        st.session_state.triage_input = ""

    customer_message = st.text_area(
        "Customer message:",
        value=st.session_state.triage_input,
        height=120,
        placeholder="Paste or type a customer support message here...",
        key="triage_text"
    )

    if st.button("🔍 Run Triage Agent", use_container_width=True):
        if customer_message.strip():
            with st.spinner("Agent is analyzing the message..."):
                result = run_triage_agent(customer_message)

            classification = result["classification"]
            entities = result["entities"]
            draft = result["draft_response"]

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            # Urgency badge
            urgency = classification.get("urgency", "LOW")
            intent = classification.get("intent", "QUERY")
            summary = classification.get("summary", "")

            urgency_class = {
                "HIGH": "urgency-high",
                "MEDIUM": "urgency-medium",
                "LOW": "urgency-low"
            }.get(urgency, "urgency-low")

            urgency_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(urgency, "🟢")
            intent_icon = {"COMPLAINT": "😠", "QUERY": "❓", "REQUEST": "📝", "FEEDBACK": "💬"}.get(intent, "❓")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="{urgency_class}">{urgency_icon} Urgency: {urgency}</div>', unsafe_allow_html=True)
            with col2:
                st.info(f"{intent_icon} Intent: **{intent}**")

            st.markdown(f"**📌 Summary:** {summary}")

            # Entities
            st.markdown("#### 🔍 Extracted Entities (NER)")
            has_entities = any([
                entities["phone_numbers"],
                entities["amounts"],
                entities["dates"],
                entities["plan_ids"],
                entities["providers"]
            ])

            if has_entities:
                ecol1, ecol2, ecol3 = st.columns(3)
                with ecol1:
                    if entities["phone_numbers"]:
                        st.metric("📱 Phone", entities["phone_numbers"][0])
                    if entities["providers"]:
                        st.metric("📡 Provider", ", ".join(entities["providers"]))
                with ecol2:
                    if entities["amounts"]:
                        st.metric("💰 Amount", entities["amounts"][0])
                with ecol3:
                    if entities["dates"]:
                        st.metric("📅 Date", entities["dates"][0])
                    if entities["plan_ids"]:
                        st.metric("🎫 Plan/Ticket ID", entities["plan_ids"][0])
            else:
                st.info("No specific entities (phone numbers, amounts, dates) detected.")

            # Draft response
            st.markdown("#### ✉️ AI-Generated Draft Response")
            st.markdown(
                f'<div style="background:#f0fff4;border-left:5px solid #38a169;padding:16px;border-radius:10px;font-size:15px;line-height:1.7">{draft}</div>',
                unsafe_allow_html=True
            )

            st.download_button(
                label="⬇️ Download Draft Response",
                data=f"Customer Message:\n{customer_message}\n\nUrgency: {urgency}\nIntent: {intent}\nSummary: {summary}\n\nDraft Response:\n{draft}",
                file_name="triage_response.txt",
                mime="text/plain"
            )
        else:
            st.warning("Please enter a customer message first.")