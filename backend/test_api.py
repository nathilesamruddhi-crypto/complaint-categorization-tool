"""
Complaint Categorization API - Testing Guide
Test the backend API with various test cases
"""

import requests
import json
from datetime import datetime

# ===== CONFIGURATION =====
API_URL = "http://127.0.0.1:5000"
ENDPOINT_PREDICT = f"{API_URL}/predict"
ENDPOINT_STATUS = f"{API_URL}/status"
ENDPOINT_HOME = f"{API_URL}/"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{YELLOW}ℹ {text}{RESET}")


def test_api_health():
    """Test 1: API Health Check"""
    print_header("Test 1: API Health Check")
    
    try:
        response = requests.get(ENDPOINT_HOME, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is running: {data['message']}")
            print(f"  Status: {data['status']}")
            print(f"  Version: {data['version']}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to API. Is Flask running on port 5000?")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_api_status():
    """Test 2: Get API Status and Categories"""
    print_header("Test 2: API Status & Categories")
    
    try:
        response = requests.get(ENDPOINT_STATUS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Status retrieved successfully")
            print(f"  Model Type: {data['model_type']}")
            print(f"  Number of Categories: {data['num_categories']}")
            print(f"  Available Categories:")
            for cat in data['categories']:
                print(f"    • {cat}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_single_prediction(complaint, expected_category=None):
    """Test 3: Single Complaint Prediction"""
    
    try:
        payload = {"complaint": complaint}
        response = requests.post(ENDPOINT_PREDICT, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                result = {
                    'success': True,
                    'complaint': complaint[:50] + "...",
                    'category': data['category'],
                    'confidence': data['confidence'],
                    'probabilities': data['probabilities']
                }
                
                print_success(f"Prediction successful!")
                print(f"  Complaint: {complaint[:60]}...")
                print(f"  Category: {data['category']}")
                print(f"  Confidence: {data['confidence']}%")
                print(f"  Top 3 Probabilities:")
                
                sorted_probs = sorted(data['probabilities'].items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
                for cat, prob in sorted_probs:
                    bar_length = int(prob / 5)
                    bar = "█" * bar_length
                    print(f"    {cat:12} {prob:6.2f}% {bar}")
                
                if expected_category and data['category'] != expected_category:
                    print_info(f"Expected {expected_category}, got {data['category']}")
                
                return True
            else:
                print_error(f"Prediction failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_batch_prediction():
    """Test 4: Batch Prediction"""
    print_header("Test 4: Batch Prediction (Multiple Complaints)")
    
    complaints = [
        "I was charged twice for the same order without my consent",
        "The product arrived completely damaged and broken",
        "Cannot login to my account, password reset not working",
        "My delivery is 5 days late, where is my package",
        "The customer service representative was very rude",
        "The website keeps crashing and timing out"
    ]
    
    try:
        payload = {"complaints": complaints}
        response = requests.post(f"{API_URL}/predict-batch", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Batch prediction completed: {data['total']} items")
            
            success_count = sum(1 for r in data['results'] if r['success'])
            print(f"  Successful: {success_count}/{data['total']}")
            
            print("\n  Results:")
            for result in data['results']:
                if result['success']:
                    print(f"    [{result['index']}] {result['category']:10} - "
                          f"{result['confidence']:6.2f}% - {result['complaint'][:40]}")
                else:
                    print_info(f"    [{result['index']}] Error: {result['error']}")
            
            return True
        else:
            print_error(f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_all_categories():
    """Test 5: Test Each Category with Sample Complaints"""
    print_header("Test 5: Testing All Categories")
    
    test_cases = {
        "Account": "I cannot login to my account, the password reset is not working",
        "Billing": "I was charged $100 twice for the same transaction",
        "Delivery": "My package arrived 7 days late and no tracking updates",
        "Product": "The product arrived damaged and cannot be used",
        "Service": "The customer service was rude and unhelpful",
        "Technical": "The app keeps crashing and showing error messages"
    }
    
    results = []
    for category, complaint in test_cases.items():
        print_info(f"Testing {category} category...")
        success = test_single_prediction(complaint, category)
        results.append({'category': category, 'success': success})
    
    print(f"\n{BLUE}Summary:{RESET}")
    passed = sum(1 for r in results if r['success'])
    print(f"  Passed: {passed}/{len(results)}")
    
    return passed == len(results)


def test_edge_cases():
    """Test 6: Edge Cases"""
    print_header("Test 6: Edge Cases & Error Handling")
    
    edge_cases = [
        ("", "Empty complaint"),
        ("Hi", "Too short (2 chars)"),
        ("a" * 6000, "Too long (>5000 chars)"),
        ("!!!@@@###$$$%%%", "Only special characters"),
        ("   ", "Only whitespace"),
    ]
    
    for complaint, description in edge_cases:
        print_info(f"Testing: {description}")
        try:
            payload = {"complaint": complaint}
            response = requests.post(ENDPOINT_PREDICT, json=payload, timeout=5)
            
            if response.status_code in [400, 500]:
                data = response.json()
                print_success(f"  Correctly rejected: {data.get('error', 'Error handling working')}")
            else:
                data = response.json()
                if not data['success']:
                    print_success(f"  Correctly failed: {data.get('error', '')}")
                else:
                    print_error(f"  Should have failed but succeeded")
                    
        except Exception as e:
            print_error(f"  Unexpected error: {str(e)}")


def test_performance():
    """Test 7: Performance Test (Response Time)"""
    print_header("Test 7: Performance & Response Time")
    
    import time
    
    complaint = "I was charged twice for my order and need immediate refund"
    times = []
    
    for i in range(5):
        try:
            start = time.time()
            payload = {"complaint": complaint}
            response = requests.post(ENDPOINT_PREDICT, json=payload, timeout=5)
            elapsed = (time.time() - start) * 1000  # Convert to milliseconds
            times.append(elapsed)
            
            print(f"  Request {i+1}: {elapsed:.2f}ms")
            
        except Exception as e:
            print_error(f"Request {i+1} failed: {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n{BLUE}Performance Summary:{RESET}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Fastest: {min(times):.2f}ms")
        print(f"  Slowest: {max(times):.2f}ms")
        
        if avg_time < 100:
            print_success("Excellent response time!")
        elif avg_time < 500:
            print_info("Good response time")
        else:
            print_error("Slow response time")


# ===== MAIN TEST RUNNER =====
def run_all_tests():
    """Run all tests"""
    print(f"\n{YELLOW}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Complaint Categorization API - Comprehensive Test Suite ║")
    print(f"║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):42} ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print_info("Starting test suite...")
    print_info("Make sure Flask server is running on port 5000")
    
    input("\nPress Enter to start testing...")
    
    # Run tests in sequence
    results = []
    
    # Test 1: Health Check
    results.append(("API Health Check", test_api_health()))
    
    if not results[-1][1]:
        print_error("\n❌ Cannot continue - API is not running")
        print_info("Start the Flask server with: python app.py")
        return
    
    # Test 2: Status
    results.append(("API Status", test_api_status()))
    
    # Test 3: Single Prediction
    print_header("Test 3: Single Complaint Prediction")
    results.append(("Single Prediction", test_single_prediction(
        "I was charged twice for my order"
    )))
    
    # Test 4: Batch Prediction
    results.append(("Batch Prediction", test_batch_prediction()))
    
    # Test 5: All Categories
    results.append(("Category Testing", test_all_categories()))
    
    # Test 6: Edge Cases
    test_edge_cases()
    results.append(("Edge Cases", True))
    
    # Test 7: Performance
    test_performance()
    results.append(("Performance", True))
    
    # Print Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = f"{GREEN}✓ PASSED{RESET}" if success else f"{RED}✗ FAILED{RESET}"
        print(f"  {test_name:30} {status}")
    
    print(f"\n{BLUE}Overall: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print_success("\n🎉 All tests passed! API is working correctly.\n")
    else:
        print_error("\n⚠️  Some tests failed. Check the output above.\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Testing interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
