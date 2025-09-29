from graph import create_chat_graph
import json
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command

MONGODB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": "4"}}

def init():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)
        state = graph_with_mongo.get_state(config=config)
        # for message in state.values['messages']:
        #     message.pretty_print()
            
        last_message = state.values['messages'][-1]
        tool_calls = getattr(last_message, "tool_calls", [])
        
        user_query = None
        for call in tool_calls:
            if call.get("name", "").strip().lower() == "human_assistance_tool":
                args = call.get("args", {})
                user_query = args.get("query")

                # If args is a string, try to load JSON
                if isinstance(args, str):
                    try:
                        args_dict = json.loads(args)
                        user_query = args_dict.get("query")
                    except json.JSONDecodeError:
                        print("Failed to decode function arguments.")
                # If args is already dict, get query directly
                elif isinstance(args, dict):
                    user_query = args.get("query")
        
        print("User is Trying to Ask:", user_query)
        
        ans = input("Resolution > ")
        
        resume_command = Command(resume={"data": ans})
        
        for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
        


init()