#!/usr/bin/env python3
"""
Test script to verify session configuration
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_session_persistence():
    """Test if session persists after login"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("1. Testing login...")
    login_data = {
        "login": "testuser",  # 请替换为实际的测试用户
        "password": "testpassword",  # 请替换为实际的密码
        "remember_me": False
    }
    
    try:
        # Login
        login_response = session.post(f"{BASE_URL}/users/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✓ Login successful")
            print(f"Session cookies: {session.cookies}")
            
            # Test accessing protected endpoint
            print("\n2. Testing protected endpoint access...")
            profile_response = session.get(f"{BASE_URL}/users/profile")
            print(f"Profile access status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                print("✓ Session is working correctly")
                user_data = profile_response.json()
                print(f"User: {user_data.get('data', {}).get('username', 'Unknown')}")
            else:
                print("✗ Session not maintained")
                print(f"Error: {profile_response.text}")
        else:
            print(f"✗ Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure the Flask app is running on localhost:8000")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_session_persistence() 