"""
Flask Web Server with Error Handling for Blank Input
=====================================================

This module implements a Flask web server that demonstrates comprehensive
error handling for blank input and invalid requests in the emotion detection
application.

Features:
- Blank input validation and error handling
- Empty string detection
- Whitespace-only input handling
- Comprehensive error messages
- HTTP 400 status codes for invalid input
- Request validation middleware
- User-friendly error responses

Author: Sondus1209
Version: 2.0 (Error Handling Focus)
"""

from flask import Flask, request, render_template, jsonify
from emotion_detection import emotion_detector, format_emotion_output
import sys
import logging

# Initialize Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS (Cross-Origin Resource Sharing) if needed
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    pass


# ===== INPUT VALIDATION UTILITIES =====
def validate_text_input(text):
    """
    Function: validate_text_input
    
    Description:
    Validates text input for emotion detection.
    Checks for blank, empty, None, and whitespace-only inputs.
    
    Parameters:
    - text (str): The text to validate
    
    Returns:
    - tuple: (is_valid, error_message)
      - is_valid (bool): True if text is valid, False otherwise
      - error_message (str): Descriptive error message if invalid
    
    Examples:
    >>> validate_text_input("")
    (False, "Text cannot be blank")
    
    >>> validate_text_input("   ")
    (False, "Text cannot be whitespace only")
    
    >>> validate_text_input(None)
    (False, "Text cannot be None")
    
    >>> validate_text_input("Valid text")
    (True, "")
    """
    
    # Check for None
    if text is None:
        return False, "Text cannot be None. Please provide valid text input."
    
    # Check for empty string
    if isinstance(text, str) and len(text) == 0:
        return False, "Text cannot be blank. Please provide some text for emotion detection."
    
    # Check for whitespace-only string
    if isinstance(text, str) and text.strip() == "":
        return False, "Text cannot be whitespace only. Please provide meaningful text content."
    
    # Check for proper type
    if not isinstance(text, str):
        return False, f"Text must be a string. Received: {type(text).__name__}"
    
    # Check for minimum length (at least 1 character after stripping)
    if len(text.strip()) == 0:
        return False, "Text must contain at least one non-whitespace character."
    
    # Check for maximum length
    if len(text) > 5000:
        return False, "Text exceeds maximum length of 5000 characters."
    
    # All validation passed
    return True, ""


@app.route('/')
def index():
    """
    Route: GET /
    Description: Renders the home page with emotion detection form
    Returns: HTML template with the web interface
    """
    logger.info("Home page requested")
    return render_template('index.html')


@app.route('/api/emotion', methods=['POST'])
def detect_emotion():
    """
    Route: POST /api/emotion
    
    Description:
    API endpoint for emotion detection with comprehensive error handling
    for blank input and invalid requests.
    
    Request Body (JSON):
    {
        "text": "The text to analyze for emotions"
    }
    
    Response on Success (JSON):
    {
        "anger": 0.0,
        "disgust": 0.0,
        "fear": 0.0,
        "joy": 0.876,
        "sadness": 0.0,
        "dominant_emotion": "joy"
    }
    
    Response on Blank Input (JSON - HTTP 400):
    {
        "error": "Blank Input",
        "message": "Text cannot be blank. Please provide some text for emotion detection.",
        "status_code": 400
    }
    
    Response on Missing Field (JSON - HTTP 400):
    {
        "error": "Missing Field",
        "message": "Missing 'text' field in request body. Please include text data.",
        "status_code": 400
    }
    
    Response on Invalid JSON (JSON - HTTP 400):
    {
        "error": "Invalid JSON",
        "message": "Request body must be valid JSON.",
        "status_code": 400
    }
    
    Status Codes:
    - 200: Success - emotions detected
    - 400: Bad Request - blank input, missing field, or invalid format
    - 500: Server Error - internal processing error
    """
    
    logger.info("Emotion detection API called")
    
    try:
        # ===== STEP 1: VALIDATE CONTENT TYPE =====
        if not request.is_json:
            logger.warning("Request is not JSON")
            return jsonify({
                "error": "Invalid Content-Type",
                "message": "Request must have Content-Type: application/json",
                "status_code": 400
            }), 400
        
        # ===== STEP 2: PARSE JSON =====
        try:
            data = request.get_json()
            logger.info(f"Received JSON data: {type(data)}")
        except Exception as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return jsonify({
                "error": "Invalid JSON",
                "message": "Request body must be valid JSON. Please check your JSON syntax.",
                "details": str(e),
                "status_code": 400
            }), 400
        
        # ===== STEP 3: CHECK FOR NULL DATA =====
        if data is None:
            logger.warning("Received null JSON data")
            return jsonify({
                "error": "Empty Request",
                "message": "Request body is empty. Please provide JSON data with 'text' field.",
                "status_code": 400
            }), 400
        
        # ===== STEP 4: CHECK FOR MISSING 'text' FIELD =====
        if 'text' not in data:
            logger.warning("Missing 'text' field in request")
            return jsonify({
                "error": "Missing Field",
                "message": "Missing 'text' field in request body. Please include text data.",
                "received_fields": list(data.keys()),
                "status_code": 400
            }), 400
        
        # ===== STEP 5: EXTRACT TEXT =====
        text = data.get('text')
        logger.info(f"Text received (type: {type(text).__name__}, length: {len(str(text)) if text else 0})")
        
        # ===== STEP 6: VALIDATE TEXT INPUT (BLANK HANDLING) =====
        is_valid, error_message = validate_text_input(text)
        
        if not is_valid:
            logger.warning(f"Input validation failed: {error_message}")
            return jsonify({
                "error": "Blank Input" if text == "" or text is None else "Invalid Input",
                "message": error_message,
                "status_code": 400
            }), 400
        
        # ===== STEP 7: PROCESS EMOTION DETECTION =====
        logger.info("Processing emotion detection")
        result = emotion_detector(text)
        
        # ===== STEP 8: CHECK FOR EMOTION DETECTION ERRORS =====
        if result is None or 'dominant_emotion' not in result:
            logger.error("Emotion detection returned None or missing dominant_emotion")
            return jsonify({
                "error": "Detection Error",
                "message": "Failed to detect emotions from the provided text",
                "status_code": 500
            }), 500
        
        # Check if emotion_detector returned an error
        if "error" in result:
            logger.warning(f"Emotion detector returned error: {result.get('message')}")
            return jsonify(result), result.get('status_code', 500)
        
        # ===== STEP 9: RETURN SUCCESS RESPONSE =====
        logger.info(f"Emotion detection successful. Dominant emotion: {result.get('dominant_emotion')}")
        return jsonify(result), 200
    
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        return jsonify({
            "error": "Validation Error",
            "message": f"Invalid input: {str(e)}",
            "status_code": 400
        }), 400
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }), 500


