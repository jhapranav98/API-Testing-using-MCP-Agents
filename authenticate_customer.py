#!/usr/bin/env python3

import boto3
import json
import hmac
import hashlib
import base64

def calculate_secret_hash(username, client_id, client_secret):
    """Calculate SECRET_HASH for Cognito authentication"""
    message = username + client_id
    dig = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def update_secrets_manager(token):
    """Update token in Secrets Manager"""
    secrets = boto3.client('secretsmanager', region_name='us-west-2')
    
    try:
        # Update existing secret
        secrets.update_secret(
            SecretId='Api-Testing-postman-ID-Token',
            SecretString=json.dumps({       
                'id_token': token
            })
        )
        print("✅ Successfully updated token in Secrets Manager")
    except Exception as e:
        print(f"❌ Failed to update secret: {str(e)}")
        raise

def authenticate_customer():
    """Authenticate with existing Cognito user and save token"""
    
    # Get Cognito details from SSM
    ssm = boto3.client('ssm', region_name='us-west-2')
    
    try:
        # Get user pool ID
        response = ssm.get_parameter(Name='/ecommerce/dev/users/user-pool/id')
        user_pool_id = response['Parameter']['Value']
        
        # Get client ID (we'll need to find this from Cognito directly)
        print(f"🏛️ User Pool ID: {user_pool_id}")
        
        # Get the client ID from Cognito directly
        cognito = boto3.client('cognito-idp', region_name='us-west-2')
        clients_response = cognito.list_user_pool_clients(UserPoolId=user_pool_id)
        
        if clients_response['UserPoolClients']:
            client_id = clients_response['UserPoolClients'][0]['ClientId']
            print(f"🔑 Client ID: {client_id}")
            
            # Get client secret
            client_details = cognito.describe_user_pool_client(
                UserPoolId=user_pool_id,
                ClientId=client_id
            )
            client_secret = client_details['UserPoolClient'].get('ClientSecret')
            
            if client_secret:
                print("🔐 Client has secret - will generate SECRET_HASH")
            else:
                print("ℹ️ Client has no secret")
        else:
            print("❌ No Cognito clients found")
            return None
        
    except Exception as e:
        print(f"❌ Error getting Cognito config: {e}")
        return None
    
    # User credentials (from our previous setup)
    username = "48c193b0-b041-70ff-68e4-323eb150a6ed"
    password = "TestPassword123!@#"
    
    print(f"\n🔐 Authenticating user: {username}")
    
    try:
        # Prepare auth parameters
        auth_params = {
            'USERNAME': username,
            'PASSWORD': password
        }
        
        # Add SECRET_HASH if client has secret
        if client_secret:
            secret_hash = calculate_secret_hash(username, client_id, client_secret)
            auth_params['SECRET_HASH'] = secret_hash
        
        # Authenticate user
        response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters=auth_params
        )
        
        # Extract tokens
        auth_result = response['AuthenticationResult']
        id_token = auth_result['IdToken']
        
        print("✅ Authentication successful!")
        
        # Store token only in Secrets Manager
        try:
            update_secrets_manager(id_token)
            print("🔐 Token securely stored in AWS Secrets Manager")
        except Exception as e:
            print(f"❌ Failed to store token in Secrets Manager: {str(e)}")
            return None
        
        return id_token
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def main():
    """Authenticate customer for Scenario 2 testing"""
    print("🔐 CUSTOMER AUTHENTICATION FOR SCENARIO 2")
    print("=" * 60)
    print("🎯 Getting Cognito authentication token for customer testing")
    print("=" * 60)
    
    token = authenticate_customer()
    
    if token:
        print("\n" + "=" * 60)
        print("✅ READY FOR SCENARIO 2 TESTING")
        print("=" * 60)
        print("🚀 You can now run: python test_scenario2_customer.py")
        print("🎫 Authentication token is saved and ready to use")
    else:
        print("\n" + "=" * 60)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 60)
        print("🔧 Check your Cognito user credentials")

if __name__ == "__main__":
    main()