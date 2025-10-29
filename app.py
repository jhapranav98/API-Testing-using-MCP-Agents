#!/usr/bin/env python3
import os
from aws_cdk import App, Environment

from api_testing_cdk.github_agent_stack import GitHubAgentStack
from api_testing_cdk.jira_agent_stack import JiraAgentStack
from api_testing_cdk.postman_agent_stack import PostmanAgentStack
from api_testing_cdk.supervisor_agent_stack import SupervisorAgentStack
from api_testing_cdk.streamlit_frontend_stack import StreamlitFrontendStack

app = App()

# Get AWS account and region from environment variables or set default region
account = os.environ.get("CDK_DEFAULT_ACCOUNT")
region = os.environ.get("CDK_DEFAULT_REGION", "us-west-2")  # Default to us-west-2 for agents

# Create GitHub agent stack first to create the VPC
github_stack = GitHubAgentStack(
    app, "DematicsGitHubAgentStack",
    env=Environment(account=account, region=region),
    description="GitHub Agent Stack for interacting with GitHub repositories"
)

# Create JIRA agent stack using the VPC from GitHub stack
jira_stack = JiraAgentStack(
    app, "DematicsJiraAgentStack",
    vpc=github_stack.vpc,  # Pass the VPC from GitHub stack
    env=Environment(account=account, region=region),
    description="JIRA Agent Stack with MCP tools"
)

# Create Postman agent stack using the VPC from GitHub stack
postman_stack = PostmanAgentStack(
    app, "DematicsPostmanAgentStack",
    vpc=github_stack.vpc,  # Pass the VPC from GitHub stack
    env=Environment(account=account, region=region),
    description="Postman Agent Stack for API testing and collection management"
)

# Create Supervisor agent stack using the VPC from GitHub stack
supervisor_stack = SupervisorAgentStack(
    app, "DematicsSupervisorAgentStack",
    vpc=github_stack.vpc,  # Pass the VPC from GitHub stack
    env=Environment(account=account, region=region),
    description="Supervisor Agent Stack for coordinating multi-agent workflows"
)

# Create Streamlit frontend stack using the VPC from GitHub stack
streamlit_stack = StreamlitFrontendStack(
    app, "DematicsStreamlitFrontendStack",
    vpc=github_stack.vpc,  # Pass the VPC from GitHub stack
    env=Environment(account=account, region=region),
    description="Streamlit Frontend Stack for multi-agent UI"
)

app.synth()
