"""
Emotion Detection Module with Error Handling
=============================================

This module provides emotion detection functionality using IBM Watson NLU API.
It includes comprehensive error handling for HTTP status code 400 (Bad Request).

Functions:
- emotion_detector(text): Detects emotions in text and returns a dictionary
- format_emotion_output(emotion_dict): Formats emotion dictionary for display

Author: Sondus1209
Version: 2.0 (Updated with error handling)
"""

import requests
import json
from typing import Dict, Optional, Any
from requests.exceptions import RequestException, Timeout, ConnectionError


# IBM Watson NLU API Configuration
WATSON_API_KEY = "YOUR_API_KEY_HERE"
WATSON_API_URL = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/YOUR_INSTANCE_ID/v1/analyze"
WATSON_API_VERSION = "2021-08-01"


def emotion_detector(text: str) -> Dict[str, Any]:
    """
    Function: emotion_detector
    
    Description:
    Analyzes text using IBM Watson Natural Language Understanding API
    to detect emotions (anger, disgust, fear, joy, sadness).
    
    Parameters:
    - text (str): The input text to analyze for emotions
    
    Returns:
    Dict with keys:
    - 'anger' (float): Anger emotion score (0-1)
    - 'disgust' (float): Disgust emotion score (0-1)
    - 'fear' (float): Fear emotion score (0-1)
    - 'joy' (float): Joy emotion score (0-1)
    - 'sadness' (float): Sadness emotion score (0-1)
    - 'dominant_emotion' (str): The emotion with highest score
    
    Error Handling:
    - Returns error dictionary with status code on API errors
    - Handles HTTP 400 (Bad Request) with descriptive messages
    - Handles connection errors and timeouts
    - Validates input before sending to API
    
    Raises:
    - ValueError: If text is None or empty string
    - RequestException: If API connection fails (caught and handled)
    """
    
    # ===== INPUT VALIDATION =====
    # Check if text is None
    if text is None:
        return {
            "error": "Invalid input",
            "message": "Text cannot be None",
            "status_code": 400,
            "dominant_emotion": None
        }
    
    # Check if text is empty string
    if isinstance(text, str) and text.strip() == "":
        return {
            "error": "Invalid input",
            "message": "Text cannot be empty string",
            "status_code": 400,
            "dominant_emotion": None
        }
    
    # Check if text is proper string type
    if not isinstance(text, str):
        return {
            "error": "Invalid input type",
            "message": f"Text must be a string, got {type(text).__name__}",
            "status_code": 400,
            "dominant_emotion": None
        }
    
    # Check text length (prevent abuse)
    if len(text) > 10000:
        return {
            "error": "Input too large",
            "message": "Text exceeds maximum length of 10000 characters",
            "status_code": 400,
            "dominant_emotion": None
        }
    
    # ===== API REQUEST PREPARATION =====
    try:
        # Prepare request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {WATSON_API_KEY}"
        }
        
        # Prepare request body
        request_body = {
            "text": text,
            "features": {
                "emotion": {}
            }
        }
        
        # Prepare request parameters
        params = {
            "version": WATSON_API_VERSION
        }
        
        # ===== API REQUEST EXECUTION =====
        response = requests.post(
            WATSON_API_URL,
            headers=headers,
            json=request_body,
            params=params,
            timeout=10  # 10 second timeout
        )
        
        # ===== ERROR HANDLING FOR HTTP 400 =====
        if response.status_code == 400:
            """
            HTTP 400 Bad Request Error Handling
            
            Possible causes:
            1. Invalid API key
            2. Missing required fields in request
            3. Invalid text format
            4. API rate limit exceeded
            5. Invalid request parameters
            """
            
            try:
                error_response = response.json()
                error_message = error_response.get('error', {})
                
                return {
                    "error": "Bad Request (400)",
                    "message": f"API returned 400 error: {error_message}",
                    "details": error_response,
                    "status_code": 400,
                    "dominant_emotion": None
                }
            except json.JSONDecodeError:
                # If response is not JSON
                return {
                    "error": "Bad Request (400)",
                    "message": "API returned 400 error with non-JSON response",
                    "response_text": response.text,
                    "status_code": 400,
                    "dominant_emotion": None
                }
        
        # ===== ERROR HANDLING FOR OTHER HTTP ERRORS =====
        if response.status_code == 401:
            return {
                "error": "Unauthorized (401)",
                "message": "Invalid API key or authentication failed",
                "status_code": 401,
                "dominant_emotion": None
            }
        
        if response.status_code == 403:
            return {
                "error": "Forbidden (403)",
                "message": "Access to this resource is forbidden",
                "status_code": 403,
                "dominant_emotion": None
            }
        
        if response.status_code == 429:
            return {
                "error": "Too Many Requests (429)",
                "message": "API rate limit exceeded",
                "status_code": 429,
                "dominant_emotion": None
            }
        
        if response.status_code == 500:
            return {
                "error": "Internal Server Error (500)",
                "message": "Watson API server error",
                "status_code": 500,
                "dominant_emotion": None
            }
        
        # Check for other non-2xx status codes
        if response.status_code < 200 or response.status_code >= 300:
            return {
                "error": f"HTTP Error {response.status_code}",
                "message": f"Unexpected response status code",
                "status_code": response.status_code,
                "dominant_emotion": None
            }
        
        # ===== SUCCESS RESPONSE HANDLING =====
        response_data = response.json()
        
        # Extract emotion scores
        emotions = response_data.get("emotion", {}).get("document", {}).get("emotion", {})
        
        # Validate emotion data
        if not emotions:
            return {
                "error": "Invalid response",
                "message": "No emotion data in API response",
                "status_code": 200,
                "dominant_emotion": None
            }
        
        # Extract individual emotion scores
        anger = emotions.get("anger", 0.0)
        disgust = emotions.get("disgust", 0.0)
        fear = emotions.get("fear", 0.0)
        joy = emotions.get("joy", 0.0)
        sadness = emotions.get("sadness", 0.0)
        
        # Determine dominant emotion
        emotion_scores = {
            "anger": anger,
            "disgust": disgust,
            "fear": fear,
            "joy": joy,
            "sadness": sadness
        }
        
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Return formatted response
        return {
            "anger": anger,
            "disgust": disgust,
            "fear": fear,
            "joy": joy,
            "sadness": sadness,
            "dominant_emotion": dominant_emotion
        }
    
    # ===== EXCEPTION HANDLING =====
    except Timeout:
        """
        Timeout Exception Handler
        API request took too long to respond
        """
        return {
            "error": "Request Timeout",
            "message": "API request timed out after 10 seconds",
            "status_code": 504,
            "dominant_emotion": None
        }
    
    except ConnectionError:
        """
        Connection Error Handler
        Cannot connect to API server
        """
        return {
            "error": "Connection Error",
            "message": "Failed to connect to Watson API server",
            "status_code": 503,
            "dominant_emotion": None
        }
    
    except RequestException as e:
        """
        General Request Exception Handler
        Other request-related errors
        """
        return {
            "error": "Request Error",
            "message": f"Request failed: {str(e)}",
            "status_code": 500,
            "dominant_emotion": None
        }
    
    except json.JSONDecodeError:
        """
        JSON Decode Error Handler
        Cannot parse API response as JSON
        """
        return {
            "error": "Invalid Response Format",
            "message": "API response is not valid JSON",
            "status_code": 500,
            "dominant_emotion": None
        }
    
    except KeyError as e:
        """
        Key Error Handler
        Missing expected key in API response
        """
        return {
            "error": "Invalid Response Structure",
            "message": f"Missing expected key in API response: {str(e)}",
            "status_code": 500,
            "dominant_emotion": None
        }
    
    except Exception as e:
        """
        General Exception Handler
        Catch-all for unexpected errors
        """
        return {
            "error": "Unexpected Error",
            "message": f"An unexpected error occurred: {str(e)}",
            "status_code": 500,
            "dominant_emotion": None
        }


