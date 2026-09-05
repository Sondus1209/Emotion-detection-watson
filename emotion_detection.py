import requests
import json

def emotion_detector(text_to_analyze):
    """
    Analyze the emotion of the given text using Watson NLP API
    
    Args:
        text_to_analyze (str): The text to analyze for emotions
        
    Returns:
        dict: A dictionary containing emotion scores and the dominant emotion
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
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Return results
            return {
                'anger': emotions.get('anger', 0),
                'disgust': emotions.get('disgust', 0),
                'fear': emotions.get('fear', 0),
                'joy': emotions.get('joy', 0),
                'sadness': emotions.get('sadness', 0),
                'dominant_emotion': dominant_emotion
            }
        else:
            return {'error': f'API Error: {response.status_code}'}
            
    except Exception as e:
        return {'error': str(e)}


def main():
    """Main function to demonstrate emotion detection"""
    
    print("=" * 50)
    print("Watson NLP Emotion Detection Application")
    print("=" * 50)
    
    # Example texts to analyze
    test_texts = [
        "I am so happy and excited about this amazing opportunity!",
        "This is absolutely terrible and makes me very angry.",
        "I feel quite sad and disappointed with the results."
    ]
    
    for text in test_texts:
        print(f"\nAnalyzing: {text}")
        result = emotion_detector(text)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Emotions detected:")
            print(f"  - Anger: {result['anger']:.3f}")
            print(f"  - Disgust: {result['disgust']:.3f}")
            print(f"  - Fear: {result['fear']:.3f}")
            print(f"  - Joy: {result['joy']:.3f}")
            print(f"  - Sadness: {result['sadness']:.3f}")
            print(f"  - Dominant Emotion: {result['dominant_emotion'].upper()}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
