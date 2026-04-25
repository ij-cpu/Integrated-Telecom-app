import requests
import json
import re
from data.plans import telecom_plans

# -------------------------
# STEP 1: CLASSIFY MESSAGE
# -------------------------
def classify_message(text):
    prompt = f"""
You are a telecom support triage system.

Analyze this customer message: "{text}"

Classify it into exactly one urgency level and one intent category.

Urgency levels:
- HIGH: service outage, no network, SIM blocked, emergency
- MEDIUM: billing issues, wrong charges, plan not activated
- LOW: general inquiry, plan comparison, feature question

Intent categories:
- COMPLAINT: customer is unhappy or reporting a problem
- QUERY: customer is asking for information
- REQUEST: customer wants an action done (upgrade, change plan, refund)
- FEEDBACK: customer sharing opinion or suggestion

Respond ONLY in this exact JSON format, no extra text:
{{"urgency": "HIGH/MEDIUM/LOW", "intent": "COMPLAINT/QUERY/REQUEST/FEEDBACK", "summary": "one sentence summary of the issue"}}
"""
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "gemma3:1b", "prompt": prompt, "stream": False},
            timeout=60
        )
        raw = response.json()["response"].strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != 0:
            return json.loads(raw[start:end])
        return {"urgency": "LOW", "intent": "QUERY", "summary": raw}
    except Exception as e:
        return {"urgency": "UNKNOWN", "intent": "UNKNOWN", "summary": str(e)}


# -------------------------
# STEP 2: EXTRACT ENTITIES (NER)
# -------------------------
def extract_entities(text):
    entities = {
        "phone_numbers": re.findall(r'\b[6-9]\d{9}\b', text),
        "amounts": re.findall(r'₹\s?\d+|\d+\s?rupees?', text, re.IGNORECASE),
        "dates": re.findall(
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s?\d{1,2},?\s?\d{0,4})\b',
            text, re.IGNORECASE
        ),
        "plan_ids": re.findall(r'\b(plan\s?#?\d+|order\s?#?\d+|ticket\s?#?\d+)\b', text, re.IGNORECASE),
        "providers": [
            p for p in ["Jio", "Airtel", "Vi", "BSNL"]
            if p.lower() in text.lower()
        ]
    }
    return entities


# -------------------------
# STEP 3: GENERATE DRAFT RESPONSE
# -------------------------
def generate_draft_response(text, classification, entities):
    urgency = classification.get("urgency", "LOW")
    intent = classification.get("intent", "QUERY")
    summary = classification.get("summary", "")

    plan_context = "\n".join([
        f"- {p['provider']} ₹{p['price']}: {p['data']}, {p['validity']}, Extras: {p['extras']}"
        for p in telecom_plans
    ])

    entity_str = ""
    if entities["phone_numbers"]:
        entity_str += f"Phone number mentioned: {', '.join(entities['phone_numbers'])}. "
    if entities["amounts"]:
        entity_str += f"Amount mentioned: {', '.join(entities['amounts'])}. "
    if entities["providers"]:
        entity_str += f"Provider mentioned: {', '.join(entities['providers'])}. "
    if entities["dates"]:
        entity_str += f"Date mentioned: {', '.join(entities['dates'])}. "

    prompt = f"""
You are a professional telecom customer support agent.

Customer message: "{text}"
Issue summary: {summary}
Urgency: {urgency}
Intent: {intent}
Extracted details: {entity_str if entity_str else "None found"}

Available telecom plans for reference:
{plan_context}

Write a professional, empathetic draft response to the customer.
- If HIGH urgency: acknowledge urgency immediately, promise fast resolution
- If MEDIUM: apologize and provide clear next steps
- If LOW: be helpful and informative
- If it's a QUERY about plans: reference relevant plan details
- Keep response between 60-100 words
- Do NOT use placeholders like [Name] or [Date] — write naturally
- Sign off as: "Telecom Support Team"
"""
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "gemma3:1b", "prompt": prompt, "stream": False},
            timeout=90
        )
        return response.json()["response"].strip()
    except Exception as e:
        return f"⚠️ Could not generate response. Error: {str(e)}"


# -------------------------
# MAIN AGENT RUNNER
# -------------------------
def run_triage_agent(customer_message):
    classification = classify_message(customer_message)
    entities = extract_entities(customer_message)
    draft_response = generate_draft_response(customer_message, classification, entities)

    return {
        "classification": classification,
        "entities": entities,
        "draft_response": draft_response
    }