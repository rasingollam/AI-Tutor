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
async def validate_answer(
    step_data: str = Form(...),
    answer: str = Form(None),
    file: UploadFile = None
):
    try:
        step_data_dict = json.loads(step_data)
        
        # Process image if provided
        answer_text = answer or ""
        if file:
            try:
                contents = await file.read()
                image = Image.open(BytesIO(contents))
                
                # Save image temporarily
                temp_path = "temp_answer.jpg"
                image.save(temp_path)
                
                try:
                    # Extract answer from image
                    answer_data = image_processor.process_image(temp_path, mode="answer")
                    if answer_data and isinstance(answer_data, dict):
                        # Extract the answer text from the processed image
                        if 'answer_text' in answer_data:
                            extracted_text = answer_data['answer_text']
                            # Clean up the extracted text
                            if isinstance(extracted_text, str):
                                # Remove any leading/trailing colons and whitespace
                                extracted_text = extracted_text.strip(': ')
                                # Split by commas and take the last equation if multiple are present
                                equations = [eq.strip() for eq in extracted_text.split(',')]
                                answer_text = equations[-1]  # Take the last equation as it's likely the final answer
                            else:
                                answer_text = str(extracted_text)
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            except Exception as img_error:
                print(f"Error processing image: {str(img_error)}")
                # Don't fail completely on image processing error
                answer_text = "Error processing image"
        
        if not answer_text:
            raise HTTPException(
                status_code=400,
                detail="No answer provided in either text or image"
            )
            
        print(f"Validating answer - Expected: {step_data_dict['expected_answer']}, Got: {answer_text}")
        result = answer_validator.validate_answer(
            step_instruction=step_data_dict["instruction"],
            expected_answer=step_data_dict["expected_answer"],
            user_answer=answer_text
        )
        return {"success": True, "validation": result}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in validate_answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
