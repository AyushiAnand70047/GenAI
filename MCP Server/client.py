from mcp_use import MCPClient, MCPAgent
from langchain_openai import ChatOpenAI
import asyncio

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
    - weather: Takes a city name as an input and returns the current weather for the city.
    - add: Take two number as an input and return its sum
    
    Example:
    User Query: What is the weather of new york?
    Output: {{"step": "plan", "content": "The user is interested in weather data of new york city"}}
    Output: {{"step": "plan", "content": "From the available tools I should call weather"}}
    Output: {{"step": "action", "function": "weather", "input": "new york"}}
    Output: {{"step": "observe", "output": "12 Degree celcius"}}
    Output: {{"step": "result", "content": "The weather for new york seems to 12 degrees."}}
"""

async def main():
    config_path = "client_config.json"
    mcp_client = MCPClient(config_path)
    
    user_prompt = input("Enter your query: ")

    llm = ChatOpenAI(
        model="gemini-2.5-flash",
        api_key="<your_api_key>",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        temperature=0
    )

    agent = MCPAgent(llm=llm, client=mcp_client, max_steps=30)
    
    result = await agent.run(user_prompt)
    
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())