@app.route('/api/emotion/formatted', methods=['POST'])
def detect_emotion_formatted():
    """
    Route: POST /api/emotion/formatted
    
    Description:
    API endpoint for emotion detection with formatted text output.
    Includes comprehensive error handling for blank input.
    
    Request Body (JSON):
    {
        "text": "The text to analyze for emotions"
    }
    
    Response on Success (Plain Text):
    For the given text, the system predicts the following emotions:
    anger: 0.0
    disgust: 0.0
    fear: 0.0
    joy: 0.876
    sadness: 0.0
    Dominant emotion: joy
    
    Response on Blank Input (Plain Text - HTTP 400):
    Error: Text cannot be blank. Please provide some text for emotion detection.
    
    Status Codes:
    - 200: Success - emotions detected and formatted
    - 400: Bad Request - blank input or invalid format
    - 500: Server Error - internal processing error
    """
    
    logger.info("Formatted emotion detection API called")
    
    try:
        # Validate content type
        if not request.is_json:
            logger.warning("Request is not JSON (formatted endpoint)")
            return "Error: Request must have Content-Type: application/json", 400
        
        # Parse JSON
        try:
            data = request.get_json()
        except Exception as e:
            logger.error(f"JSON parsing error (formatted): {str(e)}")
            return f"Error: Invalid JSON - {str(e)}", 400
        
        # Check for null data
        if data is None:
            logger.warning("Received null JSON data (formatted)")
            return "Error: Request body is empty. Please provide JSON with 'text' field.", 400
        
        # Check for missing text field
        if 'text' not in data:
            logger.warning("Missing 'text' field (formatted)")
            return "Error: Missing 'text' field in request body.", 400
        
        # Extract text
        text = data.get('text')
        logger.info(f"Text received (formatted endpoint, length: {len(str(text)) if text else 0})")
        
        # Validate text input (blank handling)
        is_valid, error_message = validate_text_input(text)
        
        if not is_valid:
            logger.warning(f"Input validation failed (formatted): {error_message}")
            return f"Error: {error_message}", 400
        
        # Process emotion detection
        logger.info("Processing emotion detection (formatted)")
        result = emotion_detector(text)
        
        # Format and return output
        formatted_output = format_emotion_output(result)
        logger.info("Formatted output generated")
        
        return formatted_output, 200
    
    except Exception as e:
        logger.error(f"Unexpected error (formatted): {str(e)}")
        return f"Error: Internal server error - {str(e)}", 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Route: GET /health
    Description: Health check endpoint for monitoring
    Returns: JSON with server status
    """
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "service": "Emotion Detection Server",
        "version": "2.0",
        "features": [
            "Blank input error handling",
            "Empty string detection",
            "Whitespace validation",
            "Comprehensive logging"
        ]
    }), 200


@app.route('/api/info', methods=['GET'])
def api_info():
    """
    Route: GET /api/info
    Description: Returns API documentation and available endpoints
    Returns: JSON with API information and error handling details
    """
    logger.info("API info requested")
    return jsonify({
        "api_version": "2.0",
        "service": "Emotion Detection API with Error Handling",
        "error_handling": {
            "blank_input": "HTTP 400 - Text cannot be blank",
            "empty_string": "HTTP 400 - Text cannot be empty string",
            "whitespace_only": "HTTP 400 - Text cannot be whitespace only",
            "missing_field": "HTTP 400 - Missing 'text' field",
            "invalid_json": "HTTP 400 - Invalid JSON format",
            "invalid_type": "HTTP 400 - Text must be string",
            "length_exceeded": "HTTP 400 - Text exceeds maximum length",
            "server_error": "HTTP 500 - Internal server error"
        },
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "Home page with web interface"
            },
            {
                "path": "/api/emotion",
                "method": "POST",
                "description": "Detect emotions from text (JSON response)",
                "error_handling": "Comprehensive blank input validation",
                "request": {
                    "format": "JSON",
                    "body": {
                        "text": "string - text to analyze (required, non-blank)"
                    }
                },
                "response": {
                    "format": "JSON",
                    "body": {
                        "anger": "float (0-1)",
                        "disgust": "float (0-1)",
                        "fear": "float (0-1)",
                        "joy": "float (0-1)",
                        "sadness": "float (0-1)",
                        "dominant_emotion": "string"
                    }
                },
                "status_codes": {
                    "200": "Success",
                    "400": "Blank/invalid input",
                    "500": "Server error"
                }
            },
            {
                "path": "/api/emotion/formatted",
                "method": "POST",
                "description": "Detect emotions from text (formatted text response)",
                "error_handling": "Comprehensive blank input validation",
                "request": {
                    "format": "JSON",
                    "body": {
                        "text": "string - text to analyze (required, non-blank)"
                    }
                },
                "response": {
                    "format": "Plain Text",
                    "body": "Formatted emotion analysis results"
                },
                "status_codes": {
                    "200": "Success",
                    "400": "Blank/invalid input",
                    "500": "Server error"
                }
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            },
            {
                "path": "/api/info",
                "method": "GET",
                "description": "API documentation and available endpoints"
            }
        ]
    }), 200


@app.errorhandler(400)
def bad_request(error):
    """
    Error Handler: 400 Bad Request
    Description: Handles bad requests including blank input errors
    """
    logger.warning(f"400 Bad Request: {str(error)}")
    return jsonify({
        "error": "Bad Request",
        "message": "The request could not be processed. Please check your input.",
        "status_code": 400
    }), 400


@app.errorhandler(404)
def not_found(error):
    """
    Error Handler: 404 Not Found
    Description: Handles requests to non-existent endpoints
    """
    logger.warning(f"404 Not Found: {str(error)}")
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested resource does not exist. Use GET /api/info for available endpoints.",
        "status_code": 404
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """
    Error Handler: 405 Method Not Allowed
    Description: Handles requests with incorrect HTTP method
    """
    logger.warning(f"405 Method Not Allowed: {str(error)}")
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method used is not allowed for this endpoint.",
        "status_code": 405
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """
    Error Handler: 500 Internal Server Error
    Description: Handles internal server errors
    """
    logger.error(f"500 Internal Server Error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred on the server.",
        "status_code": 500
    }), 500


def run_server(debug=False, host='0.0.0.0', port=5000):
    """
    Function: run_server
    
    Description:
    Starts the Flask development/production server with error handling.
    
    Parameters:
    - debug (bool): Enable debug mode (default: False)
    - host (str): Server host address (default: '0.0.0.0')
    - port (int): Server port number (default: 5000)
    
    Usage:
    >>> run_server(debug=True, port=5000)
    """
    print("=" * 80)
    print("Emotion Detection Web Server - Error Handling Version")
    print("=" * 80)
    print(f"Starting Flask server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug Mode: {debug}")
    print(f"Environment: {'Development' if debug else 'Production'}")
    print("=" * 80)
    print("\nAvailable Endpoints:")
    print("  GET  /                      - Home page with web interface")
    print("  POST /api/emotion           - Detect emotions (JSON response)")
    print("  POST /api/emotion/formatted - Detect emotions (text response)")
    print("  GET  /health                - Health check endpoint")
    print("  GET  /api/info              - API documentation")
    print("\n" + "=" * 80)
    print("Error Handling Features:")
    print("=" * 80)
    print("✓ Blank input validation")
    print("✓ Empty string detection")
    print("✓ Whitespace-only input handling")
    print("✓ Missing field validation")
    print("✓ Invalid JSON detection")
    print("✓ Type validation")
    print("✓ Length validation")
    print("✓ Comprehensive logging")
    print("✓ HTTP 400 status codes for invalid input")
    print("=" * 80 + "\n")
    
    app.run(debug=debug, host=host, port=port, use_reloader=debug)


if __name__ == '__main__':
    """
    Main Entry Point
    
    Usage:
    - Development mode: python server.py
    - Production mode: python server.py --no-debug
    - Custom port: python server.py --port 8080
    - Custom host: python server.py --host localhost
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Emotion Detection Web Server with Error Handling')
    parser.add_argument('--debug', action='store_true', default=True,
                       help='Enable debug mode (default: True)')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                       help='Disable debug mode')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Server port (default: 5000)')
    
    args = parser.parse_args()
    
    # Start the server
    run_server(debug=args.debug, host=args.host, port=args.port)
