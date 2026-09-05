import unittest
import sys
sys.path.insert(0, '.')
from emotion_detection import emotion_detector, format_emotion_output


class TestEmotionDetection(unittest.TestCase):
    """
    Unit tests for the emotion_detector function
    Tests various text inputs and validates the emotion detection results
    """

    def test_joy_emotion(self):
        """
        Test Case 1: Verify that 'joy' is the dominant emotion for positive text
        """
        text = "I am so happy and excited about this amazing opportunity!"
        result = emotion_detector(text)
        
        # Assert that joy is the dominant emotion
        self.assertEqual(result['dominant_emotion'], 'joy',
                        "Failed: Joy should be the dominant emotion for positive text")
        
        # Assert that joy score is greater than other emotions
        self.assertGreater(result['joy'], result['anger'],
                          "Failed: Joy score should be greater than anger")
        self.assertGreater(result['joy'], result['disgust'],
                          "Failed: Joy score should be greater than disgust")
        self.assertGreater(result['joy'], result['fear'],
                          "Failed: Joy score should be greater than fear")
        self.assertGreater(result['joy'], result['sadness'],
                          "Failed: Joy score should be greater than sadness")

    def test_anger_emotion(self):
        """
        Test Case 2: Verify that 'anger' is the dominant emotion for angry text
        """
        text = "This is absolutely terrible and makes me very angry."
        result = emotion_detector(text)
        
        # Assert that anger is the dominant emotion
        self.assertEqual(result['dominant_emotion'], 'anger',
                        "Failed: Anger should be the dominant emotion for angry text")
        
        # Assert that anger score is greater than other emotions
        self.assertGreater(result['anger'], result['joy'],
                          "Failed: Anger score should be greater than joy")
        self.assertGreater(result['anger'], result['sadness'],
                          "Failed: Anger score should be greater than sadness")

    def test_sadness_emotion(self):
        """
        Test Case 3: Verify that 'sadness' is the dominant emotion for sad text
        """
        text = "I feel quite sad and disappointed with the results."
        result = emotion_detector(text)
        
        # Assert that sadness is the dominant emotion
        self.assertEqual(result['dominant_emotion'], 'sadness',
                        "Failed: Sadness should be the dominant emotion for sad text")
        
        # Assert that sadness score is greater than other emotions
        self.assertGreater(result['sadness'], result['joy'],
                          "Failed: Sadness score should be greater than joy")
        self.assertGreater(result['sadness'], result['anger'],
                          "Failed: Sadness score should be greater than anger")

    def test_fear_emotion(self):
        """
        Test Case 4: Verify that 'fear' is the dominant emotion for fearful text
        """
        text = "I'm very worried and anxious about what might happen."
        result = emotion_detector(text)
        
        # Assert that fear is in the result
        self.assertIsNotNone(result['fear'],
                            "Failed: Fear score should not be None")
        
        # Assert that all emotion scores are present
        self.assertIsNotNone(result['anger'], "Failed: Anger score is missing")
        self.assertIsNotNone(result['disgust'], "Failed: Disgust score is missing")
        self.assertIsNotNone(result['sadness'], "Failed: Sadness score is missing")
        self.assertIsNotNone(result['joy'], "Failed: Joy score is missing")

    def test_disgust_emotion(self):
        """
        Test Case 5: Verify that 'disgust' can be detected in text
        """
        text = "This is absolutely disgusting and repulsive!"
        result = emotion_detector(text)
        
        # Assert that disgust score exists and is greater than 0
        self.assertGreater(result['disgust'], 0,
                          "Failed: Disgust score should be greater than 0")
        
        # Assert that result contains dominant emotion
        self.assertIsNotNone(result['dominant_emotion'],
                            "Failed: Dominant emotion should not be None")

    def test_emotion_detector_returns_dict(self):
        """
        Test Case 6: Verify that emotion_detector returns a dictionary
        """
        text = "I love this amazing application!"
        result = emotion_detector(text)
        
        # Assert that result is a dictionary
        self.assertIsInstance(result, dict,
                             "Failed: Result should be a dictionary")
        
        # Assert that all required keys are present
        required_keys = ['anger', 'disgust', 'fear', 'joy', 'sadness', 'dominant_emotion']
        for key in required_keys:
            self.assertIn(key, result,
                         f"Failed: Key '{key}' should be in the result dictionary")

    def test_emotion_scores_range(self):
        """
        Test Case 7: Verify that emotion scores are within valid range (0-1)
        """
        text = "I am feeling neutral about this situation."
        result = emotion_detector(text)
        
        # Assert that all emotion scores are between 0 and 1
        emotions = ['anger', 'disgust', 'fear', 'joy', 'sadness']
        for emotion in emotions:
            if result[emotion] is not None:
                self.assertGreaterEqual(result[emotion], 0,
                                       f"Failed: {emotion} score should be >= 0")
                self.assertLessEqual(result[emotion], 1,
                                    f"Failed: {emotion} score should be <= 1")

    def test_format_emotion_output(self):
        """
        Test Case 8: Verify that format_emotion_output produces formatted string
        """
        emotion_dict = {
            'anger': 0.0,
            'disgust': 0.0,
            'fear': 0.0,
            'joy': 0.876,
            'sadness': 0.0,
            'dominant_emotion': 'joy'
        }
        
        formatted = format_emotion_output(emotion_dict)
        
        # Assert that formatted output is a string
        self.assertIsInstance(formatted, str,
                             "Failed: Formatted output should be a string")
        
        # Assert that formatted output contains emotion information
        self.assertIn('joy', formatted.lower(),
                     "Failed: Formatted output should contain emotion name")
        self.assertIn('0.876', formatted,
                     "Failed: Formatted output should contain emotion scores")

    def test_multiple_emotion_detection(self):
        """
        Test Case 9: Verify emotion detection with mixed emotions
        """
        texts = [
            "I am so happy!",
            "I am very angry!",
            "I feel sad.",
            "I am scared!"
        ]
        
        for text in texts:
            result = emotion_detector(text)
            
            # Assert that each result has a dominant emotion
            self.assertIsNotNone(result['dominant_emotion'],
                               f"Failed: Dominant emotion should be detected for '{text}'")
            
            # Assert that dominant emotion is one of the five emotions
            valid_emotions = ['anger', 'disgust', 'fear', 'joy', 'sadness']
            self.assertIn(result['dominant_emotion'], valid_emotions,
                         f"Failed: Dominant emotion should be one of {valid_emotions}")

    def test_empty_string_handling(self):
        """
        Test Case 10: Verify that empty string is handled properly
        """
        text = ""
        result = emotion_detector(text)
        
        # Assert that result is returned even for empty string
        self.assertIsNotNone(result,
                            "Failed: Function should return result for empty string")
        
        # Assert that result is a dictionary
        self.assertIsInstance(result, dict,
                             "Failed: Result should be a dictionary for empty string")


class TestEmotionDetectionIntegration(unittest.TestCase):
    """
    Integration tests for emotion detection module
    """

    def test_complete_workflow(self):
        """
        Test Case 11: Test complete workflow from detection to formatting
        """
        text = "I am absolutely thrilled and delighted!"
        
        # Detect emotions
        result = emotion_detector(text)
        
        # Format output
        formatted = format_emotion_output(result)
        
        # Assert that entire workflow works
        self.assertIsNotNone(result, "Failed: Emotion detection should return result")
        self.assertIsNotNone(formatted, "Failed: Output formatting should return string")
        self.assertIn(result['dominant_emotion'], formatted.lower(),
                     "Failed: Formatted output should contain dominant emotion")


if __name__ == '__main__':
    # Run all unit tests
    unittest.main(verbosity=2)
