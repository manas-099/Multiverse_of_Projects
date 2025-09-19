
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
import asyncio
import getpass
import os
load_dotenv()


os.environ["GOOGLE_API_KEY"]=os.getenv('GOOGLE_API_KEY')
gemini_key=os.getenv('GOOGLE_API_KEY')
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")

async def main():
    client=MultiServerMCPClient(
        {
            "FileOps_HelperServer":{
                "command":"python",
                "args":["server/FileOps_helper.py"],
                "transport":"stdio"
            }
        }
    
    )
    
    # client = MultiServerMCPClient({
    # "FileOps_HelperServer": {
    #     "url": "http://127.0.0.1:8000",  # HTTP endpoint of your running server
    #     "transport": "streamable_http"
    # }
    # })
    
    await asyncio.sleep(1)  # wait 1 sec for server to be ready
    tools=await client.get_tools()

    

    llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    # other params...
    )
    # agent=create_react_agent(
    #     llm,tools
    # )
    # 
    roots = [
        # r"C:\Users\manas\One\Desktop",
        r"C:\Users\ms\OneDrive\Desktop\Bright_data"
        # r"C:\Users\manas\Documents",
        # r"C:\Users\manas\Downloads",
       
    ]

    




    system_message = f"All file queries are limited to these roots: {roots}"
    checkpointer = InMemorySaver()
    agent = create_react_agent(
        llm, 
        tools, 
        prompt=open(r'server\sys_msg.txt').read().strip()+system_message,
        checkpointer=checkpointer
        )
    config = {"configurable": {"thread_id": "1"}}

    

    


    print(r"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║🚀  Welcome to the LocalFS Agent Interactive Console  🚀 ║
    ║                                                          ║
    ║   Your smart file assistant is ready to help you:        ║
    ║     • Search files & folders                             ║
    ║     • Read, write, delete files                          ║
    ║     • Organize your directories                          ║
    ║                                                          ║
    ║   💡 Type 'exit' anytime to quit the loop                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config
        )
       
        
        ai_reply =response['messages'][-1].content
        print("AI:", ai_reply)


if __name__=="__main__":
    asyncio.run(main())