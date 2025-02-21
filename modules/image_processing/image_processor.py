import os
import base64
from groq import Groq
from typing import Dict, Union
from utils.logging_utils import image_logger as logger
import re
from PIL import Image
import io
import json
from io import BytesIO

class ImageProcessor:
    def __init__(self):
        """Initialize the image processor."""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("ImageProcessor initialized")
        
        self.answer_prompt = """You are a math answer extractor. Look at this image and:
1. Find the mathematical answer or step shown
2. Extract it exactly as written
3. Convert any handwritten or printed text into a clear digital format
4. If multiple steps are shown, focus on the final answer

Return a JSON response in this format:
{
    "problem_text": "The exact mathematical answer/step from the image",
    "answer_type": "step|final",  # Whether this is an intermediate step or final answer
    "confidence": 0.0-1.0  # How confident you are in the extraction
}"""

        self.image_prompt = """You are a math problem extractor. Look at this image and:
1. Find any mathematical equations, expressions, or word problems
2. Extract them exactly as written
3. Identify the type of problem (e.g., linear equation, arithmetic, etc.)
4. Convert any handwritten or printed text into a clear digital format

Return a JSON response in this format:
{
    "problem_text": "The exact math problem from the image",
    "problem_type": "The type of mathematical problem",
    "additional_context": "Any relevant context or special instructions"
}"""

    def _resize_image(self, image_path: str, max_size: int = 400) -> bytes:
        """Resize image to reduce token count while maintaining readability."""
        with Image.open(image_path) as img:
            # Convert to grayscale for math problems
            img = img.convert('L')
            
            # Calculate new dimensions
            ratio = min(max_size / max(img.size), 1.0)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            
            # Resize image
            if ratio < 1.0:
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=75)
            return buffer.getvalue()
            
    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string."""
        try:
            # Resize image first
            image_data = self._resize_image(image_path)
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise

    def _extract_content(self, image_path: str, mode: str = "problem") -> Dict:
        """Extract content from image using Groq's vision model."""
        try:
            # Read image as base64
            image_base64 = self.encode_image_to_base64(image_path)
            
            # Create message with proper image format
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract the math problem from this image and return in JSON format:
                        {
                            "problem_text": "exact math problem",
                            "problem_type": "type",
                            "additional_context": "details"
                        }"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
            
            # Make API call
            response = self.client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[user_message],
                temperature=0.1,
                max_tokens=200
            )
            
            # Extract and parse JSON from response
            result = response.choices[0].message.content.strip()
            logger.debug(f"Raw vision model response: {result}")
            
            # Try to find JSON in the response
            try:
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    return json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Could not parse JSON from response: {result}")
                # Return default structure based on mode
                if mode == "problem":
                    return {
                        "problem_text": self._extract_problem_text(result),
                        "problem_type": "Unknown",
                        "additional_context": "Error processing image"
                    }
                else:
                    return {
                        "answer_text": self._extract_answer_text(result),
                        "detail_level": "Unknown",
                        "work_shown": "Error processing image"
                    }
                    
        except Exception as e:
            logger.error(f"Error in _extract_content: {str(e)}", exc_info=True)
            if mode == "problem":
                return {
                    "problem_text": "",
                    "problem_type": "Unknown",
                    "additional_context": f"Error: {str(e)}"
                }
            else:
                return {
                    "answer_text": "",
                    "detail_level": "Unknown",
                    "work_shown": f"Error: {str(e)}"
                }

    def _extract_problem_text(self, text: str) -> str:
        """Extract problem text from non-JSON response."""
        try:
            # Look for common patterns
            patterns = [
                r"problem in the image is:\s*\n*\s*([^\n]+)",
                r"math problem is:\s*\n*\s*([^\n]+)",
                r"equation is:\s*\n*\s*([^\n]+)",
                r"problem text[:\s]+([^\n]+)",
                r"math problem[:\s]+([^\n]+)",
                r"equation[:\s]+([^\n]+)",
                r"problem[:\s]+([^\n]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    problem = match.group(1).strip()
                    if any(c in problem for c in '=+-*/()'):
                        return problem
                    
            # If no pattern matches, try to find equation-like text
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if any(c in line for c in '=+-*/()'):
                    return line
                    
            return ""
        except Exception as e:
            logger.error(f"Error extracting problem text: {str(e)}")
            return ""
            
    def _extract_answer_text(self, text: str) -> str:
        """Extract answer text from non-JSON response."""
        try:
            # Look for common patterns
            patterns = [
                r"answer[:\s]+([^\n]+)",
                r"solution[:\s]+([^\n]+)",
                r"result[:\s]+([^\n]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    return match.group(1).strip()
                    
            # If no pattern matches, try to find equation-like text
            lines = text.split('\n')
            for line in lines:
                if any(c in line for c in '=+-*/()'):
                    return line.strip()
                    
            return ""
        except Exception as e:
            logger.error(f"Error extracting answer text: {str(e)}")
            return ""

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown formatting from text."""
        # Remove markdown headers
        text = re.sub(r'\*\*.*?\*\*', '', text)
        
        # Remove bullet points
        text = re.sub(r'^\s*\*\s*', '', text, flags=re.MULTILINE)
        
        # Remove other markdown formatting
        text = re.sub(r'\*\*|\*', '', text)
        
        # Extract actual equation/answer if present
        if "Problem Text:" in text:
            match = re.search(r'Problem Text:(.+?)(?=Problem Type:|$)', text, re.DOTALL)
            if match:
                text = match.group(1)
        elif "Answer Text:" in text:
            match = re.search(r'Answer Text:(.+?)(?=Explanation:|$)', text, re.DOTALL)
            if match:
                text = match.group(1)
                
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def process_image(self, image_path: str, mode: str = "problem") -> Dict:
        """Process an image and extract text/math content."""
        logger.info(f"Processing image: {image_path} in {mode} mode")
        
        try:
            # Open and resize image
            image = Image.open(image_path)
            logger.info(f"Original image size: {image.size}")
            
            # Resize if needed
            if image.size[0] > 400 or image.size[1] > 400:
                ratio = min(400/image.size[0], 400/image.size[1])
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to: {new_size}")
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Save as JPEG with reduced quality
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=75)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            logger.info("Image converted and encoded")
            
            # Prepare prompt based on mode
            if mode == "problem":
                prompt = """You are a math problem extractor. Look at this image and extract ONLY the math problem.
                Return your response in this EXACT JSON format:
                {
                    "problem_text": "write the exact math problem here",
                    "problem_type": "linear_equation/quadratic/word_problem/etc",
                    "additional_context": "any additional instructions or context"
                }"""
            else:
                prompt = """You are a math answer extractor. Look at this image and extract ONLY the mathematical answer/work shown.
                Return your response in this EXACT JSON format:
                {
                    "answer_text": "write the exact mathematical answer/expression here",
                    "explanation": "briefly explain the work shown",
                    "confidence": 0.95
                }"""
                
            logger.info(f"Using prompt: {prompt}")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_str}",
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            logger.info(f"Raw API response: {result}")
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response
                start = result.find('{')
                end = result.rfind('}') + 1
                
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    logger.info(f"Extracted JSON string: {json_str}")
                    data = json.loads(json_str)
                    
                    if mode == "problem":
                        problem_text = self._clean_markdown(data.get("problem_text", ""))
                        extracted = {
                            "problem_text": problem_text,
                            "problem_type": data.get("problem_type", "unknown"),
                            "additional_context": data.get("additional_context", "")
                        }
                    else:
                        answer_text = self._clean_markdown(data.get("answer_text", ""))
                        extracted = {
                            "answer_text": answer_text,
                            "explanation": data.get("explanation", ""),
                            "confidence": data.get("confidence", 0.0)
                        }
                    logger.info(f"Extracted content: {extracted}")
                    return extracted
                else:
                    # If no JSON found, try to extract problem directly
                    clean_text = self._clean_markdown(result)
                    if mode == "problem":
                        extracted = {
                            "problem_text": clean_text,
                            "problem_type": "unknown",
                            "additional_context": ""
                        }
                    else:
                        extracted = {
                            "answer_text": clean_text,
                            "explanation": "",
                            "confidence": 0.5
                        }
                    logger.info(f"Extracted content (no JSON): {extracted}")
                    return extracted
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Invalid JSON string: {json_str}")
                return {"error": "Failed to parse response"}
                
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return {"error": str(e)}
            
    def _get_problem_prompt(self) -> str:
        """Get prompt for problem extraction."""
        return """Extract the math problem from this image. Respond in JSON format:
        {
            "problem_text": "The complete math problem as written",
            "problem_type": "The type of math problem (e.g. linear_equation, quadratic, word_problem, etc)",
            "additional_context": "Any additional context or instructions shown"
        }"""
        
    def _get_answer_prompt(self) -> str:
        """Get prompt for answer extraction."""
        return """Extract the mathematical answer from this image. Respond in JSON format:
        {
            "answer_text": "The complete mathematical answer/expression",
            "explanation": "Brief explanation of the work shown",
            "confidence": 0.95
        }"""
