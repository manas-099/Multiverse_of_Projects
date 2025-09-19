from langgraph.graph import StateGraph,MessagesState,START,END
from typing_extensions import Annotated,List
from langgraph.graph.message import BaseMessage,add_messages
from langchain_core.prompts import ChatPromptTemplate
from stacksnap.tools.stacksnap_tool import stacks_analyzer
from langchain_core.output_parsers import StrOutputParser
from stacksnap.utils.model_loader import ModelLoader
import os

get_llm=ModelLoader(model_provider="gemini")
llm=get_llm.load_llm()




class StackSnapState(MessagesState):
    # messages:Annotated[List[BaseMessage],add_messages]
    repo_url:str
    result:dict
    stack_info:dict



def gather_context(state:StackSnapState)->StackSnapState:
    repo_url=state.get("repo_url","")

    # 1️⃣ Gather repo context + stack
    context, stack_info = stacks_analyzer(repo_url)

    return {"repo_url":repo_url,"stack_info":stack_info}

def stack_inspector(state:StackSnapState)->StackSnapState:
    stack_info=state.get("stack_info",{})
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # path=os.path.join(current_dir, "..", "prompt_library", "prompt.txt")
    # template=open(path).read().strip()
    path = os.path.normpath(os.path.join(current_dir, "..", "prompt_library", "prompt.txt"))

    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        template = f.read().strip()
    prompt=ChatPromptTemplate.from_template(template)
   

    chain=prompt|llm|StrOutputParser()
    response=chain.invoke({"stack":stack_info})
    return {"stack_info":stack_info,"result":response}

    
    

def analyze_repo():
    graph = StateGraph(StackSnapState)
    graph.add_node("gather_context", gather_context)
    graph.add_node("stack_inspector", stack_inspector)
    graph.add_edge(START, "gather_context")
    graph.add_edge("gather_context", "stack_inspector")
    graph.add_edge("stack_inspector", END)
    app=graph.compile()

    return app

if __name__=="__main__":
    app=analyze_repo()

