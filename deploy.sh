#!/bin/bash

# Deploy script for Dematics E-Commerce API Testing Platform CDK stacks

echo "🚀 Starting deployment of Dematics E-Commerce API Testing Platform..."

# Check if AWS CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK not found. Please install it first:"
    echo "npm install -g aws-cdk"
    exit 1
fi

# Check if Python requirements are installed
echo "📦 Installing Python dependencies..."
pip install -r requirements-cdk.txt

# Bootstrap CDK (only needed once per account/region)
echo "🔧 Bootstrapping CDK..."
cdk bootstrap

# Synthesize CloudFormation templates
echo "🔍 Synthesizing CloudFormation templates..."
cdk synth

# Deploy all stacks
echo "🚢 Deploying all stacks..."
cdk deploy --all --require-approval=never

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Stack URLs will be displayed in the CDK output above."
echo "🔗 Look for outputs ending with 'URL' to access your deployed services."
