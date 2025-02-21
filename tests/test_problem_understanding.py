# tests/test_problem_understanding.py
import unittest
from unittest.mock import patch, MagicMock
from modules.problem_understanding.analyzer import ProblemUnderstandingEngine

class TestProblemUnderstanding(unittest.TestCase):
    @patch('modules.problem_understanding.analyzer.Groq')
    @patch('modules.problem_understanding.analyzer.os.getenv')
    def test_analyze_problem(self, mock_getenv, mock_groq):
        # Mock environment setup
        mock_getenv.return_value = "mock-api-key"
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        # Configure mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"problem_type":"algebra"}'
        mock_client.chat.completions.create.return_value = mock_response

        # Test the analyzer
        engine = ProblemUnderstandingEngine()
        result = engine.analyze_problem("Solve 2x + 5 = 15")
        
        # Verify the response
        self.assertIn("problem_type", result)
        mock_client.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    unittest.main()