import os
import json
from groq import Groq
from typing import Dict, List
from utils.logging_utils import validation_logger as logger

class ScaffoldingEngine:
    """Generates adaptive learning paths based on problem understanding and knowledge assessment."""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("ScaffoldingEngine initialized")
        
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
5. Pay careful attention to signs (+ and -) in equations

For each step, provide:
- instruction: Clear, specific instruction about what to do AND what the result should look like
- expected_answer: The answer for this specific step (include alternate forms if applicable)
- hint: A helpful hint that guides without giving away the answer
- explanation: Why this step is important and how it helps solve the problem

IMPORTANT:
1. Pay careful attention to signs (+ and -) when moving terms
2. Double-check all arithmetic
3. Make sure each step follows logically from the previous one
4. Verify that the final answer is correct by substituting it back into the original equation
5. Return ONLY the JSON object without any markdown formatting or explanatory text

Example format (but create steps for the GIVEN problem):
{
    "steps": [
        {
            "instruction": "Move all x terms to the left side by subtracting 4x from both sides. You should get: -2x + 6 = -2",
            "expected_answer": "-2x + 6 = -2|-2x+6=-2|6-2x=-2",
            "hint": "When moving terms, remember to change their signs",
            "explanation": "Grouping like terms (terms with x) on one side makes it easier to solve for x"
        }
    ]
}"""

    def generate_solution_steps(self, problem: str) -> List[Dict]:
        """Generate solution steps for a problem."""
        logger.info(f"Generating solution steps for: {problem}")
        
        try:
            # Create a basic analysis for the problem
            analysis = {
                "problem_type": "linear_equation",  # Default to linear equation
                "key_concepts": ["equation_solving"],
                "complexity": "basic"
            }
            
            # Generate scaffolding
            scaffolding = self.generate_scaffolding(
                concept=analysis["problem_type"],
                problem_analysis=json.dumps(analysis),
                knowledge_assessment=json.dumps({"knowledge_gaps": []}),
                problem_text=problem
            )
            
            if isinstance(scaffolding, dict) and "steps" in scaffolding:
                logger.info(f"Generated {len(scaffolding['steps'])} solution steps")
                return scaffolding["steps"]
            else:
                logger.error(f"Invalid scaffolding format: {scaffolding}")
                # Return default steps if something goes wrong
                return [
                    {
                        "instruction": "First, let's understand what we're solving for.",
                        "expected_answer": problem,
                        "hint": "Read the problem carefully and identify the variable.",
                        "explanation": "Understanding the problem is the first step to solving it."
                    }
                ]
                
        except Exception as e:
            logger.error(f"Error generating solution steps: {str(e)}", exc_info=True)
            # Return a simple error step
            return [
                {
                    "instruction": "There was an error generating steps. Let's try a simpler approach.",
                    "expected_answer": problem,
                    "hint": "Start by writing out what you know.",
                    "explanation": "Sometimes breaking down a problem helps us solve it."
                }
            ]

    def generate_scaffolding(self, 
                           concept: str,
                           problem_analysis: str,
                           knowledge_assessment: str,
                           problem_text: str) -> Dict:
        """Generate scaffolding steps for the given problem."""
        logger.debug(f"Generating scaffolding for concept: {concept}")
        try:
            prompt = f"""Create a step-by-step solution guide for this math problem.

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
5. Pay careful attention to signs (+ and -) in equations

For each step, provide:
- instruction: Clear, specific instruction about what to do AND what the result should look like
- expected_answer: The answer for this specific step (include alternate forms if applicable)
- hint: A helpful hint that guides without giving away the answer
- explanation: Why this step is important and how it helps solve the problem

IMPORTANT:
1. Pay careful attention to signs (+ and -) when moving terms
2. Double-check all arithmetic
3. Make sure each step follows logically from the previous one
4. Verify that the final answer is correct by substituting it back into the original equation
5. Return ONLY the JSON object without any markdown formatting or explanatory text

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
}}

Respond with ONLY a valid JSON object containing the steps. Do not include any markdown formatting or explanatory text."""
            
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "system",
                    "content": prompt
                }],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            logger.debug(f"Raw scaffolding response: {result}")
            
            # Remove any markdown code blocks and find JSON
            result = result.replace('```json', '').replace('```', '').strip()
            
            try:
                # First try direct JSON parsing
                try:
                    data = json.loads(result)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from the response
                    start = result.find('{')
                    end = result.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = result[start:end]
                        data = json.loads(json_str)
                    else:
                        raise ValueError("No JSON found in response")
                
                # Validate steps
                if "steps" in data:
                    for step in data["steps"]:
                        # Ensure all required fields are present
                        required_fields = ["instruction", "expected_answer", "hint", "explanation"]
                        if not all(field in step for field in required_fields):
                            raise ValueError("Missing required fields in step")
                            
                        # Validate that the step makes mathematical sense
                        if "=" in step["expected_answer"]:
                            parts = step["expected_answer"].split("=")
                            if len(parts) < 2:  
                                raise ValueError("Invalid equation format")
                                
                    logger.info(f"Generated valid scaffolding with {len(data['steps'])} steps")
                    return data
                    
                else:
                    raise ValueError("No steps found in response")
                    
            except Exception as e:
                logger.error(f"Invalid JSON in scaffolding response: {result}")
                
            # If we get here, return default steps
            return {
                "steps": [
                    {
                        "instruction": "Let's solve this step by step.",
                        "expected_answer": problem_text,
                        "hint": "Start by identifying what we're solving for.",
                        "explanation": "Breaking down the problem helps us solve it."
                    },
                    {
                        "instruction": "Now, let's solve the equation.",
                        "expected_answer": problem_text,
                        "hint": "Follow the order of operations (PEMDAS).",
                        "explanation": "Solving equations requires following mathematical rules."
                    }
                ]
            }
                
        except Exception as e:
            logger.error(f"Error in generate_scaffolding: {str(e)}", exc_info=True)
            return {
                "steps": [
                    {
                        "instruction": "Let's solve this step by step.",
                        "expected_answer": problem_text,
                        "hint": "Start by identifying what we're solving for.",
                        "explanation": "Breaking down the problem helps us solve it."
                    }
                ]
            }

    def adapt_path(self, progress_data: Dict) -> Dict:
        """Adjust learning path based on student progress."""
        # Implementation for dynamic adaptation
        pass
