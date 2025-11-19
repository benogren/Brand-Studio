#!/usr/bin/env python3
"""
AI Brand Studio - Streamlit Web Chat Interface

A beautiful, interactive chat interface for brand identity creation.
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

from google.adk.runners import InMemoryRunner
from src.agents.orchestrator import create_orchestrator
from src.infrastructure.logging import get_logger

# Configure page
st.set_page_config(
    page_title="AI Brand Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .system-message {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        font-style: italic;
    }
    .message-role {
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stats-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'runner' not in st.session_state:
    st.session_state.runner = None
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'agent_stats' not in st.session_state:
    st.session_state.agent_stats = {
        'names_generated': 0,
        'validations_run': 0,
        'brands_created': 0
    }

def initialize_agent():
    """Initialize the orchestrator agent and runner."""
    if st.session_state.orchestrator is None:
        with st.spinner("🚀 Initializing AI agents..."):
            try:
                st.session_state.orchestrator = create_orchestrator()
                st.session_state.runner = InMemoryRunner(agent=st.session_state.orchestrator)
                st.session_state.session_started = True
                return True
            except Exception as e:
                st.error(f"Failed to initialize agents: {e}")
                return False
    return True

def display_message(role: str, content: str):
    """Display a chat message with appropriate styling."""
    if role == "user":
        css_class = "user-message"
        icon = "👤"
        role_label = "You"
    elif role == "assistant":
        css_class = "assistant-message"
        icon = "🤖"
        role_label = "AI Brand Studio"
    else:
        css_class = "system-message"
        icon = "ℹ️"
        role_label = "System"

    st.markdown(f"""
    <div class="chat-message {css_class}">
        <div class="message-role">{icon} {role_label}</div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def process_user_input(user_input: str):
    """Process user input through the orchestrator."""
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Show processing indicator
        with st.spinner("🎨 Creating your brand identity..."):
            # Run the orchestrator
            result = st.session_state.runner.run(user_input)

            # Extract response
            if hasattr(result, 'text'):
                response = result.text
            elif isinstance(result, dict):
                response = str(result)
            else:
                response = str(result)

            # Add assistant response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Update stats
            st.session_state.agent_stats['brands_created'] += 1

    except Exception as e:
        error_msg = f"I encountered an error while processing your request: {str(e)}\n\nPlease try again or rephrase your request."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})

def show_sidebar():
    """Display sidebar with features and examples."""
    with st.sidebar:
        st.markdown('<h2 class="main-header" style="font-size: 1.8rem;">AI Brand Studio</h2>', unsafe_allow_html=True)
        st.markdown("### 🎨 Multi-Agent Brand Creation")

        st.markdown("---")

        # Features
        st.markdown("### ✨ Features")

        features = [
            ("🔍", "Research", "Industry analysis & competitive insights"),
            ("✍️", "Name Generation", "Creative, RAG-enhanced naming"),
            ("✅", "Validation", "Domain & trademark checking"),
            ("🎯", "SEO", "Search optimization & meta content"),
            ("📖", "Story", "Brand narrative & positioning")
        ]

        for icon, title, desc in features:
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <strong>{icon} {title}</strong><br/>
                <small style="color: #6c757d;">{desc}</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Example prompts
        st.markdown("### 💡 Example Prompts")

        examples = [
            "Create a brand for an AI-powered fitness coaching app",
            "I need a brand name for a sustainable fashion marketplace",
            "Generate brand identity for a mental wellness app for Gen Z",
            "Brand my fintech app for freelance expense tracking"
        ]

        for example in examples:
            if st.button(f"📝 {example[:40]}...", key=f"example_{examples.index(example)}"):
                st.session_state.user_input = example

        st.markdown("---")

        # Stats
        st.markdown("### 📊 Session Stats")
        st.markdown(f"""
        <div class="stats-box">
            <strong>Brands Created:</strong> {st.session_state.agent_stats['brands_created']}<br/>
            <strong>Messages:</strong> {len(st.session_state.messages)}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Actions
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent_stats = {
                'names_generated': 0,
                'validations_run': 0,
                'brands_created': 0
            }
            st.rerun()

        st.markdown("---")

        # Info
        st.markdown("""
        <small style="color: #6c757d;">
        Powered by Google ADK & Gemini 2.0<br/>
        <a href="https://github.com/benogren/Brand-Agent" target="_blank">View on GitHub</a>
        </small>
        """, unsafe_allow_html=True)

def main():
    """Main application."""

    # Show sidebar
    show_sidebar()

    # Main content
    st.markdown('<h1 class="main-header">AI Brand Studio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create complete brand identities with AI-powered multi-agent collaboration</p>', unsafe_allow_html=True)

    # Initialize agents
    if not st.session_state.session_started:
        if not initialize_agent():
            st.stop()
        else:
            st.session_state.messages.append({
                "role": "system",
                "content": "👋 **Welcome to AI Brand Studio!**\n\nI'll help you create a complete brand identity using a team of specialized AI agents:\n\n"
                          "🔍 **Research Agent** - Analyzes your industry\n"
                          "✍️ **Name Generator** - Creates unique brand names\n"
                          "✅ **Validation Agent** - Checks domains & trademarks\n"
                          "🎯 **SEO Agent** - Optimizes for search engines\n"
                          "📖 **Story Agent** - Crafts your brand narrative\n\n"
                          "**To get started**, tell me about your product:\n"
                          "- What does it do?\n"
                          "- Who is it for?\n"
                          "- What's the brand personality?\n\n"
                          "Or try one of the example prompts in the sidebar! 👈"
            })

    # Display chat history
    for message in st.session_state.messages:
        display_message(message["role"], message["content"])

    # Chat input
    st.markdown("---")

    # Create columns for input and button
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Message AI Brand Studio",
            placeholder="Describe your product and brand vision...",
            key="user_input_field",
            label_visibility="collapsed"
        )

    with col2:
        send_button = st.button("Send", use_container_width=True, type="primary")

    # Handle input
    if send_button and user_input:
        process_user_input(user_input)
        st.rerun()

    # Show quick tips at the bottom
    if len(st.session_state.messages) <= 1:
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")

        tip_cols = st.columns(3)

        with tip_cols[0]:
            st.markdown("""
            **Be Specific**
            - Target audience
            - Industry/category
            - Brand personality
            """)

        with tip_cols[1]:
            st.markdown("""
            **Iterative Process**
            - Provide feedback
            - Request more names
            - Refine your vision
            """)

        with tip_cols[2]:
            st.markdown("""
            **Complete Package**
            - Brand names
            - Domain check
            - Taglines & story
            """)

if __name__ == "__main__":
    main()
