from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
from pathlib import Path
import json
from typing import Optional

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

# Configure CORS with more permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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
        
        # Save image temporarily
        temp_path = "temp_image.jpg"
        image.save(temp_path)
        
        try:
            # Extract problem from image
            problem_data = image_processor.process_image(temp_path, mode="problem")
            
            if problem_data and "problem_text" in problem_data:
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
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not extract valid problem text from image"
                )
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/process-combined-problem")
async def process_combined_problem(
    file: Optional[UploadFile] = None,
    text: Optional[str] = Form(None)
):
    try:
        problem_text = text or ""
        
        if file:
            # Read and process the image
            contents = await file.read()
            image = Image.open(BytesIO(contents))
            
            # Save image temporarily
            temp_path = "temp_image.jpg"
            image.save(temp_path)
            
            try:
                # Extract problem from image
                problem_data = image_processor.process_image(temp_path, mode="problem")
                
                if problem_data and "problem_text" in problem_data:
                    # Combine text and image problem
                    if problem_text:
                        problem_text = f"{problem_text}\n{problem_data['problem_text']}"
                    else:
                        problem_text = problem_data["problem_text"]
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        if not problem_text:
            raise HTTPException(
                status_code=400,
                detail="No problem text provided in either text or image"
            )
            
        # Generate steps
        steps = scaffolding_engine.generate_scaffolding(
            concept="unknown",
            problem_analysis="",
            knowledge_assessment="",
            problem_text=problem_text
        )
        return {
            "success": True,
            "problem": problem_text,
            "steps": steps
        }
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing problem: {str(e)}"
        )

@app.post("/validate-answer")
async def validate_answer(step_data: str = Form(...), answer: str = Form(...)):
    try:
        step_data_dict = json.loads(step_data)
        result = answer_validator.validate_answer(
            step_instruction=step_data_dict["instruction"],
            expected_answer=step_data_dict["expected_answer"],
            user_answer=answer
        )
        return {"success": True, "validation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
