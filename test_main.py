import os
import json
from datetime import datetime
from modules.problem_understanding.analyzer import ProblemUnderstandingEngine
from modules.knowledge_assessment.diagnoser import KnowledgeAssessor
from modules.scaffolding.engine import ScaffoldingEngine
from modules.feedback.feedback_engine import FeedbackEngine
from modules.knowledge_reinforcement.reinforcer import KnowledgeReinforcer
from utils.validation import AnswerValidator

class AITutor:
    def __init__(self):
        self.problem_analyzer = ProblemUnderstandingEngine()
        self.knowledge_assessor = KnowledgeAssessor()
        self.scaffolding_engine = ScaffoldingEngine()
        self.feedback_engine = FeedbackEngine()
        self.reinforcer = KnowledgeReinforcer()
        self.validator = AnswerValidator()
        self.current_step = 0
        self.total_steps = 0
        self.solution_steps = []
        self.max_attempts = 3

    def start_tutoring_session(self):
        print(f"\n{'='*50}")
        print(f"Welcome to AI Math Tutor!")
        print(f"{'='*50}")
        print("I'm here to help you solve math problems step by step.")
        print("Type 'exit' to end the session.")
        
        while True:
            print("\nWhat math problem would you like help with?")
            problem = input("> ").strip()
            
            if problem.lower() == 'exit':
                print("\nThank you for learning with AI Math Tutor! Goodbye!")
                break
            
            self.guide_problem_solution(problem)
    
    def guide_problem_solution(self, problem: str):
        try:
            # Step 1: Analyze the problem
            analysis = self.problem_analyzer.analyze_problem(problem)
            
            print(f"\nI see! This is a {analysis['problem_type']} problem.")
            print("Let's solve it together step by step.")
            print("I'll guide you through each step, and you'll provide the answers.")
            
            # Step 2: Generate solution steps
            self.solution_steps = self.scaffolding_engine.generate_scaffolding(
                concept=analysis['problem_type'],
                problem_analysis=analysis,
                knowledge_assessment={'knowledge_gaps': []},
                problem_text=problem
            )['steps']
            
            self.current_step = 0
            self.total_steps = len(self.solution_steps)
            
            # Guide through each step
            while self.current_step < self.total_steps:
                if not self.handle_step():
                    break
            
            if self.current_step >= self.total_steps:
                print("\n🎉 Congratulations! You've successfully solved the problem!")
                self.suggest_practice()
            
        except Exception as e:
            print(f"\nI apologize, but I'm having trouble with this problem.")
            print(f"Error: {str(e)}")
            print("Let's try a different problem!")
    
    def handle_step(self) -> bool:
        """Handle a single step in the problem-solving process."""
        step = self.solution_steps[self.current_step]
        print(f"\nStep {self.current_step + 1} of {len(self.solution_steps)}:")
        print(step['instruction'])
        
        attempts = 0
        while attempts < self.max_attempts:
            print("\nWhat's your answer? (Type 'hint' for help, 'explain' for detailed explanation, or 'quit' to stop)")
            answer = input("> ").strip()
            
            if answer.lower() == 'quit':
                return False
            elif answer.lower() == 'hint':
                print(f"\n💡 Hint: {step['hint']}")
                continue
            elif answer.lower() == 'explain':
                print(f"\n📚 Detailed Explanation:")
                print(step['explanation'])
                print("\nKey Concepts for this step:")
                continue
            
            # Validate the answer using LLM
            try:
                result = self.validator.validate_answer(
                    step["instruction"],
                    step["expected_answer"],
                    answer
                )
                
                if result["is_correct"]:
                    print("\n✅ Correct! Great job!")
                    
                    # Give extra encouragement for showing work
                    if result.get("understanding_level") == "full":
                        if result.get("is_final_answer"):
                            print("Perfect! You've found the solution!")
                        else:
                            print("Excellent work showing your steps! This is a great way to solve problems.")
                    
                    if result.get("explanation") and result["explanation"] != "Correct!":
                        print(f"({result['explanation']})")
                    
                    print(f"\nExplanation: {step['explanation']}")
                    self.current_step += 1
                    return True
                else:
                    attempts += 1
                    if attempts < self.max_attempts:
                        print(f"\n❌ That's not quite right. You have {self.max_attempts - attempts} more attempts.")
                        if result.get("explanation"):
                            print(f"Hint: {result['explanation']}")
                        print("Would you like another hint? (yes/no)")
                        if input("> ").lower().startswith('y'):
                            print(f"\n💡 Hint: {step['hint']}")
                    else:
                        print("\n❌ Let's look at this step again.")
                        # Show all equivalent forms if they exist
                        expected_forms = step['expected_answer'].split('|')
                        if len(expected_forms) > 1:
                            print("The answer could be written in any of these equivalent forms:")
                            for form in expected_forms:
                                print(f"  • {form}")
                        else:
                            print(f"The correct answer was: {step['expected_answer']}")
                        print(f"Explanation: {step['explanation']}")
                        return False
                        
            except Exception as e:
                print(f"Debug - Validation error: {str(e)}")
                # Fallback to basic string comparison
                if self.validator.check_equivalent_forms(step['expected_answer'], answer):
                    print("\n✅ Correct! Great job!")
                    print(f"\nExplanation: {step['explanation']}")
                    self.current_step += 1
                    return True
                else:
                    attempts += 1
                    if attempts < self.max_attempts:
                        print(f"\n❌ That's not quite right. You have {self.max_attempts - attempts} more attempts.")
                        print("Would you like a hint? (yes/no)")
                        if input("> ").lower().startswith('y'):
                            print(f"\n💡 Hint: {step['hint']}")
                    else:
                        print("\n❌ Let's look at this step again.")
                        print(f"The correct answer was: {step['expected_answer']}")
                        print(f"Explanation: {step['explanation']}")
                        return False
        
        return False
    
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
        if input("> ").lower().strip() == 'yes':
            print("\nHere's a similar problem to try:")
            print(reinforcement['practice_set'][0])

if __name__ == '__main__':
    tutor = AITutor()
    tutor.start_tutoring_session()
