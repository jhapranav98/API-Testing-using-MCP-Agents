#!/usr/bin/env python3
"""
Simple Chatbot Interface for JIRA Agent
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.jira_agent import create_jira_agent

# Configure page
st.set_page_config(
    page_title="JIRA Agent Chatbot",
    page_icon="🎫",
    layout="centered"
)

def initialize_agent():
    """Initialize the JIRA agent"""
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = create_jira_agent()
        except Exception as e:
            st.error(f"Failed to initialize JIRA agent: {e}")
            return False
    return True

def initialize_chat():
    """Initialize chat history"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def extract_response_text(response):
    """Extract clean text from agent response - handles complex nested structures"""
    try:
        # If response is a string, return as-is
        if isinstance(response, str):
            return response
        
        # Handle dict with 'role' and 'content' structure
        if isinstance(response, dict):
            if 'content' in response:
                content = response['content']
                
                # Handle content as list
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if 'text' in item:
                                text_parts.append(item['text'])
                            elif 'content' in item:
                                text_parts.append(str(item['content']))
                            else:
                                text_parts.append(str(item))
                        else:
                            text_parts.append(str(item))
                    return ' '.join(text_parts)
                
                # Handle content as string
                elif isinstance(content, str):
                    return content
                
                # Handle content as dict
                elif isinstance(content, dict):
                    if 'text' in content:
                        return content['text']
                    else:
                        return str(content)
            
            # Handle other dict structures
            elif 'message' in response:
                return extract_response_text(response['message'])
            elif 'text' in response:
                return response['text']
            else:
                # Convert dict to string as fallback
                return str(response)
        
        # Handle objects with attributes
        if hasattr(response, 'content'):
            return extract_response_text(response.content)
        elif hasattr(response, 'message'):
            return extract_response_text(response.message)
        elif hasattr(response, 'text'):
            return response.text
        
        # Final fallback
        return str(response)
        
    except Exception as e:
        st.error(f"Error extracting response: {str(e)}")
        return f"Error extracting response: {str(e)}\n\nRaw response: {str(response)}"

def main():
    # Title
    st.title("🎫 JIRA Agent Chatbot")
    st.markdown("Ask me anything about JIRA operations - issues, projects, comments, attachments, and more!")
    
    # Sidebar with JIRA examples
    with st.sidebar:
        st.header("🚀 Quick JIRA Examples")
        st.markdown("Click any example to try it:")
        
        examples = {
            "📋 Issues": [
                "TBAPI-1",
                "Get details for TBAPI-1",
                "Show me issue TBAPI-1 with attachments"
            ],
            "🎫 Projects": [
                "List all JIRA projects",
                "Show me project information"
            ],
            "💬 Comments": [
                "Add a comment to issue TBAPI-1",
                "Get all comments for issue TBAPI-1"
            ],
            "👥 Users": [
                "Get user info for john.doe@company.com",
                "List all available issue types"
            ]
        }
        
        for category, questions in examples.items():
            with st.expander(category):
                for question in questions:
                    if st.button(question, key=f"example_{question}"):
                        # Add the example question to chat
                        st.session_state.messages.append({"role": "user", "content": question})
                        st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Debug section
        st.markdown("---")
        st.header("🔧 Debug")
        if st.button("Test Agent"):
            if "agent" in st.session_state:
                st.success("✅ Agent is initialized")
            else:
                st.error("❌ Agent not initialized")
    
    # Initialize components
    if not initialize_agent():
        st.stop()
    
    initialize_chat()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about JIRA operations..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get JIRA agent response
        with st.chat_message("assistant"):
            with st.spinner("🎫 JIRA Agent is working..."):
                try:
                    # Use async chat method for JIRA agent
                    import asyncio
                    raw_response = asyncio.run(st.session_state.agent.chat(prompt))
                    
                    # Extract clean text from the response
                    clean_response = extract_response_text(raw_response)
                    
                    # Display the response
                    st.markdown(clean_response)
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})
                    
                    # Optional: Show raw response for debugging
                    if st.checkbox("Show raw response (debug)", key=f"debug_{len(st.session_state.messages)}"):
                        st.json(raw_response)
                        
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    # Show the raw response for debugging
                    with st.expander("Debug Info"):
                        st.write("Error details:", str(e))
                        if 'raw_response' in locals():
                            st.write("Raw response:", raw_response)

if __name__ == "__main__":
    main()