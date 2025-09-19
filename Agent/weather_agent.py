from openai import OpenAI
import json
import requests

client = OpenAI(
    api_key= "",
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"
)

OPEN_WEATHER_API_KEY=""

def get_weather(city: str):
    print("Tool called ", city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        return f"The weather in {city} is {temp} degree Celcius"
    
    return "Something went wrong"

available_tools= {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city."
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
    - get_weather: Takes a city name as an input and returns the current weather for the city.
    
    Example:
    User Query: What is the weather of new york?
    Output: {{"step": "plan", "content": "The user is interested in weather data of new york city"}}
    Output: {{"step": "plan", "content": "From the available tools I should call get_weather"}}
    Output: {{"step": "action", "function": "get_weather", "input": "new york"}}
    Output: {{"step": "observe", "output": "12 Degree celcius"}}
    Output: {{"step": "result", "content": "The weather for new york seems to 12 degrees."}}
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