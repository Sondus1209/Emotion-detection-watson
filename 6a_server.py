"""
Flask Web Application for Emotion Detection
============================================

This module implements a Flask web server that provides:
- A home page with an HTML form for emotion detection
- A REST API endpoint for processing text and detecting emotions
- Integration with the emotion_detection module for NLP analysis
- Error handling and validation for user inputs
- JSON response formatting for API clients

Author: Sondus1209
Version: 1.0
"""

from flask import Flask, request, render_template, jsonify
from emotion_detection import emotion_detector, format_emotion_output
import sys

# Initialize Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS (Cross-Origin Resource Sharing) if needed
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    pass  # CORS not required for basic functionality


@app.route('/')
def index():
    """
    Route: GET /
    Description: Renders the home page with emotion detection form
    Returns: HTML template with the web interface
    """
    return render_template('index.html')


@app.route('/api/emotion', methods=['POST'])
def detect_emotion():
    """
    Route: POST /api/emotion
    Description: API endpoint for emotion detection
    
    Request Body (JSON):
    {
        "text": "The text to analyze for emotions"
    }
    
    Response (JSON):
    {
        "anger": 0.0,
        "disgust": 0.0,
        "fear": 0.0,
        "joy": 0.876,
        "sadness": 0.0,
        "dominant_emotion": "joy"
    }
    
    Error Response (JSON):
    {
        "error": "Invalid request or missing text field"
    }
    
    Status Codes:
    - 200: Success - emotions detected
    - 400: Bad Request - missing or invalid input
    - 500: Server Error - internal processing error
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                "error": "Invalid request format. Please send JSON data with Content-Type: application/json"
            }), 400
        
        # Get JSON data from request
        data = request.get_json()
        
        # Validate request body contains 'text' field
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request body"
            }), 400
        
        # Extract and validate text
        text = data.get('text', '').strip()
        
        # Check if text is empty
        if not text:
            return jsonify({
                "error": "Text field cannot be empty"
            }), 400
        
        # Validate text length (optional - prevent abuse)
        if len(text) > 5000:
            return jsonify({
                "error": "Text exceeds maximum length of 5000 characters"
            }), 400
        
        # Process emotion detection
        result = emotion_detector(text)
        
        # Validate emotion detection result
        if not result or 'dominant_emotion' not in result:
            return jsonify({
                "error": "Failed to detect emotions from the provided text"
            }), 500
        
        # Return successful response with emotion data
        return jsonify(result), 200
    
    except ValueError as e:
        # Handle validation errors from emotion_detector
        return jsonify({
            "error": f"Validation error: {str(e)}"
        }), 400
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/emotion/formatted', methods=['POST'])
def detect_emotion_formatted():
    """
    Route: POST /api/emotion/formatted
    Description: API endpoint for emotion detection with formatted output
    
    Request Body (JSON):
    {
        "text": "The text to analyze for emotions"
    }
    
    Response (Plain Text):
    For the given text, the system predicts the following emotions:
    anger: 0.0
    disgust: 0.0
    fear: 0.0
    joy: 0.876
    sadness: 0.0
    Dominant emotion: joy
    
    Status Codes:
    - 200: Success - emotions detected and formatted
    - 400: Bad Request - missing or invalid input
    - 500: Server Error - internal processing error
    """
    try:
        # Validate request content type
        if not request.is_json:
            return "Invalid request format. Please send JSON data.", 400
        
        # Get JSON data from request
        data = request.get_json()
        
        # Validate request body contains 'text' field
        if not data or 'text' not in data:
            return "Missing 'text' field in request body", 400
        
        # Extract and validate text
        text = data.get('text', '').strip()
        
        # Check if text is empty
        if not text:
            return "Text field cannot be empty", 400
        
        # Process emotion detection
        result = emotion_detector(text)
        
        # Format the output
        formatted_output = format_emotion_output(result)
        
        # Return formatted response
        return formatted_output, 200
    
    except Exception as e:
        # Handle unexpected errors
        return f"Internal server error: {str(e)}", 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Route: GET /health
    Description: Health check endpoint for monitoring
    Returns: JSON with server status
    
    Response (JSON):
    {
        "status": "healthy",
        "service": "Emotion Detection Server",
        "version": "1.0"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "Emotion Detection Server",
        "version": "1.0"
    }), 200


@app.route('/api/info', methods=['GET'])
def api_info():
    """
    Route: GET /api/info
    Description: Returns API documentation and available endpoints
    Returns: JSON with API information
    
    Response (JSON):
    {
        "api_version": "1.0",
        "endpoints": [
            {
                "path": "/api/emotion",
                "method": "POST",
                "description": "Detect emotions from text"
            },
            ...
        ]
    }
    """
    return jsonify({
        "api_version": "1.0",
        "service": "Emotion Detection API",
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "Render home page with web interface"
            },
            {
                "path": "/api/emotion",
                "method": "POST",
                "description": "Detect emotions from text (returns JSON)",
                "request": {
                    "format": "JSON",
                    "body": {
                        "text": "string - text to analyze"
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
                }
            },
            {
                "path": "/api/emotion/formatted",
                "method": "POST",
                "description": "Detect emotions from text (returns formatted text)",
                "request": {
                    "format": "JSON",
                    "body": {
                        "text": "string - text to analyze"
                    }
                },
                "response": {
                    "format": "Plain Text",
                    "body": "Formatted emotion analysis results"
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


@app.errorhandler(404)
def not_found(error):
    """
    Error Handler: 404 Not Found
    Description: Handles requests to non-existent endpoints
    """
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested resource does not exist. Use GET /api/info for available endpoints."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """
    Error Handler: 405 Method Not Allowed
    Description: Handles requests with incorrect HTTP method
    """
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method used is not allowed for this endpoint."
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """
    Error Handler: 500 Internal Server Error
    Description: Handles internal server errors
    """
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred on the server."
    }), 500


def run_server(debug=False, host='0.0.0.0', port=5000):
    """
    Function: run_server
    Description: Starts the Flask development/production server
    
    Parameters:
    - debug (bool): Enable debug mode (default: False)
    - host (str): Server host address (default: '0.0.0.0')
    - port (int): Server port number (default: 5000)
    
    Usage:
    >>> run_server(debug=True, port=5000)
    """
    print("=" * 70)
    print("Emotion Detection Web Server")
    print("=" * 70)
    print(f"Starting Flask server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug Mode: {debug}")
    print(f"Environment: {'Development' if debug else 'Production'}")
    print("=" * 70)
    print("\nAvailable Endpoints:")
    print("  GET  /                      - Home page with web interface")
    print("  POST /api/emotion           - Detect emotions (JSON response)")
    print("  POST /api/emotion/formatted - Detect emotions (text response)")
    print("  GET  /health                - Health check endpoint")
    print("  GET  /api/info              - API documentation")
    print("\n" + "=" * 70)
    
    app.run(debug=debug, host=host, port=port, use_reloader=debug)


if __name__ == '__main__':
    """
    Main Entry Point
    
    Usage:
    - Development mode: python server.py
    - Production mode: python server.py --no-debug
    - Custom port: python server.py --port 8080
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Emotion Detection Web Server')
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
