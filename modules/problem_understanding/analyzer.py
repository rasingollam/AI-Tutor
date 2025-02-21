from groq import Groq
import os
from dotenv import load_dotenv
import json
from typing import Dict

class ProblemUnderstandingEngine:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.system_prompt = """Analyze math problems and output structured JSON with:
        - problem_type: (algebra|geometry|calculus)
        - key_entities: list of math symbols/variables
        - complexity: (basic|intermediate|advanced)
        - related_concepts: curriculum mapping"""
        
    def analyze_problem(self, problem_text: str) -> Dict:
        """Analyze math problems with strict JSON validation."""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": self.system_prompt.format(problem=problem_text)
                }],
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            
            # Validate JSON structure
            analysis = json.loads(raw_content)
            required_keys = ['problem_type', 'key_concepts', 'complexity']
            if not all(key in analysis for key in required_keys):
                raise ValueError(f"Missing required keys: {required_keys}")
                
            return analysis
            
        except json.JSONDecodeError:
            raise ValueError("Failed to parse analysis response")
        except Exception as e:
            raise Exception(f"Problem analysis failed: {str(e)}")
