import os
import json
from groq import Groq
from typing import Dict, List

class ScaffoldingEngine:
    """Generates adaptive learning paths based on problem understanding and knowledge assessment."""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.scaffolding_prompt = """Create a personalized learning path for a student struggling with {concept}.

Analysis Input:
{problem_analysis}

Knowledge Assessment:
{knowledge_assessment}

Output a JSON structure with:
{{
    "learning_objectives": ["list of specific objectives"],
    "steps": [
        {{
            "type": "explanation|example|practice",
            "content": "instructional content",
            "resources": ["relevant resources"],
            "checkpoint_question": "question to verify understanding"
        }}
    ],
    "adaptation_rules": {{
        "success": "next steps for mastery",
        "struggle": "remediation strategies"
    }}
}}"""

    def generate_scaffolding(self, 
                            concept: str,
                            problem_analysis: Dict,
                            knowledge_assessment: Dict) -> Dict:
        """Generate adaptive learning path."""
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "system",
                    "content": self.scaffolding_prompt.format(
                        concept=concept,
                        problem_analysis=json.dumps(problem_analysis),
                        knowledge_assessment=json.dumps(knowledge_assessment)
                    )
                }],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Scaffolding generation failed: {str(e)}")

    def adapt_path(self, progress_data: Dict) -> Dict:
        """Adjust learning path based on student progress."""
        # Implementation for dynamic adaptation
        pass
