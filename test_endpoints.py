#!/usr/bin/env python3
"""
Test script for Multi-Agent Custom Automation Engine API endpoints.
This script tests all available endpoints using the data from a successful plan creation.
"""

import requests
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "https://cpo-acrasalesanalytics.jollyfield-479bc951.eastus2.azurecontainerapps.io"

# Test data from successful request
TEST_SESSION_ID = "brokoomaa222"
TEST_PLAN_ID = "46721fd4-0d3f-4eb9-bc52-a88a008124c5"
TEST_DESCRIPTION = "Onboard a new employee, Rico Primo"

def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> requests.Response:
    """Make a request to the API with proper headers."""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def test_endpoint(name: str, method: str, endpoint: str, data: Dict[Any, Any] = None, params: Dict[str, str] = None):
    """Test a single endpoint and print results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method}")
    print(f"Endpoint: {endpoint}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    if params:
        print(f"Params: {params}")
    print(f"{'='*60}")
    
    response = make_request(method, endpoint, data, params)
    
    if response is None:
        print("❌ Request failed - No response")
        return None
    
    print(f"Status Code: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
        
        if 200 <= response.status_code < 300:
            print("✅ Test PASSED")
            return response_json
        else:
            print("❌ Test FAILED")
            return None
    except json.JSONDecodeError:
        print(f"Response Text: {response.text}")
        if 200 <= response.status_code < 300:
            print("✅ Test PASSED (non-JSON response)")
            return response.text
        else:
            print("❌ Test FAILED")
            return None

def main():
    """Main test function."""
    print("🚀 Starting API Endpoint Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Health check (if available)
    test_endpoint(
        "Health Check",
        "GET",
        "/health"
    )
    
    # Test 2: Get all plans
    plans_response = test_endpoint(
        "Get All Plans",
        "GET",
        "/api/plans"
    )
    
    # Test 3: Get plans by session ID
    test_endpoint(
        "Get Plans by Session ID",
        "GET",
        "/api/plans",
        params={"session_id": TEST_SESSION_ID}
    )
    
    # Test 4: Get steps for the plan
    test_endpoint(
        "Get Steps by Plan ID",
        "GET",
        f"/api/steps/{TEST_PLAN_ID}"
    )
    
    # Test 5: Get agent messages for session
    test_endpoint(
        "Get Agent Messages by Session",
        "GET",
        f"/api/agent_messages/{TEST_SESSION_ID}"
    )
    
    # Test 6: Get all messages
    test_endpoint(
        "Get All Messages",
        "GET",
        "/api/messages"
    )
    
    # Test 7: Get agent tools
    test_endpoint(
        "Get Agent Tools",
        "GET",
        "/api/agent-tools"
    )
    
    # Test 8: Human feedback (assuming we have steps to provide feedback on)
    if plans_response and isinstance(plans_response, list) and len(plans_response) > 0:
        plan = plans_response[0]
        if 'steps' in plan and len(plan['steps']) > 0:
            step_id = plan['steps'][0]['id']
            
            test_endpoint(
                "Submit Human Feedback",
                "POST",
                "/api/human_feedback",
                data={
                    "step_id": step_id,
                    "plan_id": TEST_PLAN_ID,
                    "session_id": TEST_SESSION_ID,
                    "approved": True,
                    "human_feedback": "This step looks good, please proceed.",
                    "updated_action": "",
                    "user_id": "test-user"
                }
            )
    
    # Test 9: Human clarification on plan
    test_endpoint(
        "Submit Human Clarification",
        "POST",
        "/api/human_clarification_on_plan",
        data={
            "plan_id": TEST_PLAN_ID,
            "session_id": TEST_SESSION_ID,
            "human_clarification": "Please provide more details on the onboarding process timeline.",
            "user_id": "test-user"
        }
    )
    
    # Test 10: Approve step(s)
    test_endpoint(
        "Approve Steps",
        "POST",
        "/api/approve_step_or_steps",
        data={
            "plan_id": TEST_PLAN_ID,
            "session_id": TEST_SESSION_ID,
            "approved": True,
            "human_feedback": "All steps approved for execution.",
            "user_id": "test-user"
        }
    )
    
    # Test 11: Create another input task for testing
    test_endpoint(
        "Create Another Input Task",
        "POST",
        "/api/input_task",
        data={
            "session_id": "test-session-2",
            "description": "Schedule a team meeting for next week"
        }
    )
    
    print(f"\n{'='*60}")
    print("🎉 All tests completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
