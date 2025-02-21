import os
import json
from groq import Groq

class AnswerValidator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.validation_prompt = """You are a math answer validator that understands student reasoning. Analyze the student's answer and determine if it demonstrates correct mathematical understanding.

CONTEXT:
Current Step: {step_instruction}
Expected Answer: {expected_answer}
Student's Work: {user_answer}

VALIDATION RULES:
1. Accept mathematically equivalent expressions:
   - Different forms (e.g., "2x = 8" equals "8 = 2x")
   - Different orderings (e.g., "-2x + 6 = -2" equals "6 - 2x = -2")
   - Different but equivalent expressions (e.g., "x = 4" equals "x = 8/2")

2. Accept step-by-step work that:
   - Shows correct mathematical reasoning
   - Leads to a correct result
   - May include intermediate steps

3. Accept natural language explanations that demonstrate understanding

4. For final answer steps:
   - Accept any mathematically equivalent form of the answer
   - Be more lenient with formatting
   - Focus on mathematical correctness

5. For intermediate steps:
   - Prefer the suggested form but accept equivalents
   - Check that the step achieves the intended goal
   - Validate the mathematical reasoning

Return a JSON response with these exact keys:
{{
    "is_correct": true/false,
    "explanation": "Brief explanation of why the answer is correct/incorrect. If incorrect, point out where they went wrong.",
    "normalized_answer": "The canonical form of the final answer (if correct)",
    "understanding_level": "full" if they showed complete work, "partial" if only final answer, "incorrect" if wrong,
    "is_final_answer": true/false
}}"""

    def normalize_math_expression(self, expr: str) -> str:
        """Normalize a math expression by removing spaces and converting to lowercase."""
        # Remove spaces and convert to lowercase
        normalized = ''.join(expr.lower().split())
        # Remove unnecessary characters like '>' or '->' used in step-by-step work
        normalized = normalized.split('>')[-1].split('->')[-1]
        # Split by possible separators to handle multiple equivalent forms
        if '|' in normalized:
            forms = normalized.split('|')
            return [form.strip() for form in forms]
        return normalized

    def check_equivalent_forms(self, expected: str, actual: str) -> bool:
        """Check if the actual answer matches any of the equivalent forms."""
        expected_forms = self.normalize_math_expression(expected)
        actual_norm = self.normalize_math_expression(actual)
        
        if isinstance(expected_forms, list):
            return any(form == actual_norm for form in expected_forms)
        return expected_forms == actual_norm

    def validate_answer(self, step_instruction: str, expected_answer: str, user_answer: str) -> dict:
        """Validate a user's answer against the expected answer using LLM."""
        try:
            # First try basic comparison with equivalent forms
            if self.check_equivalent_forms(expected_answer, user_answer):
                return {
                    "is_correct": True,
                    "explanation": "Correct!",
                    "normalized_answer": expected_answer.split('|')[0],  # Use first form as canonical
                    "understanding_level": "full",
                    "is_final_answer": "x=" in user_answer.lower()
                }

            # If basic comparison fails, use LLM for more sophisticated validation
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": self.validation_prompt.format(
                        step_instruction=step_instruction,
                        expected_answer=expected_answer,
                        user_answer=user_answer
                    )
                }],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
                
            # Fallback to basic string comparison
            return {
                "is_correct": self.check_equivalent_forms(expected_answer, user_answer),
                "explanation": "Basic comparison used",
                "normalized_answer": user_answer,
                "understanding_level": "partial",
                "is_final_answer": "x=" in user_answer.lower()
            }
            
        except Exception as e:
            print(f"Debug - Validation error: {str(e)}")
            # Ultimate fallback
            return {
                "is_correct": self.check_equivalent_forms(expected_answer, user_answer),
                "explanation": "Basic comparison used due to error",
                "normalized_answer": user_answer,
                "understanding_level": "partial",
                "is_final_answer": "x=" in user_answer.lower()
            }
