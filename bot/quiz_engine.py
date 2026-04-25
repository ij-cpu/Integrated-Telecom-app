import random
import requests
import json
from data.plans import telecom_plans

def get_quiz_question(provider_filter=None):
    plans = telecom_plans
    if provider_filter and provider_filter != "All":
        plans = [p for p in plans if p["provider"] == provider_filter]
    if not plans:
        plans = telecom_plans

    plan = random.choice(plans)

    question_templates = [
        {
            "question": f"What is the daily data limit for {plan['provider']}'s ₹{plan['price']} plan?",
            "answer": plan["data"],
            "plan": plan
        },
        {
            "question": f"How long is the validity of {plan['provider']}'s ₹{plan['price']} plan?",
            "answer": plan["validity"],
            "plan": plan
        },
        {
            "question": f"What extras/OTT benefits does {plan['provider']}'s ₹{plan['price']} plan offer?",
            "answer": plan["extras"],
            "plan": plan
        },
        {
            "question": f"What type of calls does {plan['provider']}'s ₹{plan['price']} plan provide?",
            "answer": plan["calls"],
            "plan": plan
        }
    ]

    return random.choice(question_templates)


def evaluate_answer(question, correct_answer, user_answer, plan):
    prompt = f"""
You are a telecom quiz evaluator and tutor.

Question asked: {question}
Correct answer: {correct_answer}
User's answer: {user_answer}

Plan details for context:
- Provider: {plan['provider']}
- Price: ₹{plan['price']}
- Validity: {plan['validity']}
- Data: {plan['data']}
- Calls: {plan['calls']}
- Extras: {plan['extras']}

Task:
1. Determine if the user's answer is correct or partially correct (be lenient with wording).
2. If correct: congratulate briefly and reinforce WHY this feature matters for users.
3. If wrong: clearly explain the correct answer and provide a helpful explanation of what this plan feature means in real-world usage.
4. Keep response under 80 words. Be friendly and educational.

Respond in this exact JSON format:
{{"is_correct": true or false, "feedback": "your feedback here"}}
"""

    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        raw = response.json()["response"].strip()

        # Strip markdown code fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()

        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != 0:
            parsed = json.loads(raw[start:end])
            return parsed.get("is_correct", False), parsed.get("feedback", raw)
        else:
            return False, raw

    except Exception as e:
        return False, f"⚠️ Could not evaluate answer. Error: {str(e)}"


def get_score_summary(score, total):
    percentage = (score / total * 100) if total > 0 else 0
    if percentage == 100:
        level = "🏆 Expert"
        msg = "Perfect score! You know telecom plans inside out."
    elif percentage >= 70:
        level = "⭐ Proficient"
        msg = "Great job! A few gaps to close."
    elif percentage >= 40:
        level = "📚 Learning"
        msg = "Good effort. Review the plan details and try again."
    else:
        level = "🔰 Beginner"
        msg = "Keep practicing! Read through the plan details carefully."
    return level, msg, round(percentage)