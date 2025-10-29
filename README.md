MCP Supervisor Agent Platform

This project builds a local MCP (Model Context Protocol) server ecosystem that automates API testing using natural language prompts. Users interact through a Streamlit interface to trigger the supervisor agent, which reads BRD instructions from GitHub and coordinates with connected MCP tools to test APIs with positive and negative cases.

🧠 Overview

Supervisor Agent orchestrates multiple MCP tools.

Streamlit UI enables natural language interaction for API testing.

GitHub Integration allows fetching BRD documents as input.

MCP Tools handle endpoint validation and test case generation.

Deployment: MCP servers run locally, Streamlit client is deployed on AWS.

🧩 Project Structure
├── frontend/                     # Streamlit UI files  
├── api_testing_cdk/              # AWS CDK setup for infrastructure  
├── authenticate_customer.py      # Authentication logic  
├── chatbot.py                    # Natural language interface  
├── jira_agent_server.py          # Jira-related automation agent  
├── github_agent_server.py        # GitHub agent to fetch BRD and configs  
├── postman_agent_server.py       # Tool for API endpoint testing  
├── supervisor_agent_server.py    # Main supervisor coordinating MCP tools  
├── app.py                        # Entry point for Streamlit interface  
├── Dockerfile*                   # Docker builds for different components  
├── deploy.sh / destroy.sh        # Deployment scripts  
├── requirements-streamlit.txt    # Streamlit dependencies  
├── requirements-cdk.txt          # CDK dependencies  
└── README.md                     # Project documentation  

⚙️ Tech Stack

Language: Python

LLM API: AWS Bedrock (Sonet model)

Interface: Streamlit

Infrastructure: AWS CDK, Docker

MCP Tools: Local servers communicating over MCP protocol

🚀 How It Works

User enters a prompt on Streamlit (e.g., “Test the payroll API from BRD F01”).

The Supervisor Agent fetches the BRD document from GitHub.

MCP tools (Postman, GitHub, Jira agents) generate and execute API test cases.

Results are displayed back to the user through the Streamlit dashboard.

🐳 Running Locally
# Clone the repo  
git clone <repo_url>
cd <repo_name>

# Install dependencies  
pip install -r requirements-streamlit.txt

# Run Streamlit  
streamlit run app.py

🧱 Deployment

Each component can be containerized using its Dockerfile.

docker build -f Dockerfile.streamlit -t streamlit-client .
docker run -p 8501:8501 streamlit-client
