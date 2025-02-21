import os
import json
from groq import Groq
from typing import Dict, List

class ScaffoldingEngine:
    """Generates adaptive learning paths based on problem understanding and knowledge assessment."""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.scaffolding_prompt = """Create a step-by-step solution guide for this math problem.

PROBLEM:
{problem_text}

CONTEXT:
Type: {concept}
Analysis: {problem_analysis}
Student Level: {knowledge_assessment}

Return a JSON object with solution steps for the GIVEN problem above (not the example). Each step must have:
- instruction: What to do in this step
- expected_answer: The correct answer for this step
- hint: A helpful hint
- explanation: Why this step works

Format example (but create steps for the GIVEN problem, not this example):
{{
    "steps": [
        {{
            "instruction": "First step instruction",
            "expected_answer": "expected result",
            "hint": "helpful hint",
            "explanation": "why this step works"
        }}
    ]
}}"""

    def generate_scaffolding(self, 
                            concept: str,
                            problem_analysis: str,
                            knowledge_assessment: str,
                            problem_text: str) -> Dict:
        """Generate scaffolding steps for the given problem."""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": self.scaffolding_prompt.format(
                            concept=concept,
                            problem_analysis=problem_analysis, 
                            knowledge_assessment=knowledge_assessment,
                            problem_text=problem_text
                        )
                    }
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            
            # Extract the JSON response
            json_str = response.choices[0].message.content
            return json.loads(json_str)

        except Exception as e:
            print(f"Debug - Unexpected error: {str(e)}")
            return None

    def adapt_path(self, progress_data: Dict) -> Dict:
        """Adjust learning path based on student progress."""
        # Implementation for dynamic adaptation
        pass
