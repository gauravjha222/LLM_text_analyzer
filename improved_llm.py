import os
import re
import json
import math
import requests
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from google import genai

# CONFIG

load_dotenv()

QUERY = "rent in koramangala"
MODELS = ["ChatGPT", "Gemini", "Llama"]

# LLM CALLS

def get_response(model, prompt):
    try:
        if model == "ChatGPT":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return res.choices[0].message.content

        if model == "Gemini":
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            return client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            ).text

        if model == "Llama":
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500
                },
                timeout=20
            )
            return response.json()["choices"][0]["message"]["content"]

    except Exception:
        return None


# ANALYSIS

def extract_details(text):
    text = text.lower()
    details = {}

    # BHK types
    bhk_matches = re.findall(r'\b[1-4]\s*bhk\b|\bstudio\b', text)
    details["bhk"] = list(set(b.replace(" ", "") for b in bhk_matches))

    # Blocks
    details["blocks"] = list(set(
        re.findall(r'(\d)(?:st|nd|rd|th)?\s*block', text)
    ))

    # Amenities
    amenities_list = ["gym", "parking", "lift", "security", "power backup"]
    details["amenities"] = [a for a in amenities_list if a in text]

    # Prices (₹10,000+ only)
    prices = []
    for value, unit in re.findall(r'₹?\s*(\d+(?:[,\.]\d+)?)\s*(k|thousand)?', text):
        amount = float(value.replace(",", ""))
        if unit:
            amount *= 1000
        if 10000 <= amount <= 300000:
            prices.append(int(amount))

    details["prices"] = sorted(set(prices))
    return details


# IMPROVED RESPONSE (PER MODEL)

def build_improved_response(analysis):
    parts = []

    if analysis["bhk"]:
        parts.append(
            "Available configurations include " +
            ", ".join(analysis["bhk"]) + " apartments."
        )

    if analysis["prices"]:
        parts.append(
            f"Monthly rents typically range from "
            f"₹{min(analysis['prices'])} to ₹{max(analysis['prices'])}."
        )

    if analysis["blocks"]:
        parts.append(
            "Popular rental blocks include Block " +
            ", ".join(analysis["blocks"]) + "."
        )

    if analysis["amenities"]:
        parts.append(
            "Common amenities offered are " +
            ", ".join(analysis["amenities"]) + "."
        )

    return " ".join(parts)


# FINAL CONSENSUS RESPONSE (MOST IMPORTANT)

def build_final_response(common):
    lines = []

    if common["bhk"]:
        lines.append(
            "Most rental listings in Koramangala commonly offer " +
            ", ".join(common["bhk"]) + " apartments."
        )

    if common["prices"]:
        lines.append(
            f"Across multiple models, monthly rents consistently fall between "
            f"₹{min(common['prices'])} and ₹{max(common['prices'])}."
        )

    return " ".join(lines)


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():
    collected = []

    for model in MODELS:
        response = get_response(model, QUERY)
        if not response:
            continue

        analysis = extract_details(response)

        collected.append({
            "model": model,
            "raw_response": response,
            "analysis": analysis,
            "improved_response": build_improved_response(analysis)
        })

# Find common patterns (present in at least half the models)
    common = {}
    for key in ["bhk", "blocks", "amenities", "prices"]:
        values = []
        for item in collected:
            values.extend(item["analysis"][key])

        freq = Counter(values)
        common[key] = [
            k for k, v in freq.items()
            if v >= math.ceil(len(collected) / 2)
        ]

    output = {
        "query": QUERY,
        "models_used": [c["model"] for c in collected],
        "responses": collected,
        "common_patterns": common,
        "final_response": build_final_response(common),
        "generated_at": datetime.now().isoformat()
    }

    with open("llm_analysis_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("LLM analysis completed successfully.")


if __name__ == "__main__":
    main()
