from fastapi import APIRouter, HTTPException
from app.services.ai_analyzer import AIAnalyzer
from app.core.config import settings
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI analyzer
ai_analyzer = AIAnalyzer()

# Request models
class JobDescriptionRequest(BaseModel):
    description: str
    title: Optional[str] = None
    company: Optional[str] = None

class ResumeTextRequest(BaseModel):
    resume_text: str
    job_context: Optional[Dict] = None

@router.post("/analyze-job")
async def analyze_job_description(
    request: JobDescriptionRequest
) -> Dict[str, Any]:
    """
    Analyze job description and extract structured requirements using Google Gemini
    
    This endpoint:
    1. Takes job description text
    2. Uses Google Gemini to extract required skills, experience, education
    3. Returns structured data for matching against resumes
    """
    
    logger.info(f"🔍 Analyzing job description: {request.title or 'Untitled Job'}")
    
    try:
        if not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty"
            )
        
        # Analyze with Google Gemini
        analysis = await ai_analyzer.analyze_job_description(request.description)
        
        result = {
            "status": "success",
            "job_title": request.title,
            "company": request.company,
            "analysis": analysis,
            "ai_provider": "google_gemini",
            "message": "Job description analyzed successfully with Google Gemini"
        }
        
        logger.info("✅ Job analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing job description: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing job description: {str(e)}"
        )

@router.post("/analyze-resume-text")
async def analyze_resume_text(
    request: ResumeTextRequest
) -> Dict[str, Any]:
    """
    Analyze resume text and extract structured information using Google Gemini
    
    This endpoint:
    1. Takes resume text content
    2. Uses Google Gemini to extract candidate information
    3. Returns structured candidate profile
    """
    
    logger.info("🔍 Analyzing resume text with Google Gemini")
    
    try:
        if not request.resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Resume text cannot be empty"
            )
        
        # Analyze with Google Gemini
        analysis = await ai_analyzer.analyze_resume_content(
            request.resume_text,
            request.job_context
        )
        
        result = {
            "status": "success",
            "analysis": analysis,
            "text_length": len(request.resume_text),
            "ai_provider": "google_gemini", 
            "message": "Resume analyzed successfully with Google Gemini"
        }
        
        logger.info("✅ Resume analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )

@router.get("/ai-status")
async def get_ai_status():
    """Check Google Gemini AI service status and test connection"""
    
    logger.info("🔍 Checking Google Gemini AI status")
    
    # Test Google Gemini connection
    connection_test = await ai_analyzer.test_connection()
    
    return {
        "current_provider": "google_gemini",
        "google_api_configured": bool(settings.google_api_key),
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
        "model": "gemini-1.5-flash",
        "connection_test": connection_test,
        "status": "ready" if connection_test.get("status") == "connected" else "not_ready"
    }