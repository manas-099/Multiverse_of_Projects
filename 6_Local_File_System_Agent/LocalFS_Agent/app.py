
import streamlit as st
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

# Patch for running asyncio inside Streamlit
nest_asyncio.apply()
load_dotenv()

# ================= Custom CSS Styling =================
def apply_custom_styling():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Custom sidebar title */
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
        padding: 0.5rem 0;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Model cards */
    .model-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    /* Chat messages - CHANGED TO BLACK TEXT */
    .stChatMessage {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* ALL CHAT TEXT BLACK */
    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span,
    .stChatMessage *,
    [data-testid="user"] .stChatMessage p,
    [data-testid="user"] .stChatMessage div,
    [data-testid="user"] .stChatMessage span,
    [data-testid="user"] .stChatMessage *,
    [data-testid="assistant"] .stChatMessage p,
    [data-testid="assistant"] .stChatMessage div,
    [data-testid="assistant"] .stChatMessage span,
    [data-testid="assistant"] .stChatMessage * {
        color: black !important;
    }
    
    [data-testid="user"] .stChatMessage {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="assistant"] .stChatMessage {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Main title */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background-color: #00ff88;
        box-shadow: 0 0 8px #00ff88;
    }
    
    .status-disconnected {
        background-color: #ff4444;
        box-shadow: 0 0 8px #ff4444;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Dark theme overrides */
    .dark-theme {
        background-color: #0e1117 !important;
    }
    
    .dark-theme .main .block-container,
    .dark-theme .main .block-container p,
    .dark-theme .main .block-container div,
    .dark-theme .stMarkdown {
        color: white !important;
    }
    
    .dark-theme .stInfo, .dark-theme .stSuccess, 
    .dark-theme .stWarning, .dark-theme .stError {
        color: white !important;
    }
    
    .dark-theme .stInfo p, .dark-theme .stSuccess p,
    .dark-theme .stWarning p, .dark-theme .stError p {
        color: white !important;
    }
    
    .dark-theme .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* DARK THEME CHAT TEXT ALSO BLACK */
    .dark-theme .stChatMessage p,
    .dark-theme .stChatMessage div,
    .dark-theme .stChatMessage span,
    .dark-theme .stChatMessage *,
    .dark-theme [data-testid="user"] .stChatMessage p,
    .dark-theme [data-testid="user"] .stChatMessage div,
    .dark-theme [data-testid="user"] .stChatMessage span,
    .dark-theme [data-testid="user"] .stChatMessage *,
    .dark-theme [data-testid="assistant"] .stChatMessage p,
    .dark-theme [data-testid="assistant"] .stChatMessage div,
    .dark-theme [data-testid="assistant"] .stChatMessage span,
    .dark-theme [data-testid="assistant"] .stChatMessage * {
        color: black !important;
    }
    
    .dark-theme [data-testid="user"] .stChatMessage {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .dark-theme [data-testid="assistant"] .stChatMessage {
        background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= Model Configuration =================
MODEL_CONFIGS = {
    "Groq Models": {
        "deepseek-r1-distill-llama-70b": {
            "name": "DeepSeek R1 Distill (Llama 70B)",
            "api_key_name": "GROQ_API_KEY",
            "provider": "groq",
            "description": "Advanced reasoning model with high accuracy"
        },
        "llama3-groq-70b-8192-tool-use-preview": {
            "name": "Llama 3 Groq 70B (Tool Use)",
            "api_key_name": "GROQ_API_KEY", 
            "provider": "groq",
            "description": "Optimized for tool usage and function calling"
        },
        "mixtral-8x7b-32768": {
            "name": "Mixtral 8x7B",
            "api_key_name": "GROQ_API_KEY",
            "provider": "groq", 
            "description": "Fast and efficient mixture of experts model"
        }
    },
    "Google Models": {
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "api_key_name": "GOOGLE_API_KEY",
            "provider": "google",
            "description": "Google's latest multimodal model"
        },
        "gemini-1.5-pro": {
            "name": "Gemini 1.5 Pro", 
            "api_key_name": "GOOGLE_API_KEY",
            "provider": "google",
            "description": "Advanced reasoning with long context"
        }
    },
    "OpenAI Models": {
        "gpt-4o": {
            "name": "GPT-4o",
            "api_key_name": "OPENAI_API_KEY",
            "provider": "openai",
            "description": "Latest GPT-4 optimized model"
        },
        "gpt-4o-mini": {
            "name": "GPT-4o Mini",
            "api_key_name": "OPENAI_API_KEY", 
            "provider": "openai",
            "description": "Faster, cost-effective GPT-4 variant"
        }
    }
}

def get_all_models():
    """Get all models as a flat list for selectbox"""
    models = []
    for category, category_models in MODEL_CONFIGS.items():
        for model_id, config in category_models.items():
            models.append(f"{config['name']} ({category})")
    return models

def get_model_id_from_display(display_name):
    """Convert display name back to model ID"""
    for category, category_models in MODEL_CONFIGS.items():
        for model_id, config in category_models.items():
            if f"{config['name']} ({category})" == display_name:
                return model_id, config
    return None, None

# ================= Page Configuration =================
st.set_page_config(
    page_title="🚀 LocalFS Agent", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_styling()

# ================= Sidebar Configuration =================
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Agent Configuration</div>', unsafe_allow_html=True)
    
    # Model Selection Section
    st.markdown('<div class="section-header">🧠 Model Selection</div>', unsafe_allow_html=True)
    
    model_display_names = get_all_models()
    selected_model_display = st.selectbox(
        "Choose AI Model:",
        model_display_names,
        index=0,
        help="Select the AI model to power your agent"
    )
    
    # Get model config
    selected_model_id, model_config = get_model_id_from_display(selected_model_display)
    
    if model_config:
        # Display model info card
        st.markdown(f"""
        <div class="model-card">
            <strong>{model_config['name']}</strong><br>
            <small>{model_config['description']}</small><br>
            <small>Provider: {model_config['provider'].title()}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Dynamic API Key Input
        st.markdown('<div class="section-header">🔑 API Configuration</div>', unsafe_allow_html=True)
        
        api_key_name = model_config['api_key_name']
        api_key = st.text_input(
            f"{model_config['provider'].title()} API Key:",
            value=os.getenv(api_key_name, ""),
            type="password",
            help=f"Enter your {model_config['provider'].title()} API key to use {model_config['name']}"
        )
        
        # API Key Status
        if api_key:
            st.markdown('<span class="status-indicator status-connected"></span>API Key Configured', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-indicator status-disconnected"></span>API Key Required', 
                       unsafe_allow_html=True)
    
    # Model Parameters Section  
    st.markdown('<div class="section-header">🎛️ Model Parameters</div>', unsafe_allow_html=True)
    
    temperature = st.slider(
        "Temperature:", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.2, 
        step=0.05,
        help="Controls randomness: lower = more focused, higher = more creative"
    )
    
    max_tokens = st.number_input(
        "Max Tokens:",
        min_value=100,
        max_value=8000, 
        value=2000,
        step=100,
        help="Maximum number of tokens in the response"
    )
    
    # File System Configuration
    st.markdown('<div class="section-header">📂 File System Access</div>', unsafe_allow_html=True)
    
    default_roots = [r"C:\Users\manas\OneDrive\Desktop\Bright_data"]
    roots_input = st.text_area(
        "Allowed Root Directories:",
        value=", ".join(default_roots),
        height=100,
        help="Comma-separated list of directories the agent can access"
    )
    roots = [r.strip() for r in roots_input.split(",") if r.strip()]
    
    st.info(f"📁 {len(roots)} directories configured")
    
    # UI Theme Section
    st.markdown('<div class="section-header">🎨 Appearance</div>', unsafe_allow_html=True)
    
    theme = st.radio(
        "Theme:", 
        ["Light", "Dark"], 
        index=0,
        horizontal=True
    )
    
    # Apply dark theme
    if theme == "Dark":
        st.markdown('<div class="dark-theme">', unsafe_allow_html=True)
    
    # Connection Status
    st.markdown('<div class="section-header">🔌 Status</div>', unsafe_allow_html=True)
    if api_key and roots:
        st.success("✅ Ready to chat!")
    else:
        st.warning("⚠️ Configuration incomplete")

# ================= Session State Management =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False

# ================= Agent Setup Function =================
@st.cache_resource
def create_agent_instance(model_id, api_key, temp, max_tok, roots_str):
    """Create and cache agent instance"""
    async def setup_agent():
        client = MultiServerMCPClient({
            "FileOps_HelperServer": {
                "command": "python", 
                "args": ["server/FileOps_helper.py"],
                "transport": "stdio",
            }
        })
        
        await asyncio.sleep(1)
        tools = await client.get_tools()
        
        llm = ChatGroq(
            model=model_id,
            temperature=temp,
            max_tokens=max_tok,
            reasoning_format="parsed", 
            max_retries=2,
            api_key=api_key,
        )
        
        roots_list = [r.strip() for r in roots_str.split(",") if r.strip()]
        system_message = f"All file queries are limited to these roots: {roots_list}"
        checkpointer = InMemorySaver()
        
        agent = create_react_agent(
            llm,
            tools, 
            prompt=open(r"server/sys_msg.txt").read().strip() + system_message,
            checkpointer=checkpointer,
        )
        return agent
    
    return asyncio.run(setup_agent())

# ================= Main Chat Interface =================
st.markdown('<h1 class="main-title">🚀 LocalFS Agent</h1>', unsafe_allow_html=True)

# Display model info
if model_config:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"🤖 Using **{model_config['name']}** • Temperature: {temperature} • Max Tokens: {max_tokens}")

# Chat History
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("💬 Ask me anything about your files...", disabled=not (api_key and roots)):
    # Validation
    if not api_key:
        st.error("🔑 Please configure your API key in the sidebar")
        st.stop()
    
    if not roots:
        st.error("📂 Please configure allowed directories in the sidebar")
        st.stop()
    
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Processing your request..."):
            try:
                # Create agent instance
                agent = create_agent_instance(
                    selected_model_id, 
                    api_key, 
                    temperature,
                    max_tokens,
                    roots_input
                )
                
                config = {"configurable": {"thread_id": "1"}}
                response = asyncio.run(
                    agent.ainvoke({"messages": [{"role": "user", "content": prompt}]}, config)
                )
                
                reply = response["messages"][-1].content
                st.markdown(reply)
                
                # Store assistant message
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.error("Please check your API key and configuration.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <small>🤖 Powered by AI • 📁 Local File System Agent • Made with ❤️ using Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)