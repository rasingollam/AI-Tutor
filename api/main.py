from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
from pathlib import Path

# Add parent directory to Python path to import modules
api_dir = Path(__file__).resolve().parent
root_dir = api_dir.parent
sys.path.append(str(root_dir))

from modules.scaffolding.engine import ScaffoldingEngine
from modules.image_processing.image_processor import ImageProcessor
from utils.validation import AnswerValidator
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Math Tutor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
scaffolding_engine = ScaffoldingEngine()
image_processor = ImageProcessor()
answer_validator = AnswerValidator()

@app.get("/")
async def root():
    return {"message": "AI Math Tutor API is running"}

@app.post("/process-text-problem")
async def process_text_problem(problem: str):
    try:
        steps = scaffolding_engine.generate_scaffolding(
            concept="unknown",
            problem_analysis="",
            knowledge_assessment="",
            problem_text=problem
        )
        return {"success": True, "steps": steps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-image-problem")
async def process_image_problem(file: UploadFile = File(...)):
    try:
        # Read and process the image
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        # Extract problem from image
        problem_data = image_processor.process_image(image, mode="problem")
        
        if problem_data:
            # Generate steps
            steps = scaffolding_engine.generate_scaffolding(
                concept="unknown",
                problem_analysis="",
                knowledge_assessment="",
                problem_text=problem_data["problem_text"]
            )
            return {
                "success": True,
                "problem": problem_data["problem_text"],
                "steps": steps
            }
        raise HTTPException(status_code=400, detail="Could not extract problem from image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate-answer")
async def validate_answer(step_data: dict, answer: str):
    try:
        result = answer_validator.validate_answer(
            step_instruction=step_data["instruction"],
            expected_answer=step_data["expected_answer"],
            user_answer=answer
        )
        return {"success": True, "validation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
