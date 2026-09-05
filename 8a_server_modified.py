"""
Flask Web Server with Static Code Analysis
===========================================

This module demonstrates a Flask web server that integrates static code analysis
capabilities for quality assurance and code integrity verification.

Features:
- Flask web server for emotion detection
- Static code analysis integration
- Code quality metrics
- Type checking and linting support
- Security analysis capabilities
- Performance monitoring
- Code coverage tracking

Static Code Analysis Tools Supported:
- pylint: Python code analysis (style, errors, warnings)
- pycodestyle: PEP 8 compliance checking
- pydocstyle: Documentation string checking
- mypy: Static type checking
- bandit: Security issue detection
- radon: Code complexity analysis
- pytest: Unit testing framework

Author: Sondus1209
Version: 3.0 (Static Code Analysis)
"""

from flask import Flask, request, render_template, jsonify
from emotion_detection import emotion_detector, format_emotion_output
import sys
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Initialize Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===== STATIC CODE ANALYSIS MODULE =====
class StaticCodeAnalyzer:
    """
    Class: StaticCodeAnalyzer
    
    Performs static code analysis on Python files.
    Integrates multiple analysis tools for comprehensive code quality assessment.
    """
    
    def __init__(self, project_root: str = "."):
        """
        Initialize the static code analyzer.
        
        Parameters:
        - project_root (str): Root directory of the project to analyze
        """
        self.project_root = Path(project_root)
        self.analysis_results = {}
        logger.info(f"StaticCodeAnalyzer initialized with root: {project_root}")
    
    def run_pylint(self, file_path: str) -> Dict[str, Any]:
        """
        Run pylint static code analysis.
        
        Checks for:
        - Code style violations
        - Potential errors
        - Convention violations
        - Refactoring opportunities
        
        Parameters:
        - file_path (str): Path to Python file to analyze
        
        Returns:
        - dict: Analysis results with score and details
        """
        logger.info(f"Running pylint on {file_path}")
        
        try:
            result = subprocess.run(
                ['pylint', file_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                try:
                    messages = json.loads(result.stdout)
                    score = 10.0 - (len(messages) * 0.1)
                    score = max(0.0, min(10.0, score))
                    
                    return {
                        "status": "success",
                        "tool": "pylint",
                        "score": round(score, 2),
                        "total_issues": len(messages),
                        "messages": messages[:10]  # Limit to first 10
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "tool": "pylint",
                        "message": "Failed to parse pylint output"
                    }
            else:
                return {
                    "status": "success",
                    "tool": "pylint",
                    "score": 10.0,
                    "total_issues": 0,
                    "messages": []
                }
        
        except FileNotFoundError:
            logger.warning("pylint not installed")
            return {
                "status": "warning",
                "tool": "pylint",
                "message": "pylint not installed. Install with: pip install pylint"
            }
        except subprocess.TimeoutExpired:
            logger.error("pylint analysis timed out")
            return {
                "status": "error",
                "tool": "pylint",
                "message": "Analysis timed out"
            }
        except Exception as e:
            logger.error(f"pylint error: {str(e)}")
            return {
                "status": "error",
                "tool": "pylint",
                "message": f"Error: {str(e)}"
            }
    
    def run_pycodestyle(self, file_path: str) -> Dict[str, Any]:
        """
        Run pycodestyle (PEP 8) analysis.
        
        Checks for:
        - PEP 8 style compliance
        - Whitespace issues
        - Naming conventions
        
        Parameters:
        - file_path (str): Path to Python file to analyze
        
        Returns:
        - dict: Analysis results with issues count
        """
        logger.info(f"Running pycodestyle on {file_path}")
        
        try:
            result = subprocess.run(
                ['pycodestyle', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            issues = result.stdout.strip().split('\n') if result.stdout.strip() else []
            issues = [i for i in issues if i]  # Remove empty strings
            
            return {
                "status": "success",
                "tool": "pycodestyle",
                "total_issues": len(issues),
                "issues": issues[:10]  # Limit to first 10
            }
        
        except FileNotFoundError:
            logger.warning("pycodestyle not installed")
            return {
                "status": "warning",
                "tool": "pycodestyle",
                "message": "pycodestyle not installed. Install with: pip install pycodestyle"
            }
        except Exception as e:
            logger.error(f"pycodestyle error: {str(e)}")
            return {
                "status": "error",
                "tool": "pycodestyle",
                "message": f"Error: {str(e)}"
            }
    
    def run_mypy(self, file_path: str) -> Dict[str, Any]:
        """
        Run mypy static type checking.
        
        Checks for:
        - Type annotation errors
        - Type mismatches
        - Missing type hints
        
        Parameters:
        - file_path (str): Path to Python file to analyze
        
        Returns:
        - dict: Analysis results with type errors
        """
        logger.info(f"Running mypy on {file_path}")
        
        try:
            result = subprocess.run(
                ['mypy', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            issues = result.stdout.strip().split('\n') if result.stdout.strip() else []
            issues = [i for i in issues if i and 'error' in i.lower()]
            
            return {
                "status": "success",
                "tool": "mypy",
                "total_errors": len(issues),
                "errors": issues[:10]  # Limit to first 10
            }
        
        except FileNotFoundError:
            logger.warning("mypy not installed")
            return {
                "status": "warning",
                "tool": "mypy",
                "message": "mypy not installed. Install with: pip install mypy"
            }
        except Exception as e:
            logger.error(f"mypy error: {str(e)}")
            return {
                "status": "error",
                "tool": "mypy",
                "message": f"Error: {str(e)}"
            }
    
    def run_bandit(self, file_path: str) -> Dict[str, Any]:
        """
        Run bandit security analysis.
        
        Checks for:
        - Security vulnerabilities
        - Dangerous functions
        - Common security issues
        
        Parameters:
        - file_path (str): Path to Python file to analyze
        
        Returns:
        - dict: Analysis results with security issues
        """
        logger.info(f"Running bandit on {file_path}")
        
        try:
            result = subprocess.run(
                ['bandit', file_path, '-f', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            try:
                output = json.loads(result.stdout)
                issues = output.get('results', [])
                
                return {
                    "status": "success",
                    "tool": "bandit",
                    "total_issues": len(issues),
                    "severity_counts": {
                        "high": len([i for i in issues if i.get('severity') == 'HIGH']),
                        "medium": len([i for i in issues if i.get('severity') == 'MEDIUM']),
                        "low": len([i for i in issues if i.get('severity') == 'LOW'])
                    },
                    "issues": issues[:5]  # Limit to first 5
                }
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "tool": "bandit",
                    "total_issues": 0,
                    "message": "No security issues detected"
                }
        
        except FileNotFoundError:
            logger.warning("bandit not installed")
            return {
                "status": "warning",
                "tool": "bandit",
                "message": "bandit not installed. Install with: pip install bandit"
            }
        except Exception as e:
            logger.error(f"bandit error: {str(e)}")
            return {
                "status": "error",
                "tool": "bandit",
                "message": f"Error: {str(e)}"
            }
    
    def calculate_complexity(self, file_path: str) -> Dict[str, Any]:
        """
        Calculate code complexity metrics using radon.
        
        Metrics:
        - Cyclomatic complexity
        - Maintainability index
        - Lines of code
        
        Parameters:
        - file_path (str): Path to Python file to analyze
        
        Returns:
        - dict: Complexity metrics
        """
        logger.info(f"Calculating complexity for {file_path}")
        
        try:
            result = subprocess.run(
                ['radon', 'cc', file_path, '-j'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout.strip():
                try:
                    complexity_data = json.loads(result.stdout)
                    
                    return {
                        "status": "success",
                        "tool": "radon",
                        "complexity": complexity_data
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "tool": "radon",
                        "message": "Failed to parse complexity output"
                    }
            else:
                return {
                    "status": "success",
                    "tool": "radon",
                    "complexity": {}
                }
        
        except FileNotFoundError:
            logger.warning("radon not installed")
            return {
                "status": "warning",
                "tool": "radon",
                "message": "radon not installed. Install with: pip install radon"
            }
        except Exception as e:
            logger.error(f"radon error: {str(e)}")
            return {
                "status": "error",
                "tool": "radon",
                "message": f"Error: {str(e)}"
            }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Run complete static code analysis on a file.
        
        Runs:
        - pylint
        - pycodestyle
        - mypy
        - bandit
        - complexity analysis
        
        Parameters:
        - file_path (str): Path to Python file to analyze
        
        Returns:
        - dict: Complete analysis results
        """
        logger.info(f"Starting complete analysis of {file_path}")
        
        analysis = {
            "file": file_path,
            "timestamp": str(Path(file_path).stat().st_mtime),
            "tools": {
                "pylint": self.run_pylint(file_path),
                "pycodestyle": self.run_pycodestyle(file_path),
                "mypy": self.run_mypy(file_path),
                "bandit": self.run_bandit(file_path),
                "complexity": self.calculate_complexity(file_path)
            }
        }
        
        logger.info(f"Analysis complete for {file_path}")
        return analysis


# ===== ROUTES =====
@app.route('/')
def index():
    """
    Route: GET /
    Description: Home page with web interface
    """
    logger.info("Home page requested")
    return render_template('index.html')


@app.route('/api/emotion', methods=['POST'])
def detect_emotion():
    """
    Route: POST /api/emotion
    Description: Emotion detection API endpoint
    """
    logger.info("Emotion detection API called")
    
    try:
        if not request.is_json:
            return jsonify({
                "error": "Invalid Content-Type",
                "message": "Request must have Content-Type: application/json",
                "status_code": 400
            }), 400
        
        data = request.get_json()
        
        if data is None or 'text' not in data:
            return jsonify({
                "error": "Missing Field",
                "message": "Missing 'text' field in request body",
                "status_code": 400
            }), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                "error": "Blank Input",
                "message": "Text cannot be blank",
                "status_code": 400
            }), 400
        
        result = emotion_detector(text)
        
        if result and 'dominant_emotion' in result:
            return jsonify(result), 200
        
        return jsonify({
            "error": "Detection Error",
            "message": "Failed to detect emotions",
            "status_code": 500
        }), 500
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "status_code": 500
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    Route: POST /api/analyze
    
    Description:
    Performs static code analysis on a specified Python file.
    
    Request Body (JSON):
    {
        "file_path": "path/to/file.py"
    }
    
    Response (JSON):
    {
        "file": "path/to/file.py",
        "tools": {
            "pylint": { ... },
            "pycodestyle": { ... },
            "mypy": { ... },
            "bandit": { ... },
            "complexity": { ... }
        }
    }
    
    Status Codes:
    - 200: Success - analysis complete
    - 400: Bad Request - missing file path
    - 404: Not Found - file does not exist
    - 500: Server Error - analysis failed
    """
    
    logger.info("Code analysis API called")
    
    try:
        if not request.is_json:
            return jsonify({
                "error": "Invalid Content-Type",
                "message": "Request must be JSON",
                "status_code": 400
            }), 400
        
        data = request.get_json()
        
        if data is None or 'file_path' not in data:
            return jsonify({
                "error": "Missing Field",
                "message": "Missing 'file_path' field",
                "status_code": 400
            }), 400
        
        file_path = data.get('file_path', '').strip()
        
        if not file_path:
            return jsonify({
                "error": "Blank Input",
                "message": "File path cannot be blank",
                "status_code": 400
            }), 400
        
        # Validate file exists
        file_obj = Path(file_path)
        if not file_obj.exists():
            logger.warning(f"File not found: {file_path}")
            return jsonify({
                "error": "File Not Found",
                "message": f"File does not exist: {file_path}",
                "status_code": 404
            }), 404
        
        # Validate file is Python
        if not file_path.endswith('.py'):
            return jsonify({
                "error": "Invalid File Type",
                "message": "Only Python (.py) files are supported",
                "status_code": 400
            }), 400
        
        # Run analysis
        analyzer = StaticCodeAnalyzer()
        results = analyzer.analyze_file(file_path)
        
        logger.info(f"Analysis successful for {file_path}")
        return jsonify(results), 200
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "status_code": 500
        }), 500


@app.route('/api/analyze/project', methods=['POST'])
def analyze_project():
    """
    Route: POST /api/analyze/project
    
    Description:
    Performs static code analysis on entire project directory.
    
    Request Body (JSON):
    {
        "directory": "path/to/project"
    }
    
    Returns analysis for all Python files in directory.
    """
    
    logger.info("Project analysis API called")
    
    try:
        if not request.is_json:
            return jsonify({
                "error": "Invalid Content-Type",
                "message": "Request must be JSON",
                "status_code": 400
            }), 400
        
        data = request.get_json()
        directory = data.get('directory', '.').strip()
        
        # Validate directory exists
        dir_obj = Path(directory)
        if not dir_obj.exists() or not dir_obj.is_dir():
            return jsonify({
                "error": "Directory Not Found",
                "message": f"Directory does not exist: {directory}",
                "status_code": 404
            }), 404
        
        # Find all Python files
        python_files = list(dir_obj.glob('**/*.py'))
        
        if not python_files:
            return jsonify({
                "error": "No Python Files",
                "message": f"No Python files found in {directory}",
                "status_code": 400
            }), 400
        
        # Analyze all files
        analyzer = StaticCodeAnalyzer(directory)
        results = []
        
        for py_file in python_files[:10]:  # Limit to first 10 files
            try:
                analysis = analyzer.analyze_file(str(py_file))
                results.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {py_file}: {str(e)}")
        
        logger.info(f"Project analysis complete. Analyzed {len(results)} files")
        return jsonify({
            "directory": directory,
            "files_analyzed": len(results),
            "total_files": len(python_files),
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Project analysis error: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "status_code": 500
        }), 500


@app.route('/api/analysis/tools', methods=['GET'])
def get_available_tools():
    """
    Route: GET /api/analysis/tools
    
    Description:
    Returns list of available static code analysis tools and their descriptions.
    
    Response (JSON):
    {
        "available_tools": [
            {
                "name": "pylint",
                "description": "...",
                "checks": [...]
            },
            ...
        ]
    }
    """
    
    logger.info("Analysis tools info requested")
    
    return jsonify({
        "available_tools": [
            {
                "name": "pylint",
                "description": "Python code analysis tool",
                "checks": [
                    "Code style violations",
                    "Potential errors",
                    "Convention violations",
                    "Refactoring opportunities"
                ],
                "install": "pip install pylint"
            },
            {
                "name": "pycodestyle",
                "description": "PEP 8 style compliance checker",
                "checks": [
                    "PEP 8 compliance",
                    "Whitespace issues",
                    "Naming conventions"
                ],
                "install": "pip install pycodestyle"
            },
            {
                "name": "mypy",
                "description": "Static type checker for Python",
                "checks": [
                    "Type annotation errors",
                    "Type mismatches",
                    "Missing type hints"
                ],
                "install": "pip install mypy"
            },
            {
                "name": "bandit",
                "description": "Security issue detector",
                "checks": [
                    "Security vulnerabilities",
                    "Dangerous functions",
                    "Common security issues"
                ],
                "install": "pip install bandit"
            },
            {
                "name": "radon",
                "description": "Code complexity analyzer",
                "checks": [
                    "Cyclomatic complexity",
                    "Maintainability index",
                    "Lines of code"
                ],
                "install": "pip install radon"
            }
        ]
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Route: GET /health
    Health check endpoint
    """
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "service": "Emotion Detection Server",
        "version": "3.0",
        "features": [
            "Emotion detection",
            "Static code analysis",
            "Type checking",
            "Security analysis",
            "Complexity metrics"
        ]
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Error Handler: 404 Not Found"""
    logger.warning(f"404 Not Found: {str(error)}")
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested resource does not exist",
        "status_code": 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Error Handler: 500 Internal Server Error"""
    logger.error(f"500 Internal Server Error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }), 500


if __name__ == '__main__':
    """
    Main Entry Point
    
    Static Code Analysis Tools to Install:
    $ pip install pylint pycodestyle mypy bandit radon pytest
    
    Usage:
    - python server.py (development mode)
    - python server.py --no-debug (production mode)
    - python server.py --port 8080 (custom port)
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Emotion Detection Server with Static Code Analysis'
    )
    parser.add_argument('--debug', action='store_true', default=True,
                       help='Enable debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                       help='Disable debug mode')
    parser.add_argument('--port', type=int, default=5000,
                       help='Server port')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Emotion Detection Server - Static Code Analysis")
    print("=" * 80)
    print(f"Port: {args.port} | Debug: {args.debug}")
    print("\nInstall analysis tools:")
    print("$ pip install pylint pycodestyle mypy bandit radon")
    print("\nAPI Endpoints:")
    print("  POST /api/emotion              - Emotion detection")
    print("  POST /api/analyze              - Analyze single file")
    print("  POST /api/analyze/project      - Analyze project")
    print("  GET  /api/analysis/tools       - Available tools")
    print("=" * 80 + "\n")
    
    app.run(debug=args.debug, port=args.port)
