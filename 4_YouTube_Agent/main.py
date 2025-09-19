from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import FunctionCallTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.ui import Console
import os
import asyncio
load_dotenv()
gemini_api_key=os.getenv('GOOGLE_API_KEY')
you_tube_api_key=os.getenv("YOUTUBE_API_KEY")
print("Gemini key loaded:", gemini_api_key is not None)
print("YouTube key loaded:", you_tube_api_key is not None)

def terminate():
    """tool to teminate the agent exicution"""
    pass
async def config():


    model_client=OpenAIChatCompletionClient(
    model="gemini-2.5-flash",
    api_key=gemini_api_key
    )

    server_parameters = StdioServerParams(
        command="npx",
        args=["-y", "youtube-data-mcp-server"],
        env={
        "YOUTUBE_API_KEY":you_tube_api_key,
        
      }
    )
    
    await asyncio.sleep(10)
    mcp_tool = await mcp_server_tools(server_parameters)

        
    agent=AssistantAgent(
        name="Jarvis",
        model_client=model_client,
        system_message=open("system_msg(agent).txt").read().strip(),
        tools=mcp_tool,
        reflect_on_tool_use=True,
        max_tool_iterations=10
    )
    critic_agent=AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message=open('critic.txt').read().strip(),
        tools=[terminate],
    )
    team=RoundRobinGroupChat(
        participants=[agent,critic_agent],
        max_turns=5,
        termination_condition=FunctionCallTermination('terminate'),
        
    )
    return team

async def orchestrate(team,task):
    async for msg in team.run_stream(task=task):
        yield msg
async def main():
    team= await config()
    task=input("enter your query:")

    await Console(orchestrate(team,task))


if __name__=='__main__':
    asyncio.run(main())



