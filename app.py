import streamlit as st
import google.generativeai as genai
from typing import List, Dict
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Boris Chat Pro Version",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 4px solid;
        max-width: 80%;
    }
    .user-message {
        background-color: #2c2c2c;
        border-left-color: #4CAF50;
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #1a1a1a;
        border-left-color: #2196F3;
        color: white;
        margin-right: 20%;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #0e0e0e;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
        background-color: #2c2c2c;
        color: white;
        border: 1px solid #444;
    }
    .message-content {
        word-wrap: break-word;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model" not in st.session_state:
    st.session_state.model = None

def configure_gemini(api_key: str):
    """Configure Gemini API with the provided key"""
    try:
        genai.configure(api_key=api_key)
        # Use the latest model as shown in Google AI Studio
        model = genai.GenerativeModel('gemini-2.5-pro')
        return model
    except Exception as e:
        st.error(f"Error configuring Gemini API: {str(e)}")
        return None

def get_gemini_response(model, prompt: str, chat_history: List[Dict]) -> str:
    """Get response from Gemini API"""
    try:
        # Create chat history for context
        chat = model.start_chat(history=[])
        
        # Add previous messages for context (limit to last 10 for performance)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        context = ""
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
        
        # Send message with context
        full_prompt = f"{context}\nuser: {prompt}" if context else prompt
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"Error getting response: {str(e)}"

def main():
    # Header
    st.markdown("<h1 class='main-header'>🤖 Boris Chat Pro Max</h1>", unsafe_allow_html=True)
    
    # Sidebar for API key configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Try to get API key from environment variable first
        env_api_key = os.getenv("GEMINI_API_KEY")
        
        if env_api_key:
            st.success("✅ API Key loaded from environment variable")
            st.session_state.api_key = env_api_key
            if not st.session_state.model:
                st.session_state.model = configure_gemini(env_api_key)
        else:
            # API Key input if not found in environment
            st.info("💡 API key not found in environment variables")
            api_key_input = st.text_input(
                "Enter your Gemini API Key:",
                type="password",
                help="Get your API key from Google AI Studio: https://makersuite.google.com/app/apikey"
            )
            
            if api_key_input:
                st.session_state.api_key = api_key_input
                st.session_state.model = configure_gemini(api_key_input)
                if st.session_state.model:
                    st.success("✅ API Key configured successfully!")
                else:
                    st.error("❌ Failed to configure API Key")
        
        st.divider()
        
        # Chat controls
        st.header("💬 Chat Controls")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Display message count
        st.info(f"Messages in chat: {len(st.session_state.messages)}")
        
        st.divider()
        
        # Instructions
        st.header("📖 Instructions")
        st.markdown("""
        1. Set `GEMINI_API_KEY` environment variable, or
        2. Enter your Gemini API key manually above
        3. Start chatting with the AI assistant
        4. Use the clear button to reset the conversation
        5. The AI remembers the conversation context
        """)
        
        st.markdown("---")
        st.markdown("**Model:** Gemini 2.0 Flash")
        st.markdown("**Environment Setup:**")
        st.code("export GEMINI_API_KEY=your_api_key_here")
        st.markdown("**Note:** Environment variables take priority over manual input.")

    # Main chat interface
    if not st.session_state.api_key:
        st.warning("⚠️ Please set the GEMINI_API_KEY environment variable or enter your API key in the sidebar to start chatting.")
        st.markdown("""
        ### Option 1: Environment Variable (Recommended)
        ```bash
        export GEMINI_API_KEY=your_api_key_here
        streamlit run app.py
        ```
        
        ### Option 2: Manual Input
        Enter your API key in the sidebar.
        
        ### How to get your API key:
        1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Create a new API key
        4. Copy and use it with either method above
        """)
        return
    
    if not st.session_state.model:
        st.error("❌ Failed to initialize Gemini model. Please check your API key.")
        return
    
    # Display chat messages
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for i, message in enumerate(st.session_state.messages):
            # Clean the message content to avoid HTML issues
            clean_content = message["content"].replace("<", "&lt;").replace(">", "&gt;")
            
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong><br>
                    <div class="message-content">{clean_content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Gemini:</strong><br>
                    <div class="message-content">{clean_content}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-container">
            <div style="text-align: center; color: #888; padding: 2rem;">
                👋 Start a conversation by typing a message below!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message:",
                key="user_input",
                placeholder="Ask me anything...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send 📤", type="primary", use_container_width=True)
    
    # Handle user input - only when send button is clicked AND there's input
    if send_button and user_input.strip():
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Show loading spinner
        with st.spinner("🤔 Gemini is thinking..."):
            # Get AI response
            response = get_gemini_response(
                st.session_state.model,
                user_input,
                st.session_state.messages[:-1]  # Exclude the current message
            )
        
        # Add AI response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Clear input and rerun to show new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with Streamlit and Google Gemini 2.0 Flash API"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()