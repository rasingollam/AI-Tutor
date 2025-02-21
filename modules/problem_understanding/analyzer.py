from groq import Groq
import os
from dotenv import load_dotenv
import json
from typing import Dict

class ProblemUnderstandingEngine:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.system_prompt = """You are a math problem analyzer. Return a valid JSON object analyzing this problem:

PROBLEM: {problem}

Return ONLY a JSON object in this exact format:
{
    "problem_type": "linear_equation",
    "key_concepts": ["equation_solving"],
    "complexity": "basic",
    "key_entities": ["x", "+"],
    "related_concepts": ["arithmetic"]
}

Rules:
1. problem_type must be one of: linear_equation, quadratic_equation, system_of_equations
2. complexity must be one of: basic, intermediate, advanced
3. All arrays must have at least one item
4. Return ONLY the JSON object, no other text"""

    def analyze_problem(self, problem_text: str) -> Dict:
        """Analyze math problems with strict JSON validation."""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": self.system_prompt.format(problem=problem_text)
                }],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            try:
                analysis = json.loads(raw_content)
            except json.JSONDecodeError:
                print(f"Debug - Invalid JSON: {raw_content}")
                return {
                    "problem_type": "linear_equation",
                    "key_concepts": ["equation_solving"],
                    "complexity": "basic",
                    "key_entities": ["x"],
                    "related_concepts": ["arithmetic"]
                }
            
            # Validate structure
            required_keys = ['problem_type', 'key_concepts', 'complexity', 'key_entities', 'related_concepts']
            if not all(key in analysis for key in required_keys):
                print(f"Debug - Missing keys in: {analysis}")
                return {
                    "problem_type": "linear_equation",
                    "key_concepts": ["equation_solving"],
                    "complexity": "basic",
                    "key_entities": ["x"],
                    "related_concepts": ["arithmetic"]
                }
            
            # Ensure arrays have content
            for key in ['key_concepts', 'key_entities', 'related_concepts']:
                if not isinstance(analysis[key], list) or len(analysis[key]) == 0:
                    analysis[key] = ["unknown"]
            
            # Validate complexity
            if analysis['complexity'] not in ['basic', 'intermediate', 'advanced']:
                analysis['complexity'] = 'basic'
            
            return analysis
            
        except Exception as e:
            print(f"Debug - Unexpected error: {str(e)}")
            return {
                "problem_type": "linear_equation",
                "key_concepts": ["equation_solving"],
                "complexity": "basic",
                "key_entities": ["x"],
                "related_concepts": ["arithmetic"]
            }
