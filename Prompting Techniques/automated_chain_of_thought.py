import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = OpenAI(
    api_key=os.getenv('GEMINI_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Chain-of-Thought System Prompt
SYSTEM_PROMPT = """
You are an expert AI Assistant in resolving user queries using chain of thought.
You work on START, PLAN and OUTPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has done, finally you can give an OUTPUT.

Rules:
- Strictly follow the given JSON output format.
- Only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (that can be multiple times) and finally OUTPUT (which is going to be displayed to the user).

Output JSON Format:
{"step": "START" | "PLAN" | "OUTPUT", "content": "string"}

Example:
Question: Hey, can you solve 2 + 3 * 5 / 10
START: {"step": "START", "content": "Hey, can you solve 2 + 3 * 5 / 10"}
PLAN: {"step": "PLAN", "content": "Seems like user is interested in math problem"}
PLAN: {"step": "PLAN", "content": "Looking at the problem, we should solve this using BODMAS method"}
PLAN: {"step": "PLAN", "content": "Yes, The BODMAS is correct thing to be done here"}
PLAN: {"step": "PLAN", "content": "first we must multiply 3 * 5 which is 15"}
PLAN: {"step": "PLAN", "content": "Now the new equation is 2 + 15 / 10"}
PLAN: {"step": "PLAN", "content": "We must perform divide that is 15/10 = 1.5"}
PLAN: {"step": "PLAN", "content": "Now the equation is 2 + 1.5"}
PLAN: {"step": "PLAN", "content": "Now finally let's perform the add 2 + 1.5 = 3.5"}
PLAN: {"step": "PLAN", "content": "Great, we have solved and finally left with 3.5 as answer"}
OUTPUT: {"step": "OUTPUT", "content": "3.5"}
"""

# Initialize message history
message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# Take user input
user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

# Loop until OUTPUT is returned
while True:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=message_history
    )
    
    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_result})
    
    try:
        parsed_result = json.loads(raw_result)
    except json.JSONDecodeError:
        # Skip malformed JSON and continue
        print("⚠️ Skipping invalid JSON:", raw_result)
        continue
    
    step = parsed_result.get("step")
    content = parsed_result.get("content")
    
    if step == "START":
        print("🔥", content)
    elif step == "PLAN":
        print("🧠", content)
    elif step == "OUTPUT":
        print("🤖 Final Answer:", content)
        break
    else:
        print("⚠️ Unexpected step:", parsed_result)