from openai import OpenAI
import json
import requests
import os

client = OpenAI(
    api_key= "",
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run_command(command):
    result = os.system(command)
    return result

available_tools= {
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns output."
    }
}

system_prompt = f"""
    You are an helpful AI Assistant who is specialised in resolving query.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning, select the relevant tool from the avaialble tool. and based on the tool selection you perform an action to call the tool.
    wait for the observation and based on the observation from the tool call resolve the user query.
    
    Rules:
    - Follow the output JSON Format.
    - Always perform one step at a time and wait for next input.
    - Carefully analyse the user query.
    
    Output JSON Format: 
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function"
    }}
    
    Available Tools:
    - run_command: Takes a command as input to execute on system and returns output.
    
    Example:
    User Query: list all the files present in current directory?
    Output: {{"step": "plan", "content": "The user is interested in listing the files present in the current directory"}}
    Output: {{"step": "plan", "content": "From the available tools I should call run_command"}}
    Output: {{"step": "action", "function": "run_command", "input": "generate a command which is used for listing files in windows operating system and pass the command as input to run_command"}}
    Output: {{"step": "observe", "output": "list of all files"}}
    Output: {{"step": "result", "content": "The files are listed here."}}
"""

messages = [
    {"role": "system", "content": system_prompt},
]

user_query = input('> ')

messages.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=messages
    )
    
    parsed_output = json.loads(response.choices[0].message.content)
    
    messages.append({"role": "assistant", "content": json.dumps(parsed_output)})
    
    if parsed_output.get("step") == "plan":
        print("🧠",parsed_output.get("content"))
        continue
    
    if parsed_output.get("step") == "action":
        tool_name = parsed_output.get("function")
        tool_input = parsed_output.get("input")
        
        if available_tools.get(tool_name, False) != False:
            output = available_tools[tool_name].get("fn")(tool_input)
            messages.append({"role": "assistant", "content": json.dumps({"step": "observe", "output": output})})
            continue
        
    if parsed_output.get("step") == "result":
        print("🤖 ", json.dumps(parsed_output.get("content")))
        break