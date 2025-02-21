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
    
    def process_problem(self, problem_input: str):
        if not isinstance(problem_input, str) or len(problem_input.strip()) == 0:
            raise ValueError("Invalid problem input")

        try:
            # Step 1: Problem Understanding
            analysis = self.problem_analyzer.analyze_problem(problem_input)
            if not isinstance(analysis, dict):
                raise ValueError("Problem analysis returned invalid format")

            # Validate analysis structure
            required_analysis_keys = ['problem_type', 'key_concepts', 'complexity']
            if not all(k in analysis for k in required_analysis_keys):
                raise ValueError(f"Analysis missing required keys: {required_analysis_keys}")

            # Step 2: Knowledge Assessment
            diagnostics = self.knowledge_assessor.generate_diagnostics(
                analysis.get('problem_type', 'unknown')
            )
            
            # Validate diagnostics structure
            if not isinstance(diagnostics.get('knowledge_gaps', []), list):
                raise TypeError("Knowledge gaps should be a list")

            # Step 3: Scaffolding
            learning_path = self.scaffolding_engine.generate_scaffolding(
                concept=analysis.get('problem_type', 'unknown'),
                problem_analysis=analysis,
                knowledge_assessment=diagnostics
            )
            
            # Step 4: Generate Initial Feedback
            feedback = {
                'analysis': analysis,
                'diagnostics': diagnostics,
                'learning_path': learning_path
            }
            
            # Step 5: Plan Reinforcement
            reinforcement = self.reinforcer.generate_reinforcement(
                concept=analysis.get('problem_type', 'unknown'),
                mistakes=diagnostics.get('knowledge_gaps', []),
                retention_score=75.0  # Mock initial score
            )
            
            return {
                'feedback': feedback,
                'reinforcement_schedule': reinforcement
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'advice': "Let's try a different approach to this problem"
            }

if __name__ == '__main__':
    # Example Usage
    tutor = AITutor()
    
    sample_problem = "Solve for x: 2(x + 3) = 4x - 2"
    
    print(f"\n{'='*40}\n AI Tutor System Demo\n{'='*40}")
    print(f"Problem: {sample_problem}")
    
    result = tutor.process_problem(sample_problem)
    
    if 'error' in result:
        print(f"\nError: {result['error']}")
        print(f"Advice: {result['advice']}")
    else:
        print("\nAnalysis:")
        print(f"- Problem Type: {result['feedback']['analysis']['problem_type']}")
        print(f"- Key Concepts: {', '.join(result['feedback']['analysis']['key_concepts'])}")
        
        print("\nRecommended Learning Path:")
        for i, step in enumerate(result['feedback']['learning_path']['steps'], 1):
            print(f"{i}. {step['content']}")
        
        print("\nReinforcement Schedule:")
        print(f"Next Review: {result['reinforcement_schedule']['schedule']['next_review']}")
        print(f"Practice Problems: {len(result['reinforcement_schedule']['practice_set'])}")
