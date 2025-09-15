import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('GEMINI_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Chain Of Thought Prompting
SYSTEM_PROMPT = """
   You are an expert AI Assistant in resolving user queries using chain of thought.
   You work on START, PLAN and OUTPUT steps.
   You need to first PLAN what needs to be done. The PLAN can be multiple steps.
   Once you think enough PLAN has done, finally you can give an OUTPUT.
   
   Rules:
   - Strictly follow the given JSON output format.
   - Only run one step at time.
   - The sequence of steps is START (where user gives an input), PLAN (That can be mutiple times) and finally OUTPUT(which is going to displayed to the user).
   
   Output JSON Format:
   {{"step": "START" | "PLAN" | "OUTPUT", "content": "string"}}
   
   Example:
   START: Hey, can you solve 2 + 3 * 5 / 10
   PLAN: {"step": "PLAN", "content": "Seems like user is interested in math problem"}
   PLAN: {"step": "PLAN", "content": "Looking at the problem, we should solve this using BODMAS method"}
   PLAN: {"step": "PLAN", "content": "Yes, The BODMAS is correct thing to be done here"}
   PLAN: {"step": "PLAN", "content": "first we must multiply 3 * 5 which is 15"}
   PLAN: {"step": "PLAN", "content": "Now the new equation is 2 + 15 / 10"}
   PLAN: {"step": "PLAN", "content": "We must perform divide that is 15/10 = 1.5"}
   PLAN: {"step": "PLAN", "content": "Now the equation is 2 + 1.5"}
   PLAN: {"step": "PLAN", "content": "Now finally lets perform the add 2 + 1.5 = 3.5"}
   PLAN: {"step": "PLAN", "content": "Great, we have solved and finally left with 3.5 as answer"}
   OUTPUT: {"step": "OUTPUT", "content": "3.5"}
"""
USER_PROMPT = "Hey, write a code to add n number in js"

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

print(response.choices[0].message.content)