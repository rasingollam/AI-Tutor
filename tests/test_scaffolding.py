import unittest
from unittest.mock import patch, MagicMock
import json
from modules.scaffolding.engine import ScaffoldingEngine

class TestScaffoldingEngine(unittest.TestCase):
    def setUp(self):
        self.sample_analysis = {
            "problem_type": "algebraic_equation",
            "complexity": "intermediate"
        }
        
        self.sample_assessment = {
            "knowledge_gaps": ["equation_balancing"],
            "strengths": ["arithmetic_operations"]
        }

    @patch('modules.scaffolding.engine.Groq')
    def test_generate_scaffolding(self, mock_groq):
        """Test scaffolding generation."""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "learning_objectives": ["Master equation balancing"],
            "steps": [{
                "type": "explanation",
                "content": "Understanding equation balance...",
                "resources": ["video_link"],
                "checkpoint_question": "What's the purpose of balancing?"
            }]
        })
        mock_client.chat.completions.create.return_value = mock_response

        engine = ScaffoldingEngine()
        result = engine.generate_scaffolding(
            "linear equations",
            self.sample_analysis,
            self.sample_assessment
        )
        
        self.assertIn("learning_objectives", result)
        self.assertIn("steps", result)

    @patch('modules.scaffolding.engine.Groq')
    def test_error_handling(self, mock_groq):
        """Test error handling."""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        engine = ScaffoldingEngine()
        with self.assertRaises(Exception) as context:
            engine.generate_scaffolding("linear equations", {}, {})
        
        self.assertIn("Scaffolding generation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()
