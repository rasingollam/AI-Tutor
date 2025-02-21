import unittest
from unittest.mock import patch, MagicMock
import json
from modules.knowledge_assessment.diagnoser import KnowledgeAssessor

class TestKnowledgeAssessment(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_questions = {
            "questions": [
                {
                    "text": "What is the first step in solving 2x + 5 = 15?",
                    "options": [
                        "Subtract 5 from both sides",
                        "Divide both sides by 2",
                        "Add 5 to both sides",
                        "Multiply both sides by 2"
                    ],
                    "correct_index": 0,
                    "explanation": "To isolate the variable term, first remove the constant by subtracting 5",
                    "concept_tested": "equation_solving_steps"
                }
            ],
            "recommended_topics": ["order of operations", "equation solving"],
            "prerequisites": ["basic arithmetic", "understanding equality"]
        }
        
        self.sample_analysis = {
            "knowledge_gaps": ["order of operations"],
            "misconceptions": ["thinks addition and subtraction are interchangeable"],
            "strengths": ["understands the concept of equality"],
            "next_steps": ["practice basic equation solving steps"]
        }

    @patch('modules.knowledge_assessment.diagnoser.Groq')
    def test_generate_diagnostics(self, mock_groq):
        """Test diagnostic question generation."""
        # Configure mock
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(self.sample_questions)
        mock_client.chat.completions.create.return_value = mock_response

        # Test the method
        assessor = KnowledgeAssessor()
        result = assessor.generate_diagnostics("linear equations")
        
        # Assertions
        self.assertIn("questions", result)
        self.assertIn("recommended_topics", result)
        self.assertIn("prerequisites", result)
        self.assertEqual(len(result["questions"]), 1)
        self.assertEqual(len(result["questions"][0]["options"]), 4)

    @patch('modules.knowledge_assessment.diagnoser.Groq')
    def test_analyze_responses(self, mock_groq):
        """Test response analysis."""
        # Configure mock
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(self.sample_analysis)
        mock_client.chat.completions.create.return_value = mock_response

        # Test the method
        assessor = KnowledgeAssessor()
        result = assessor.analyze_responses(
            concept="linear equations",
            questions=self.sample_questions["questions"],
            user_responses=[1]  # Incorrect answer
        )
        
        # Assertions
        self.assertIn("knowledge_gaps", result)
        self.assertIn("misconceptions", result)
        self.assertIn("strengths", result)
        self.assertIn("next_steps", result)

    @patch('modules.knowledge_assessment.diagnoser.Groq')
    def test_error_handling(self, mock_groq):
        """Test error handling in both methods."""
        # Configure mock to raise an exception
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        assessor = KnowledgeAssessor()
        
        # Test generate_diagnostics error handling
        with self.assertRaises(Exception) as context:
            assessor.generate_diagnostics("linear equations")
        self.assertIn("Failed to generate diagnostics", str(context.exception))
        
        # Test analyze_responses error handling
        with self.assertRaises(Exception) as context:
            assessor.analyze_responses(
                concept="linear equations",
                questions=self.sample_questions["questions"],
                user_responses=[0]
            )
        self.assertIn("Failed to analyze responses", str(context.exception))

if __name__ == '__main__':
    unittest.main()
