import streamlit as st
import os
from uuid import uuid4
from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict
from elevenlabs import ElevenLabs, save
from dotenv import load_dotenv

# Load env variables
load_dotenv()
os.environ["ELEVEN_LABS_API_KEY"] = os.getenv("ELEVEN_LABS_API_KEY")
os.makedirs("audio_generations", exist_ok=True)

from langchain_google_genai import ChatGoogleGenerativeAI


model_name="gemini-2.5-flash"

llm=ChatGoogleGenerativeAI(
    model=model_name,
    temperature=0.2
)






# ---------------- LangGraph State ----------------
class BlogAgentState(TypedDict):
    blog_url: str
    blog: str
    script: str
    voice_id: str
    output_path: str

# ---------------- Nodes ----------------
def blog_Fetcher(state: BlogAgentState) -> BlogAgentState:
    from tavily import TavilyClient
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(TAVILY_API_KEY)
    response = client.extract(urls=[state["blog_url"]])
    blog_content = response['results'][0]['raw_content']
    return {"blog": blog_content}

def summarize_script_writer(state: BlogAgentState) -> BlogAgentState:
    blog_content = state["blog"]
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
        
    template_of_summariztion_blog="""
    You are a skilled content writer and podcast script creator.
    Your task is to take the provided blog content and:
    1. Summarize the main ideas and insights.
    2. Rewrite it as an engaging, conversational script for audio narration.
    3. Keep the script concise (≤ 2000 characters), while maintaining clarity and flow.
    4. Remove any unnecessary text like ads, links, author bios, or repetitive statements.
    5. Use a friendly, listener-oriented tone with smooth transitions.
    6. Avoid technical jargon unless essential, and explain briefly if needed.
    7. Output the final script only, without extra commentary or formatting.

    Here is the blog content:
    {blog_post}


    """
    summ_prompt = ChatPromptTemplate.from_template(template_of_summariztion_blog)
    chainofsumm_blog = summ_prompt | llm | StrOutputParser()
    script_text = chainofsumm_blog.invoke({"blog_post": blog_content})
    return {"script": script_text}

def AskTO_Human(state: BlogAgentState) -> BlogAgentState:
    # Voice mapping
    voice_options = {
        "Aanya": "acCWxmzPBgXdHwA63uzP",
        "Kiara": "ZF6FPAbjXT4488VcRRnw",
        "Arjun": "JBFqnCBsd6RMkjVDRZzb",
        "Rohan": "y1adqrqs4jNaANXsIZnD"
    }
    # Streamlit voice selection
    selected_voice = st.selectbox("Select a voice:", list(voice_options.keys()))
    voice_id = voice_options[selected_voice]
    return {"voice_id": voice_id}

def podcast_generator(state: BlogAgentState) -> BlogAgentState:
    script_text = state["script"]
    voice_id = state["voice_id"]
    output_path = f"audio_generations/podcast_{uuid4()}.mp3"
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))
    audio = elevenlabs.text_to_speech.convert(
        text=script_text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    save(audio, output_path)
    st.audio(output_path, format="audio/mp3")
    st.download_button("Download Podcast", data=open(output_path, "rb").read(), file_name="podcast.mp3", mime="audio/mp3")
    return {"output_path": output_path}

# ---------------- Build LangGraph Workflow ----------------
workflow = StateGraph(BlogAgentState)
workflow.add_node("blog_Fetcher", blog_Fetcher)
workflow.add_node("script_writer", summarize_script_writer)
workflow.add_node("AskTO_Human", AskTO_Human)
workflow.add_node("podcast_generator", podcast_generator)

workflow.add_edge(START, "blog_Fetcher")
workflow.add_edge("blog_Fetcher", "script_writer")
workflow.add_edge("script_writer", "AskTO_Human")
workflow.add_edge("AskTO_Human", "podcast_generator")
workflow.add_edge("podcast_generator", END)

app = workflow.compile()

# ---------------- Streamlit App ----------------
st.title("📰 ➡️ 🎙️ Blog to Podcast Generator ")

blog_url = st.text_input("Enter the Blog URL:")

if st.button("Generate Podcast"):
    if not blog_url.strip():
        st.warning("Please enter a blog URL!")
    else:
        state = {"blog_url": blog_url}
        app.invoke(state)  
