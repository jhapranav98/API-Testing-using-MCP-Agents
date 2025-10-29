#!/bin/bash

# Destroy script for Dematics E-Commerce API Testing Platform CDK stacks

echo "⚠️  WARNING: This will destroy all deployed stacks and resources!"
echo "Are you sure you want to continue? (y/N)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "🗑️  Destroying all stacks..."
    cdk destroy --all --force
    echo "✅ All stacks have been destroyed."
else
    echo "❌ Destruction cancelled."
    exit 1
fi
