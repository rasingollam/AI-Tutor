import unittest
from unittest.mock import patch, MagicMock
import json
from modules.knowledge_reinforcement.reinforcer import KnowledgeReinforcer

class TestKnowledgeReinforcer(unittest.TestCase):
    def setUp(self):
        self.sample_mistakes = ["equation_balancing", "negative_numbers"]
        
    @patch('modules.knowledge_reinforcement.reinforcer.Groq')
    def test_reinforcement_generation(self, mock_groq):
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "schedule": {"next_review": "2025-02-24", "interval_days": 3},
            "practice_set": [{"type": "application", "problem": "Solve 3x - 5 = 10"}]
        })
        mock_client.chat.completions.create.return_value = mock_response

        reinforcer = KnowledgeReinforcer()
        result = reinforcer.generate_reinforcement("linear equations", self.sample_mistakes, 65.0)
        
        self.assertIn("schedule", result)
        self.assertIn("practice_set", result)

    @patch('modules.knowledge_reinforcement.reinforcer.Groq')
    def test_error_handling(self, mock_groq):
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        reinforcer = KnowledgeReinforcer()
        with self.assertRaises(Exception) as context:
            reinforcer.generate_reinforcement("", [], 0)
        
        self.assertIn("Reinforcement generation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()
