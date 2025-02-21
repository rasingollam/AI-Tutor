import os
import json
from datetime import datetime
from modules.problem_understanding.analyzer import ProblemAnalyzer
from modules.knowledge_assessment.diagnoser import KnowledgeAssessor
from modules.scaffolding.engine import ScaffoldingEngine
from modules.feedback.feedback_engine import FeedbackEngine
from modules.knowledge_reinforcement.reinforcer import KnowledgeReinforcer
from modules.image_processing.image_processor import ImageProcessor
from utils.validation import AnswerValidator
import logging

logger = logging.getLogger(__name__)

class AITutor:
    def __init__(self):
        self.analyzer = ProblemAnalyzer()
        self.knowledge_assessor = KnowledgeAssessor()
        self.scaffolding_engine = ScaffoldingEngine()
        self.feedback_engine = FeedbackEngine()
        self.validator = AnswerValidator()
        self.image_processor = ImageProcessor()
        self.reinforcer = KnowledgeReinforcer()
        self.current_step = 0
        self.total_steps = 0
        self.solution_steps = []
        self.max_attempts = 3

    def process_user_input(self, user_input: str) -> str:
        """Process user input which can be text or image."""
        try:
            # Check if input is an image path
            if os.path.exists(user_input):
                print("\nProcessing image input...")
                result = self.image_processor.process_image(user_input, mode="problem")
                
                if result and result.get("problem_text"):
                    problem = result["problem_text"]
                    print(f"Extracted problem: {problem}")
                    if result.get("problem_type"):
                        print(f"Problem type: {result['problem_type']}")
                    if result.get("additional_context"):
                        print(f"Additional context: {result['additional_context']}")
                    return problem
                else:
                    print("Could not extract a valid problem from the image.")
                    return ""
            else:
                # Direct text input
                return user_input.strip()
                
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}", exc_info=True)
            print(f"\nI had trouble processing that input. Please try again.")
            return ""

    def start_tutoring_session(self):
        print(f"\n{'='*50}")
        print(f"Welcome to AI Math Tutor!")
        print(f"{'='*50}")
        print("I'm here to help you solve math problems step by step.")
        print("Type 'exit' or 'quit' to end the session.")
        
        while True:
            print("\nWhat math problem would you like help with?")
            print("(You can type a problem or provide an image path/URL)")
            user_input = input("> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\nThank you for learning with AI Math Tutor! Goodbye!")
                break
                
            problem = self.process_user_input(user_input)
            if not problem:
                continue
            
            self.guide_problem_solution(problem)
    
    def guide_problem_solution(self, problem: str):
        try:
            # Step 1: Analyze the problem
            analysis = self.analyzer.analyze_problem(problem)
            
            # Handle different problem types
            problem_type = analysis.get('problem_type', 'linear_equation').lower()
            if 'quadratic' in problem_type:
                problem_type = 'quadratic_equation'
            elif 'system' in problem_type:
                problem_type = 'system_of_equations'
            else:
                problem_type = 'linear_equation'
            
            print(f"\nI see! This is a {problem_type} problem.")
            print("Let's solve it together step by step.")
            print("I'll guide you through each step, and you'll provide the answers.\n")
            
            # Step 2: Get solution steps
            self.solution_steps = self.scaffolding_engine.generate_solution_steps(problem)
            if not self.solution_steps:
                print("I apologize, but I'm having trouble generating steps for this problem.")
                print("Let's try another problem!")
                return
                
            self.total_steps = len(self.solution_steps)
            if self.total_steps == 0:
                print("I apologize, but I couldn't generate steps for this problem.")
                print("Let's try another problem!")
                return
            
            # Step 3: Guide through each step
            for i, step in enumerate(self.solution_steps, 1):
                print(f"Step {i} of {self.total_steps}:")
                print(step["instruction"])
                print("\nWhat's your answer? (Type 'hint' for help, 'explain' for detailed explanation, or 'quit' to stop)")
                
                attempts = 0
                max_attempts = 3
                while attempts < max_attempts:
                    answer = input("> ").strip().lower()
                    
                    if answer in ['quit', 'exit']:
                        return
                    elif answer == 'hint':
                        print(f"\n💡 Hint: {step['hint']}")
                        print("\nWhat's your answer?")
                        continue
                    elif answer == 'explain':
                        print(f"\n📝 Explanation: {step['explanation']}")
                        print("\nWhat's your answer?")
                        continue
                        
                    # Validate the answer
                    validation = self.validator.validate_answer(
                        step_instruction=step["instruction"],
                        expected_answer=step["expected_answer"],
                        user_answer=answer
                    )
                    
                    if validation["is_correct"]:
                        print("\n✅ Correct! Great job!")
                        if validation.get("understanding_level") == "full":
                            print("Perfect! You've found the solution!")
                        else:
                            print("Excellent work showing your steps! This is a great way to solve problems.")
                        print(f"({validation['explanation']})")
                        print(f"\nExplanation: {step['explanation']}")
                        break
                    else:
                        attempts += 1
                        if attempts < max_attempts:
                            print(f"\n❌ That's not quite right. You have {max_attempts - attempts} more attempts.")
                            print(f"Hint: {validation['explanation']}")
                            print("Would you like another hint? (yes/no)")
                            if input("> ").strip().lower() == 'yes':
                                print(f"\n💡 Hint: {step['hint']}")
                            print("\nWhat's your answer? (Type 'hint' for help, 'explain' for detailed explanation, or 'quit' to stop)")
                        else:
                            print(f"\n❌ The correct answer was: {step['expected_answer']}")
                            print(f"Explanation: {step['explanation']}")
                            if i < len(self.solution_steps):
                                print("\nLet's continue with the next step.")
                
            print("\n🎉 Congratulations! You've successfully solved the problem!")
            
            # Step 4: Offer practice
            print("\nWould you like to try a similar problem for practice? (yes/no)")
            practice_response = input("> ").strip().lower()
            if practice_response == 'yes':
                practice_problem = {
                    "problem": "2(x + 3) = 8",
                    "type": problem_type
                }
                print("\nHere's a similar problem to try:")
                print(practice_problem["problem"])
                
        except Exception as e:
            logger.error(f"Error in guide_problem_solution: {str(e)}", exc_info=True)
            print("\nI apologize, but I'm having trouble with this problem.")
            print("Let's try another one!")

    def check_answer(self, user_answer: str, expected_answer: str) -> bool:
        """Compare user's answer with expected answer."""
        # Remove spaces and convert to lowercase for comparison
        user_answer = user_answer.replace(' ', '').lower()
        expected_answer = str(expected_answer).replace(' ', '').lower()
        
        # Handle multiple correct forms of the same answer
        if '|' in expected_answer:
            return user_answer in [ans.strip() for ans in expected_answer.split('|')]
        
        return user_answer == expected_answer
    
    def show_hint(self, step: dict):
        """Show a hint for the current step."""
        print("\n💡 Hint:", step.get('hint', 'Think about what we learned in the previous steps.'))
    
    def explain_step_in_detail(self, step: dict):
        """Provide detailed explanation of the current step."""
        print("\n📚 Detailed Explanation:")
        print(step.get('detailed_explanation', step.get('explanation', step['instruction'])))
        print("\nKey Concepts for this step:")
        for concept in step.get('key_concepts', []):
            print(f"- {concept}")
    
    def provide_additional_help(self, step: dict):
        """Provide additional help when student is stuck."""
        print("\n1. Let's break down the problem into smaller parts:")
        for i, part in enumerate(step.get('breakdown', ['No detailed breakdown available']), 1):
            print(f"   {i}. {part}")
        
        print("\n2. Common mistakes to avoid:")
        for mistake in step.get('common_mistakes', ['No common mistakes listed']):
            print(f"   • {mistake}")
        
        print("\n3. Tips:")
        for tip in step.get('tips', ['Take your time', 'Write down each step', 'Check your work']):
            print(f"   • {tip}")
    
    def suggest_practice(self):
        reinforcement = self.reinforcer.generate_reinforcement(
            concept=self.solution_steps[0].get('concept', 'unknown'),
            mistakes=[],
            retention_score=75.0
        )
        
        print("\nWould you like to try a similar problem for practice? (yes/no)")
        if input("> ").strip().lower() == 'yes':
            print("\nHere's a similar problem to try:")
            print(reinforcement['practice_set'][0])

if __name__ == '__main__':
    tutor = AITutor()
    tutor.start_tutoring_session()
