import requests
import json

def emotion_detector(text_to_analyze):
    """
    Analyze the emotion of the given text using Watson NLP API
    
    Args:
        text_to_analyze (str): The text to analyze for emotions
        
    Returns:
        dict: A dictionary containing emotion scores and the dominant emotion in correct format
    """
    
    # Watson NLP API endpoint
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/YOUR_INSTANCE_ID/v1/analyze"
    
    # API parameters
    params = {
        "version": "2021-08-01"
    }
    
    # Request headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request body with emotion feature enabled
    data = {
        "text": text_to_analyze,
        "features": {
            "emotion": {}
        }
    }
    
    try:
        # Make API request
        response = requests.post(url, json=data, headers=headers, params=params, auth=('apikey', 'YOUR_API_KEY'))
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract emotion scores
            emotions = response_data.get('emotion', {}).get('document', {}).get('emotion', {})
            
            # Find the dominant emotion
            if emotions:
                dominant_emotion = max(emotions, key=emotions.get)
            else:
                dominant_emotion = None
            
            # Return results in correct output format
            return {
                'anger': emotions.get('anger', 0),
                'disgust': emotions.get('disgust', 0),
                'fear': emotions.get('fear', 0),
                'joy': emotions.get('joy', 0),
                'sadness': emotions.get('sadness', 0),
                'dominant_emotion': dominant_emotion
            }
        else:
            return {
                'anger': None,
                'disgust': None,
                'fear': None,
                'joy': None,
                'sadness': None,
                'dominant_emotion': None
            }
            
    except Exception as e:
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }


def format_emotion_output(emotion_dict):
    """
    Format the emotion detection output for display
    
    Args:
        emotion_dict (dict): Dictionary containing emotion scores
        
    Returns:
        str: Formatted string representation of emotions
    """
    if emotion_dict['dominant_emotion'] is None:
        return "Unable to detect emotions from the provided text."
    
    output = f"""
Emotion Detection Results:
========================
Anger:              {emotion_dict['anger']:.4f}
Disgust:            {emotion_dict['disgust']:.4f}
Fear:               {emotion_dict['fear']:.4f}
Joy:                {emotion_dict['joy']:.4f}
Sadness:            {emotion_dict['sadness']:.4f}
------------------------
Dominant Emotion:   {emotion_dict['dominant_emotion'].upper()}
"""
    return output


def main():
    """Main function to demonstrate emotion detection with formatted output"""
    
    print("=" * 60)
    print("Watson NLP Emotion Detection Application")
    print("Output Formatting Version 3a")
    print("=" * 60)
    
    # Example texts to analyze
    test_texts = [
        "I am so happy and excited about this amazing opportunity!",
        "This is absolutely terrible and makes me very angry.",
        "I feel quite sad and disappointed with the results.",
        "I'm not sure what to think about this situation."
    ]
    
    for text in test_texts:
        print(f"\nAnalyzing: \"{text}\"")
        print("-" * 60)
        
        result = emotion_detector(text)
        formatted_output = format_emotion_output(result)
        print(formatted_output)
    
    print("=" * 60)
    print("Analysis Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
