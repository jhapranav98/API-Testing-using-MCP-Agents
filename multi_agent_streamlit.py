# """
# E-Commerce API Testing Platform - Multi-Agent Frontend
# This application orchestrates JIRA analysis, test case generation, API mapping, and Postman execution.
# """
# from styles.css_styles import CSSStyles
# from services.api_service import APIService
# from components.chat_components import ChatComponents
# from components.sidebar_components import SidebarComponents
# from utils.session_manager import SessionManager
# from config.app_config import AppConfig
# import streamlit as st
# import sys
# import os

# # Add the frontend directory to the Python path
# frontend_path = os.path.dirname(__file__)
# sys.path.insert(0, frontend_path)


# # Configure Streamlit page
# st.set_page_config(
#     layout="wide",
#     page_title="E-Commerce API Testing Platform",
#     page_icon="🧪"
# )


# def main():
#     """Main application function."""
#     # Apply CSS styles
#     CSSStyles.apply_styles()

#     # Initialize session manager
#     session_manager = SessionManager()
#     session_manager.initialize_session()

#     # Initialize sidebar
#     sidebar = SidebarComponents(session_manager)
#     sidebar.render()

#     # Initialize chat components
#     chat = ChatComponents(session_manager)

#     # Render hero section
#     chat.render_hero_section()    # Handle chat interaction
#     if st.session_state.selected_agent != "Select Agent":
#         chat.render_chat_history()

#         # Handle regular user input
#         user_input = st.chat_input("Type your message here...")
#         if user_input:
#             session_manager.add_message_to_current_chat("user", user_input)
#             st.rerun()

#         # Handle API response
#         current_chat_history = session_manager.get_current_chat_history()
#         if current_chat_history and current_chat_history[-1]["role"] == "user":
#             api_service = APIService(session_manager)
#             api_service.handle_api_call()
#     else:
#         st.info("🔽 Please select an agent from the left sidebar.")


# if __name__ == "__main__":
#     main()
"""
E-Commerce API Testing Platform - Multi-Agent Frontend
This application orchestrates JIRA analysis, test case generation, API mapping, and Postman execution.
"""
from styles.css_styles import CSSStyles
from services.api_service import APIService
from components.chat_components import ChatComponents
from components.sidebar_components import SidebarComponents
from utils.session_manager import SessionManager
from config.app_config import AppConfig
import streamlit as st
import sys
import os

# Add the frontend directory to the Python path
frontend_path = os.path.dirname(__file__)
sys.path.insert(0, frontend_path)


# Configure Streamlit page
st.set_page_config(
    layout="wide",
    page_title="E-Commerce API Testing Platform",
    page_icon="🧪",
    initial_sidebar_state="expanded"  # Force sidebar to be expanded by default
)


def main():
    """Main application function."""
    try:
        # Apply CSS styles
        CSSStyles.apply_styles()

        # Initialize session manager
        session_manager = SessionManager()
        session_manager.initialize_session()
        

        # Force sidebar to always be visible by ensuring session state is properly initialized
        if "sidebar_initialized" not in st.session_state:
            st.session_state.sidebar_initialized = True
        
        # Force sidebar visibility with a simple test
        with st.sidebar:
            st.markdown("### 🤖 Multi-Agent Platform")
            if "selected_agent" not in st.session_state:
                st.session_state.selected_agent = "Supervisor Agent"
        
        # JavaScript to ensure sidebar is always visible
        st.markdown("""
        <script>
        function ensureSidebarVisible() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                sidebar.style.display = 'block';
                sidebar.style.visibility = 'visible';
                sidebar.style.opacity = '1';
                sidebar.style.width = '300px';
                sidebar.style.minWidth = '300px';
            }
        }
        
        // Run immediately and on DOM changes
        ensureSidebarVisible();
        
        // Set up observer to ensure sidebar stays visible
        const observer = new MutationObserver(ensureSidebarVisible);
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Also run on window resize
        window.addEventListener('resize', ensureSidebarVisible);
        </script>
        """, unsafe_allow_html=True)

        # Initialize and render sidebar - this should always happen
        try:
            sidebar = SidebarComponents(session_manager)
            sidebar.render()
        except Exception as sidebar_error:
            # Fallback sidebar rendering if there's an error
            st.sidebar.error(f"Sidebar error: {str(sidebar_error)}")
            st.sidebar.markdown("### 🤖 Agent Selection")
            
            # Basic agent selector as fallback
            agents = ["Supervisor Agent", "JIRA Agent", "Postman Agent", "GitHub Agent"]
            if "selected_agent" not in st.session_state:
                st.session_state.selected_agent = "Supervisor Agent"
            
            st.sidebar.selectbox(
                "Choose an agent:",
                options=agents,
                key="selected_agent"
            )
        
        # Debug info in sidebar (can be removed later)
        with st.sidebar:
            st.markdown("---")
            with st.expander("🔧 Debug Info", expanded=False):
                st.write(f"Selected Agent: {st.session_state.get('selected_agent', 'Not set')}")
                st.write(f"Session ID: {st.session_state.get('session_id', 'Not set')[:8]}...")
                st.write(f"Sidebar Initialized: {st.session_state.get('sidebar_initialized', False)}")
                st.write(f"Available Agents: {session_manager.config.get_agent_list()}")

        # Initialize chat components
        chat = ChatComponents(session_manager)

        # Render hero section
        chat.render_hero_section()
        
        # Handle chat interaction - always render chat interface
        # The sidebar should always be visible regardless of agent selection
        chat.render_chat_history()


        # Handle new user input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            session_manager.add_message_to_current_chat("user", user_input)
            st.rerun()

        # Handle API response
        current_chat_history = session_manager.get_current_chat_history()
        if (current_chat_history and 
            current_chat_history[-1]["role"] == "user"):
            
            api_service = APIService(session_manager)
            api_service.handle_api_call()
            
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.write("Please refresh the page to restart the application.")


if __name__ == "__main__":
    main()