def format_emotion_output(emotion_dict: Dict[str, Any]) -> str:
    """
    Function: format_emotion_output
    
    Description:
    Formats emotion detection results into a readable string format.
    
    Parameters:
    - emotion_dict (dict): Dictionary containing emotion scores
                          from emotion_detector() function
    
    Returns:
    str: Formatted emotion analysis results
    
    Examples:
    >>> result = emotion_detector("I am happy!")
    >>> output = format_emotion_output(result)
    >>> print(output)
    For the given text, the system predicts the following emotions:
    anger: 0.0
    disgust: 0.0
    fear: 0.0
    joy: 0.876
    sadness: 0.0
    Dominant emotion: joy
    """
    
    # Check for error in emotion_dict
    if not isinstance(emotion_dict, dict):
        return f"Error: Invalid input type. Expected dict, got {type(emotion_dict).__name__}"
    
    if "error" in emotion_dict:
        error_msg = emotion_dict.get("message", emotion_dict.get("error", "Unknown error"))
        return f"Error: {error_msg}"
    
    if "dominant_emotion" not in emotion_dict:
        return "Error: Missing 'dominant_emotion' in results"
    
    # Extract emotion scores
    anger = emotion_dict.get("anger", 0.0)
    disgust = emotion_dict.get("disgust", 0.0)
    fear = emotion_dict.get("fear", 0.0)
    joy = emotion_dict.get("joy", 0.0)
    sadness = emotion_dict.get("sadness", 0.0)
    dominant_emotion = emotion_dict.get("dominant_emotion", "unknown")
    
    # Format output string
    output = f"""For the given text, the system predicts the following emotions:
anger: {anger}
disgust: {disgust}
fear: {fear}
joy: {joy}
sadness: {sadness}
Dominant emotion: {dominant_emotion}"""
    
    return output


