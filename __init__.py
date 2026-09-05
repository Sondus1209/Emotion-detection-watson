"""
Emotion Detection Watson NLP Module

This module provides emotion detection functionality using IBM Watson NLP library.
It includes functions to analyze and detect emotions in text.

Author: Sondus1209
Version: 1.0
"""

from .emotion_detection import emotion_detector
from .emotion_detection import format_emotion_output
from .emotion_detection import main

__version__ = "1.0"
__author__ = "Sondus1209"

__all__ = [
    'emotion_detector',
    'format_emotion_output',
    'main'
]

# Module description
__doc__ = """
Emotion Detection Watson NLP Application

This module provides comprehensive emotion detection functionality using 
IBM Watson Natural Language Understanding (NLU) API.

Main Functions:
- emotion_detector(text_to_analyze): Analyzes text and returns emotion scores
- format_emotion_output(emotion_dict): Formats emotion detection output
- main(): Runs demonstration with sample texts

Supported Emotions:
- Anger
- Disgust
- Fear
- Joy
- Sadness

Usage:
    from emotion_detection import emotion_detector
    
    result = emotion_detector("I am very happy!")
    print(result)
    # Output: {'anger': 0.0, 'disgust': 0.0, 'fear': 0.0, 
    #          'joy': 0.876, 'sadness': 0.0, 'dominant_emotion': 'joy'}

For more information, visit: https://github.com/Sondus1209/Emotion-detection-watson
"""
