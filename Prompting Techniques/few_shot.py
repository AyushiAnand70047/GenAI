import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('GEMINI_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Few Shot Prompting
SYSTEM_PROMPT = """
You have to only answer coding related question. Do not ans anything else. If user ask something other than coding, just say sorry.

Rule:
- Strictly follow the output in JSON format

Output Format:
{{
    "code": "string" or "None",
    "isCodingQuestion": boolean
}}

Examples:
Q: Can you explain the a + b whole square?
A: {{"code": null, "isCodingQuestion": false}}

Q: Hey, Write a code in python for adding two numbers.
A: {{"code": "def add(a, b): return a + b", "isCodingQuestion": true}}
"""
# USER_PROMPT = "what is a + b whole cube?"
USER_PROMPT = "write code in python for calculating a + b whole cube"

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

print(response.choices[0].message.content)