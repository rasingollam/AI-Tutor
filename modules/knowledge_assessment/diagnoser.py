from groq import Groq
import os
import json
from typing import Dict, List
from dotenv import load_dotenv

class KnowledgeAssessor:
    def __init__(self):
        """Initialize the Knowledge Assessor with Groq client and system prompts."""
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # System prompt for generating diagnostic questions
        self.diagnostic_prompt = """Generate diagnostic questions to assess the student's understanding of {concept}.
Focus on fundamental concepts and common misconceptions.

Output a JSON with this structure:
{{
    "questions": [
        {{
            "text": "question text",
            "options": ["option1", "option2", "option3", "option4"],
            "correct_index": 0,
            "explanation": "why this is the correct answer",
            "concept_tested": "specific concept being tested"
        }}
    ],
    "recommended_topics": ["list of topics to review based on concept"],
    "prerequisites": ["list of prerequisite concepts"]
}}"""
        
        # System prompt for analyzing student responses
        self.analysis_prompt = """
        Analyze the student's responses to diagnostic questions and identify:
        1. Knowledge gaps
        2. Misconceptions
        3. Areas of strength
        4. Recommended next steps
        
        Output a JSON with your analysis.
        """

    def generate_diagnostics(self, concept: str) -> Dict:
        """Generate diagnostic questions for a given concept."""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": self.diagnostic_prompt.format(concept=concept)
                    }
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Failed to generate diagnostics: {str(e)}")

    def analyze_responses(self, 
                        concept: str,
                        questions: List[Dict],
                        user_responses: List[int]) -> Dict:
        """
        Analyze user's responses to diagnostic questions.
        
        Args:
            concept: The concept being tested
            questions: List of question dictionaries
            user_responses: List of user's answer indices
        
        Returns:
            Dict containing analysis of user's understanding
        """
        # Prepare the analysis prompt with actual responses
        analysis_context = {
            "concept": concept,
            "responses": [
                {
                    "question": q["text"],
                    "user_answer": q["options"][user_resp],
                    "correct_answer": q["options"][q["correct_index"]],
                    "is_correct": user_resp == q["correct_index"]
                }
                for q, user_resp in zip(questions, user_responses)
            ]
        }
        
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": self.analysis_prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps(analysis_context)
                    }
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Failed to analyze responses: {str(e)}")
