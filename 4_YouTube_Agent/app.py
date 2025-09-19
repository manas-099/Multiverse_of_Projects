import streamlit as st
from main import config,orchestrate
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ToolCallExecutionEvent,ToolCallRequestEvent
import asyncio

st.title("youtube_agent")

chat=st.container()
task=st.chat_input("Enter your query here..")

def show(container,msg):
    with container:
        if not isinstance(msg,TaskResult):
            if msg.source=="user":
                with st.chat_message('human'):
                    st.markdown(msg.content)
            else:
                if isinstance(msg,(ToolCallRequestEvent,ToolCallExecutionEvent)):
                    st.expander('tool call')
                    st.write(msg)
                else:
                    with st.chat_message('assistant'):
                        st.markdown(msg.content)




        
if task:
    team=asyncio.run(config())
    async def run_team(team,task):
        async for msg in orchestrate(team,task):
            show(chat,msg)
    with st.spinner("running agent.."):
        asyncio.run(run_team(team,task))
    st.success("Task completed")
