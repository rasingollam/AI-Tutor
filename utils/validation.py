import os
from typing import Dict, Union, Tuple
from groq import Groq
from modules.image_processing.image_processor import ImageProcessor
from utils.logging_utils import validation_logger as logger
import json
import re

class AnswerValidator:
    def __init__(self):
        """Initialize the validator."""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("AnswerValidator initialized")
        
        self.validation_prompt = """
        You are a math tutor validating student answers. Compare the student's answer to the expected answer and provide feedback.
        
        Step instruction: {step_instruction}
        Expected answer: {expected_answer}
        Student answer: {student_answer}
        
        Respond in JSON format:
        {{
            "is_correct": true/false,
            "explanation": "Explanation of what's right/wrong",
            "normalized_answer": "Student answer in standard form",
            "understanding_level": "full/partial/none",
            "is_final_answer": true/false
        }}
        """

    def _is_image_path(self, answer: str) -> bool:
        """Check if the answer is an image path or URL."""
        return (answer.startswith(('http://', 'https://', '/')) or 
                any(answer.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']))

    def normalize_math_expression(self, expr: str) -> Union[str, list]:
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

    def validate_answer(self, step_instruction: str, expected_answer: str, user_answer: str) -> Dict:
        """Validate a user's answer."""
        logger.info(f"\nValidating answer for step: {step_instruction}")
        logger.info(f"Expected answer: {expected_answer}")
        logger.info(f"User answer: {user_answer}")
        
        # First check if this is an image answer
        if os.path.exists(user_answer):
            logger.info(f"Processing image answer: {user_answer}")
            from modules.image_processing.image_processor import ImageProcessor
            image_processor = ImageProcessor()
            result = image_processor.process_image(user_answer, mode="answer")
            
            # Log the raw result for debugging
            logger.info(f"Image processing result: {result}")
            
            if "error" in result:
                logger.error(f"Error processing image: {result['error']}")
                return {
                    "is_correct": False,
                    "explanation": f"Could not process image: {result['error']}",
                    "normalized_answer": None,
                    "understanding_level": "none",
                    "is_final_answer": False
                }
                
            user_answer = result.get("answer_text", "")
            logger.info(f"Extracted answer from image: {user_answer}")
            
        # Try LLM validation first
        try:
            validation = self._validate_with_llm(step_instruction, expected_answer, user_answer)
            logger.info(f"LLM validation result: {validation}")
            return validation
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            # Fallback to basic comparison
            return self._basic_validation(expected_answer, user_answer)

    def _validate_with_llm(self, step_instruction: str, expected_answer: str, student_answer: str) -> Dict:
        """Use LLM to validate answer."""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "user",
                    "content": self.validation_prompt.format(
                        step_instruction=step_instruction,
                        expected_answer=expected_answer,
                        student_answer=student_answer
                    )
                }],
                temperature=0.1,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
            else:
                raise ValueError("No JSON in response")
                
        except Exception as e:
            logger.error(f"LLM validation failed: {str(e)}")
            return self._basic_validation(expected_answer, student_answer)
            
    def _basic_validation(self, expected_answer: str, student_answer: str) -> Dict:
        """Basic string comparison validation."""
        # Normalize answers for comparison
        expected = self._normalize_answer(expected_answer)
        student = self._normalize_answer(student_answer)
        
        is_correct = expected == student
        return {
            "is_correct": is_correct,
            "explanation": "Basic comparison used due to error",
            "normalized_answer": student_answer,
            "understanding_level": "partial",
            "is_final_answer": False
        }
        
    def _normalize_answer(self, answer: str) -> str:
        """Normalize an answer for comparison."""
        # Remove whitespace and convert to lowercase
        normalized = answer.strip().lower()
        
        # Remove unnecessary characters
        normalized = re.sub(r'[,\s]+', '', normalized)
        
        return normalized
