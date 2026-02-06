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
                max_tokens=400
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
                    "max_tokens": 400
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
    bhk_matches = re.findall(r'\b[1-3]\s*bhk\b|\bstudio\b', text)
    details["bhk"] = list(set(b.replace(" ", "") for b in bhk_matches))

    # Blocks
    details["blocks"] = list(set(
        re.findall(r'(\d)(?:st|nd|rd|th)?\s*block', text)
    ))

    # Amenities
    amenities_list = ["gym", "parking", "lift", "security", "power backup"]
    details["amenities"] = [a for a in amenities_list if a in text]

    # Prices (₹10k+ only)
    prices = []
    for value, unit in re.findall(r'₹?\s*(\d+(?:[,\.]\d+)?)\s*(k|thousand)?', text):
        amount = float(value.replace(",", ""))
        if unit:
            amount *= 1000
        if 10000 <= amount <= 300000:
            prices.append(int(amount))

    details["prices"] = sorted(set(prices))
    return details


# MAIN PIPELINE 
def main():
    collected = []

    for model in MODELS:
        response = get_response(model, QUERY)
        if not response:
            continue

        collected.append({
            "model": model,
            "response": response,
            "analysis": extract_details(response)
            })


# Find common patterns (appear in at least 2 models)
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
        "generated_at": datetime.now().isoformat()
    }

    with open("optimized_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Analysis completed successfully.")


if __name__ == "__main__":
    main()
