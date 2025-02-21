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

Create steps that:
1. Are clear and specific about what needs to be done
2. Include the expected result of each step
3. Provide helpful hints for common mistakes
4. Give clear explanations of the mathematical concepts

For each step, provide:
- instruction: Clear, specific instruction about what to do AND what the result should look like
- expected_answer: The answer for this specific step (include alternate forms if applicable)
- hint: A helpful hint that guides without giving away the answer
- explanation: Why this step is important and how it helps solve the problem

Example format (but create steps for the GIVEN problem):
{{
    "steps": [
        {{
            "instruction": "Move all x terms to the left side by subtracting 4x from both sides. You should get: -2x + 6 = -2",
            "expected_answer": "-2x + 6 = -2|-2x+6=-2|6-2x=-2",
            "hint": "When moving terms, remember to change their signs",
            "explanation": "Grouping like terms (terms with x) on one side makes it easier to solve for x"
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
