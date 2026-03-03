from groq import Groq
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Updated with current working models!
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
]


def clean_json_response(text):
    """
    Cleans AI response and extracts valid JSON
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    # Find JSON array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        text = match.group(0)

    # Fix amounts with commas inside numbers
    # e.g 2,575.00 → 2575.00
    text = re.sub(r'(\d),(\d{3})', r'\1\2', text)

    # Fix trailing commas
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    # Fix apostrophes inside JSON string values
    # Strategy: find each JSON string value and
    # replace apostrophes with a space inside them
    def fix_string_value(match):
        content = match.group(1)
        # Replace apostrophe with nothing
        content = content.replace("'", "")
        return f'"{content}"'

    # Only fix strings that contain apostrophes
    text = re.sub(r'"([^"\']*\'[^"\']*)"', 
                  fix_string_value, text)

    return text

def extract_transactions_with_ai(raw_text):
    """
    Sends raw text to Groq AI
    Extracts and classifies transactions
    Works for ANY bank statement format!
    """

    prompt = f"""
You are a financial data extraction assistant.

Below is raw text from a bank statement.

Extract ALL transactions where money was SPENT (debits/money out only).

For each transaction return:
- description: merchant or transaction name (string)
- amount: amount spent as a number only, no currency symbols
- category: one of these exact values only:
  Food, Transport, Shopping, Entertainment,
  Healthcare, Utilities, Rent, Cash, Other

STRICT RULES:
- Ignore salary, deposits, money coming IN
- Ignore balance amounts  
- Ignore headers and footers
- Return ONLY a valid JSON array, nothing else
- No markdown, no explanation, no extra text
- Amounts must be numbers like 24.50 not strings like "24.50"

Example of EXACT output format required:
[
    {{"description": "Swiggy", "amount": 250.00, "category": "Food"}},
    {{"description": "Ola Cab", "amount": 180.00, "category": "Transport"}}
]

Bank statement text:
{raw_text}
"""

    for model_name in MODELS:
        try:
            print(f"🤖 Trying model: {model_name}...")

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Zero = most consistent output!
            )

            response_text = response.choices[0].message.content.strip()
            print(f"✅ Got response from {model_name}!")
            print(f"Raw response:\n{response_text}\n")

            # Clean the response
            cleaned = clean_json_response(response_text)
            print(f"Cleaned JSON:\n{cleaned}\n")

            # Parse JSON
            transactions = json.loads(cleaned)

            # Validate each transaction has required fields
            valid_transactions = []
            for t in transactions:
                if 'description' in t and 'amount' in t:
                    # Ensure amount is a number
                    t['amount'] = float(str(t['amount'])
                                       .replace(',', '')
                                       .replace('£', '')
                                       .replace('$', '')
                                       .strip())
                    # Ensure category exists
                    if 'category' not in t:
                        t['category'] = 'Other'
                    valid_transactions.append(t)

            print("=== TRANSACTIONS FOUND ===")
            for t in valid_transactions:
                print(f"  {t['description']} → "
                      f"{t['amount']} ({t['category']})")
            print(f"Total: {len(valid_transactions)} transactions")
            print("==========================")

            return valid_transactions

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed for {model_name}: {e}")
            print(f"Problematic text: {response_text[:200]}")
            continue

        except Exception as e:
            print(f"❌ {model_name} failed: {str(e)}")
            continue

    raise Exception("All models failed! Check your API key.")