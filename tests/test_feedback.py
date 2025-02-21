import unittest
from unittest.mock import patch, MagicMock
import json
from modules.feedback.feedback_engine import FeedbackEngine

class TestFeedbackEngine(unittest.TestCase):
    def setUp(self):
        self.sample_attempt = "2x + 5 = 15 → x = 5"
        self.correct_solution = "2x = 10 → x = 5"

    @patch('modules.feedback.feedback_engine.Groq')
    def test_error_analysis(self, mock_groq):
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "error_analysis": {
                "error_type": "procedural",
                "specific_misconception": "Incorrect equation balancing steps"
            },
            "feedback_steps": [{
                "type": "explanation",
                "content": "Always perform the same operation on both sides",
                "priority": "critical"
            }]
        })
        mock_client.chat.completions.create.return_value = mock_response

        engine = FeedbackEngine()
        result = engine.analyze_errors(
            "Solve 2x + 5 = 15",
            self.sample_attempt,
            self.correct_solution
        )
        
        self.assertIn("error_analysis", result)
        self.assertIn("feedback_steps", result)

    @patch('modules.feedback.feedback_engine.Groq')
    def test_error_handling(self, mock_groq):
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        engine = FeedbackEngine()
        with self.assertRaises(Exception) as context:
            engine.analyze_errors("", "", "")
        
        self.assertIn("Feedback generation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()
