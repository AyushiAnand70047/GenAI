from fastmcp import FastMCP
import requests

mcp = FastMCP("My Server")

@mcp.tool()
def add(num1: int, num2: int) -> int:
    return num1 + num2

@mcp.tool()
def weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=%c+%t"
    response = requests.get(url)
    
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    return "Something went wrong"

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)