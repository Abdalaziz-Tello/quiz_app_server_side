#!/usr/bin/env python3
"""
Database initialization script for Quiz App - IP-Based Authentication
This script adds sample questions and creates test data
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def get_client_ip():
    """Get client IP address (simulated)"""
    # In a real scenario, this would be the actual client IP
    # For testing, we'll use a simulated IP
    return "192.168.1.100"

def request_otp():
    """Request OTP for testing"""
    print("Requesting OTP...")
    
    otp_request = {
        "ip_address": get_client_ip(),
        "device_id": "init_device_001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/request-otp", json=otp_request)
        if response.status_code == 200:
            otp_data = response.json()
            print(f"✅ OTP received: {otp_data['otp_code']}")
            return otp_data['otp_code']
        else:
            print(f"❌ OTP request failed: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def create_test_user():
    """Create a test user if it doesn't exist"""
    print("Creating test user...")
    
    user_data = {
        "nickname": "AdminUser",
        "device_id": "init_device_001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        if response.status_code == 200:
            print("✅ Test user created successfully!")
            return response.json()
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  Test user already exists")
            return None
        else:
            print(f"❌ Failed to create test user: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def login_user(otp_code):
    """Login and get JWT token"""
    print("Logging in as admin...")
    
    login_data = {
        "ip_address": get_client_ip(),
        "otp_code": otp_code
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful!")
            token_data = response.json()
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return None

def create_sample_questions(token):
    """Create sample quiz questions"""
    print("Creating sample questions...")
    
    sample_questions = [
        {
            "question_text": "What is the capital of France?",
            "option_a": "London",
            "option_b": "Paris",
            "option_c": "Berlin",
            "option_d": "Madrid",
            "correct_answer": "B",
            "points": 10,
            "time_limit": 30
        },
        {
            "question_text": "Which planet is known as the Red Planet?",
            "option_a": "Venus",
            "option_b": "Mars",
            "option_c": "Jupiter",
            "option_d": "Saturn",
            "correct_answer": "B",
            "points": 15,
            "time_limit": 25
        },
        {
            "question_text": "What is the largest mammal in the world?",
            "option_a": "African Elephant",
            "option_b": "Blue Whale",
            "option_c": "Giraffe",
            "option_d": "Hippopotamus",
            "correct_answer": "B",
            "points": 20,
            "time_limit": 20
        },
        {
            "question_text": "Who wrote 'Romeo and Juliet'?",
            "option_a": "Charles Dickens",
            "option_b": "William Shakespeare",
            "option_c": "Jane Austen",
            "option_d": "Mark Twain",
            "correct_answer": "B",
            "points": 12,
            "time_limit": 35
        },
        {
            "question_text": "What is the chemical symbol for gold?",
            "option_a": "Ag",
            "option_b": "Fe",
            "option_c": "Au",
            "option_d": "Cu",
            "correct_answer": "C",
            "points": 8,
            "time_limit": 15
        },
        {
            "question_text": "Which year did World War II end?",
            "option_a": "1943",
            "option_b": "1944",
            "option_c": "1945",
            "option_d": "1946",
            "correct_answer": "C",
            "points": 18,
            "time_limit": 40
        },
        {
            "question_text": "What is the largest ocean on Earth?",
            "option_a": "Atlantic Ocean",
            "option_b": "Indian Ocean",
            "option_c": "Arctic Ocean",
            "option_d": "Pacific Ocean",
            "correct_answer": "D",
            "points": 14,
            "time_limit": 25
        },
        {
            "question_text": "Who painted the Mona Lisa?",
            "option_a": "Vincent van Gogh",
            "option_b": "Pablo Picasso",
            "option_c": "Leonardo da Vinci",
            "option_d": "Michelangelo",
            "correct_answer": "C",
            "points": 16,
            "time_limit": 30
        },
        {
            "question_text": "What is the square root of 144?",
            "option_a": "10",
            "option_b": "11",
            "option_c": "12",
            "option_d": "13",
            "correct_answer": "C",
            "points": 6,
            "time_limit": 20
        },
        {
            "question_text": "Which country is home to the kangaroo?",
            "option_a": "New Zealand",
            "option_b": "South Africa",
            "option_c": "Australia",
            "option_d": "India",
            "correct_answer": "C",
            "points": 11,
            "time_limit": 25
        }
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    created_count = 0
    
    for i, question_data in enumerate(sample_questions, 1):
        try:
            response = requests.post(f"{BASE_URL}/questions", json=question_data, headers=headers)
            if response.status_code == 200:
                print(f"✅ Question {i} created: {question_data['question_text'][:50]}...")
                created_count += 1
            else:
                print(f"❌ Failed to create question {i}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure the server is running.")
            break
    
    print(f"\n📊 Created {created_count} out of {len(sample_questions)} questions")

def submit_sample_quiz_attempts(token):
    """Submit some sample quiz attempts for leaderboard testing"""
    print("Submitting sample quiz attempts...")
    
    sample_attempts = [
        {"score": 95, "total_points": 150, "time_taken": 420},
        {"score": 87, "total_points": 150, "time_taken": 380},
        {"score": 92, "total_points": 150, "time_taken": 450},
        {"score": 78, "total_points": 150, "time_taken": 320},
        {"score": 89, "total_points": 150, "time_taken": 410}
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    submitted_count = 0
    
    for i, attempt_data in enumerate(sample_attempts, 1):
        try:
            response = requests.post(f"{BASE_URL}/quiz-attempt", json=attempt_data, headers=headers)
            if response.status_code == 200:
                print(f"✅ Quiz attempt {i} submitted: Score {attempt_data['score']}/{attempt_data['total_points']}")
                submitted_count += 1
            else:
                print(f"❌ Failed to submit quiz attempt {i}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure the server is running.")
            break
    
    print(f"\n📊 Submitted {submitted_count} out of {len(sample_attempts)} quiz attempts")

def main():
    """Main initialization function"""
    print("🚀 Quiz App Database Initialization - IP-Based Authentication")
    print("=" * 60)
    
    # Wait a moment for server to start
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Request OTP
    otp_code = request_otp()
    if not otp_code:
        print("❌ Cannot continue without OTP")
        return
    
    # Create test user
    user = create_test_user()
    
    # Login to get token
    token = login_user(otp_code)
    if not token:
        print("❌ Cannot continue without authentication token")
        return
    
    # Create sample questions
    create_sample_questions(token)
    
    # Submit sample quiz attempts
    submit_sample_quiz_attempts(token)
    
    print("\n" + "=" * 60)
    print("🎉 Database initialization completed!")
    print("📖 You can now test the API with the sample data")
    print(f"🔗 API Documentation: {BASE_URL}/docs")
    print("\n💡 New Authentication Flow:")
    print("   1. Request OTP for your IP address")
    print("   2. Use OTP to login (no password needed!)")
    print("   3. OTP expires in 10 minutes")
    print("   4. New OTP available daily")

if __name__ == "__main__":
    main()
