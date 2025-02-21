import os
import json
from datetime import datetime
from modules.problem_understanding.analyzer import ProblemUnderstandingEngine
from modules.knowledge_assessment.diagnoser import KnowledgeAssessor
from modules.scaffolding.engine import ScaffoldingEngine
from modules.feedback.feedback_engine import FeedbackEngine
from modules.knowledge_reinforcement.reinforcer import KnowledgeReinforcer

class AITutor:
    def __init__(self):
        self.problem_analyzer = ProblemUnderstandingEngine()
        self.knowledge_assessor = KnowledgeAssessor()
        self.scaffolding_engine = ScaffoldingEngine()
        self.feedback_engine = FeedbackEngine()
        self.reinforcer = KnowledgeReinforcer()
        self.current_step = 0
        self.total_steps = 0
        self.solution_steps = []
    
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
        """Handle a single step of the problem-solving process.
        Returns False if user wants to quit, True otherwise."""
        step = self.solution_steps[self.current_step]
        
        print(f"\nStep {self.current_step + 1} of {self.total_steps}:")
        print(step['instruction'])
        
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            print("\nWhat's your answer? (Type 'hint' for help, 'explain' for detailed explanation, or 'quit' to stop)")
            answer = input("> ").strip().lower()
            
            if answer == 'quit':
                return False
            elif answer == 'hint':
                self.show_hint(step)
                continue
            elif answer == 'explain':
                self.explain_step_in_detail(step)
                continue
            
            if self.check_answer(answer, step['expected_answer']):
                print("\n✅ Correct! Great job!")
                if step.get('explanation'):
                    print(f"\nExplanation: {step['explanation']}")
                self.current_step += 1
                return True
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"\n❌ That's not quite right. You have {remaining} more attempts.")
                    print("Would you like a hint? (yes/no)")
                    if input("> ").strip().lower() == 'yes':
                        self.show_hint(step)
        
        # If we get here, user has used all attempts
        print("\nLet me help you with this step.")
        print(f"The correct answer is: {step['expected_answer']}")
        print("\nLet's understand why:")
        self.explain_step_in_detail(step)
        print("\nDo you understand now? Type 'yes' to continue or 'no' for more help.")
        
        while True:
            response = input("> ").strip().lower()
            if response == 'yes':
                self.current_step += 1
                return True
            elif response == 'no':
                print("\nLet's break it down further:")
                self.provide_additional_help(step)
                print("\nReady to continue? (yes/no)")
            else:
                print("Please type 'yes' or 'no'")
    
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
