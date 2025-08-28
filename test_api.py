#!/usr/bin/env python3
"""
Test script for Quiz App API - Phone-Based Authentication
Run this script to test all the API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def get_test_phone():
    """Get test phone number"""
    return "+1234567890"

def get_test_username():
    """Get test username"""
    return "testuser123"

def test_request_otp():
    """Test OTP request"""
    print("Testing OTP request...")
    
    otp_request = {
        "phone_number": get_test_phone()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/request-otp", json=otp_request)
        
        if response.status_code == 200:
            print("✅ OTP requested successfully!")
            otp_data = response.json()
            print(f"OTP Code: {otp_data['otp_code']}")
            print(f"Expires in: {otp_data['expires_in_minutes']} minutes")
            return otp_data['otp_code']
        else:
            print(f"❌ OTP request failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def test_register():
    """Test user registration"""
    print("\nTesting user registration...")
    
    user_data = {
        "username": get_test_username(),
        "phone_number": get_test_phone(),
        "nickname": "TestUser"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        
        if response.status_code == 200:
            print("✅ User registered successfully!")
            return response.json()
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  User already registered")
            return None
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def test_login(otp_code):
    """Test user login with OTP"""
    print("\nTesting user login...")
    
    login_data = {
        "phone_number": get_test_phone(),
        "otp_code": otp_code
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ Login successful!")
            token_data = response.json()
            print(f"Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def test_create_question(token):
    """Test creating a question"""
    print("\nTesting question creation...")
    
    question_data = {
        "question_text": "What is the capital of Japan?",
        "option_a": "Seoul",
        "option_b": "Beijing",
        "option_c": "Tokyo",
        "option_d": "Bangkok",
        "correct_answer": "C",
        "points": 15,
        "time_limit": 25
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/questions", json=question_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Question created successfully!")
            return response.json()
        else:
            print(f"❌ Question creation failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def test_get_questions():
    """Test getting all questions"""
    print("\nTesting get questions...")
    
    try:
        response = requests.get(f"{BASE_URL}/questions")
        
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ Retrieved {len(questions)} questions!")
            for q in questions:
                print(f"  - {q['question_text']} ({q['points']} points, {q['time_limit']}s)")
                print(f"    Correct Answer: {q['correct_answer']}")
            return questions
        else:
            print(f"❌ Failed to get questions: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def test_submit_quiz_attempt(token):
    """Test submitting a quiz attempt"""
    print("\nTesting quiz attempt submission...")
    
    attempt_data = {
        "score": 90,
        "total_points": 120,
        "time_taken": 380
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/quiz-attempt", json=attempt_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Quiz attempt submitted successfully!")
            return response.json()
        else:
            print(f"❌ Quiz attempt submission failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def test_leaderboards():
    """Test getting leaderboards"""
    print("\nTesting leaderboards...")
    
    # Test weekly leaderboard
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/week")
        if response.status_code == 200:
            weekly = response.json()
            print(f"✅ Weekly leaderboard: {len(weekly)} entries")
        else:
            print(f"❌ Weekly leaderboard failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    
    # Test monthly leaderboard
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/month")
        if response.status_code == 200:
            monthly = response.json()
            print(f"✅ Monthly leaderboard: {len(monthly)} entries")
        else:
            print(f"❌ Monthly leaderboard failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    
    # Test yearly leaderboard
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/year")
        if response.status_code == 200:
            yearly = response.json()
            print(f"✅ Yearly leaderboard: {len(yearly)} entries")
        else:
            print(f"❌ Yearly leaderboard failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")

def test_root():
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            data = response.json()
            print(f"Message: {data['message']}")
            print(f"Available endpoints: {len(data['endpoints'])}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")

def test_user_info(token):
    """Test getting user info"""
    print("\nTesting user info endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/user/info", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ User info retrieved successfully!")
            print(f"  Username: {user_info['username']}")
            print(f"  Phone Number: {user_info['phone_number']}")
            print(f"  Nickname: {user_info['nickname']}")
            return user_info
        else:
            print(f"❌ User info failed: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Quiz App API Tests - Phone-Based Authentication")
    print("=" * 60)
    
    # Test root endpoint
    test_root()
    
    # Test OTP request
    otp_code = test_request_otp()
    if not otp_code:
        print("Cannot continue without OTP")
        return
    
    # Test registration
    user = test_register()
    
    # Test login with OTP
    token = test_login(otp_code)
    if not token:
        print("Cannot continue without authentication token")
        return
    
    # Test user info
    user_info = test_user_info(token)
    
    # Test question creation
    question = test_create_question(token)
    
    # Test getting questions
    questions = test_get_questions()
    
    # Test quiz attempt submission
    attempt = test_submit_quiz_attempt(token)
    
    # Test leaderboards
    test_leaderboards()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print(f"📖 API Documentation: {BASE_URL}/docs")
    print(f"📚 ReDoc: {BASE_URL}/redoc")
    print("\n💡 New Authentication Flow:")
    print("   1. Request OTP for your phone number")
    print("   2. Use OTP (123456) to login")
    print("   3. OTP expires in 10 minutes")
    print("   4. New OTP available daily")
    print("   5. Static OTP: 123456 (for testing)")

if __name__ == "__main__":
    main()