# ===== USAGE EXAMPLES =====
if __name__ == "__main__":
    """
    Example usage of emotion detection functions
    """
    
    print("=" * 70)
    print("Emotion Detection Module - Examples")
    print("=" * 70)
    
    # Example 1: Successful emotion detection
    print("\nExample 1: Successful emotion detection")
    print("-" * 70)
    text1 = "I am so happy and excited about this wonderful opportunity!"
    result1 = emotion_detector(text1)
    print(f"Input: {text1}")
    print(f"Output:\n{format_emotion_output(result1)}")
    
    # Example 2: Error handling - None input
    print("\n\nExample 2: Error handling - None input")
    print("-" * 70)
    result2 = emotion_detector(None)
    print(f"Input: None")
    print(f"Output: {format_emotion_output(result2)}")
    
    # Example 3: Error handling - Empty string
    print("\n\nExample 3: Error handling - Empty string")
    print("-" * 70)
    result3 = emotion_detector("")
    print(f"Input: (empty string)")
    print(f"Output: {format_emotion_output(result3)}")
    
    # Example 4: Error handling - Invalid type
    print("\n\nExample 4: Error handling - Invalid type")
    print("-" * 70)
    result4 = emotion_detector(12345)
    print(f"Input: 12345 (int)")
    print(f"Output: {format_emotion_output(result4)}")
    
    # Example 5: Error handling - Text too long
    print("\n\nExample 5: Error handling - Text too long")
    print("-" * 70)
    long_text = "a" * 10001
    result5 = emotion_detector(long_text)
    print(f"Input: (text with 10001 characters)")
    print(f"Output: {format_emotion_output(result5)}")
    
    print("\n" + "=" * 70)
    print("Error Handling Summary:")
    print("=" * 70)
    print("✓ HTTP 400 (Bad Request) - API returns 400 error")
    print("✓ HTTP 401 (Unauthorized) - Invalid API key")
    print("✓ HTTP 403 (Forbidden) - Access denied")
    print("✓ HTTP 429 (Too Many Requests) - Rate limit exceeded")
    print("✓ HTTP 500+ - Server errors")
    print("✓ Input Validation - None, empty, invalid type, length checks")
    print("✓ Connection Errors - Timeout, connection failure")
    print("✓ JSON Parsing - Invalid JSON response")
    print("✓ Missing Keys - Invalid response structure")
    print("=" * 70)
