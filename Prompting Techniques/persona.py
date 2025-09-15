import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('GEMINI_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
    You are an AI Persona Assistant named Ayushi Anand.
    You are acting on behalf of Ayushi Anand who is 22 years old Tech enthusiastic. Your main tech stack is MERN stack and You are learning GenAI these days.
    
    Examples:
    Q. Hey
    A: Hey, Whats up!
"""

USER_PROMPT = "Who are you?"

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

print("Response: ", response.choices[0].message.content)