from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import mimetypes
from app.services.document_parser import DocumentParser
from app.services.ai_analyzer import AIAnalyzer
from app.services.scoring_engine import ScoringEngine
from app.core.config import settings
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import json
import os

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Resume Screening AI",
    description="AI-powered resume screening and scoring system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router for scoring endpoints
router = APIRouter()

# Initialize services
document_parser = DocumentParser()
ai_analyzer = AIAnalyzer()
scoring_engine = ScoringEngine()

# Request models
class ScoreResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: Optional[str] = None
    filename: Optional[str] = "resume.pdf"

class BatchScoreRequest(BaseModel):
    job_description: str
    job_title: Optional[str] = None

@router.post("/score-resume-text")
async def score_resume_from_text(
    request: ScoreResumeRequest
) -> Dict[str, Any]:
    """
    Score a resume (provided as text) against a job description
    
    This endpoint:
    1. Analyzes the job description to extract requirements
    2. Scores the resume text against those requirements  
    3. Returns detailed scoring breakdown with recommendations
    """
    
    logger.info(f"🔍 Scoring resume text against job: {request.job_title or 'Untitled'}")
    
    try:
        if not request.resume_text.strip():
            raise HTTPException(status_code=400, detail="Resume text cannot be empty")
        
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty")
        
        # Step 1: Analyze job description
        logger.info("📋 Analyzing job requirements...")
        job_analysis = await ai_analyzer.analyze_job_description(request.job_description)
        
        # Step 2: Score resume against job
        logger.info("🎯 Scoring resume against requirements...")
        scoring_result = await scoring_engine.score_resume_against_job(
            request.resume_text,
            job_analysis,
            request.filename
        )
        
        # Step 3: Add job context to response
        result = {
            "status": "success",
            "job_title": request.job_title,
            "job_analysis": job_analysis,
            "scoring_result": scoring_result,
            "message": f"Resume scored successfully. Overall score: {scoring_result['overall_score']}/100"
        }
        
        logger.info(f"✅ Resume scoring completed: {scoring_result['overall_score']}/100")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error scoring resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error scoring resume: {str(e)}"
        )

@router.post("/score-resume-file")
async def score_resume_from_file(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Score an uploaded resume file against a job description
    
    This endpoint:
    1. Parses the uploaded resume file (PDF/Word)
    2. Analyzes the job description
    3. Scores the resume and returns detailed results
    """
    
    logger.info(f"📄 Scoring uploaded resume: {file.filename}")
    
    try:
        # Step 1: Parse uploaded resume
        logger.info("📄 Parsing resume file...")
        resume_text = await document_parser.parse_document(file)
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume file"
            )
        
        # Step 2: Analyze job description
        logger.info("📋 Analyzing job requirements...")
        job_analysis = await ai_analyzer.analyze_job_description(job_description)
        
        # Step 3: Score resume
        logger.info("🎯 Scoring resume against requirements...")
        scoring_result = await scoring_engine.score_resume_against_job(
            resume_text,
            job_analysis,
            file.filename
        )
        
        result = {
            "status": "success",
            "job_title": job_title,
            "job_analysis": job_analysis,
            "scoring_result": scoring_result,
            "resume_preview": resume_text[:300] + "..." if len(resume_text) > 300 else resume_text,
            "message": f"Resume scored successfully. Overall score: {scoring_result['overall_score']}/100"
        }
        
        logger.info(f"✅ File-based resume scoring completed: {scoring_result['overall_score']}/100")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error scoring resume file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume file: {str(e)}"
        )

@router.post("/batch-score-resumes")
async def batch_score_resumes(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    job_title: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Score multiple resume files against a job description (batch processing)
    
    This endpoint:
    1. Parses multiple resume files
    2. Analyzes the job description once
    3. Scores all resumes and returns ranked results
    """
    
    logger.info(f"📦 Batch scoring {len(files)} resumes against job: {job_title or 'Untitled'}")
    
    try:
        if len(files) > 20:  # Reasonable limit for batch processing
            raise HTTPException(
                status_code=400,
                detail="Too many files. Maximum 20 resumes per batch."
            )
        
        # Step 1: Analyze job description once
        logger.info("📋 Analyzing job requirements...")
        job_analysis = await ai_analyzer.analyze_job_description(job_description)
        
        # Step 2: Parse all resume files
        logger.info(f"📄 Parsing {len(files)} resume files...")
        resume_data_list = []
        
        for file in files:
            try:
                resume_text = await document_parser.parse_document(file)
                if resume_text.strip():
                    resume_data_list.append({
                        "text": resume_text,
                        "filename": file.filename
                    })
                else:
                    logger.warning(f"⚠️ Could not extract text from {file.filename}")
                    resume_data_list.append({
                        "text": "",
                        "filename": file.filename
                    })
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse {file.filename}: {str(e)}")
                resume_data_list.append({
                    "text": "",
                    "filename": file.filename
                })
        
        # Step 3: Score all resumes
        logger.info(f"🎯 Scoring {len(resume_data_list)} resumes...")
        batch_results = await scoring_engine.score_multiple_resumes(
            resume_data_list,
            job_analysis
        )
        
        result = {
            "status": "success",
            "job_title": job_title,
            "job_analysis": job_analysis,
            "batch_results": batch_results,
            "summary": {
                "total_files": len(files),
                "successfully_processed": batch_results["processed_successfully"],
                "failed_files": batch_results["failed_resumes"],
                "average_score": batch_results["average_score"],
                "top_score": max((r.get("overall_score", 0) for r in batch_results["results"]), default=0),
                "processing_time": batch_results["processing_time_seconds"]
            },
            "message": f"Batch processing completed. {batch_results['processed_successfully']}/{len(files)} resumes scored successfully."
        }
        
        logger.info(f"✅ Batch scoring completed: {batch_results['processed_successfully']}/{len(files)} successful")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in batch scoring: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch processing: {str(e)}"
        )

@router.get("/scoring-info")
async def get_scoring_information():
    """Get information about the scoring methodology"""
    
    return {
        "scoring_methodology": {
            "weights": {
                "required_skills_match": "40%",
                "experience_level": "30%",
                "education_requirements": "20%", 
                "additional_qualifications": "10%"
            },
            "score_ranges": {
                "90-100": "Exceptional match, immediate interview",
                "75-89": "Strong match, high priority",
                "60-74": "Good match, consider for interview",
                "45-59": "Moderate match, review carefully",
                "0-44": "Weak match, likely not suitable"
            }
        },
        "ai_provider": "google_gemini",
        "features": [
            "AI-powered skill extraction and matching",
            "Experience level evaluation", 
            "Education requirement matching",
            "Detailed justification for each score",
            "Batch processing capability",
            "Ranking and comparison reports"
        ]
    }

# Import other routers
from app.api.routes.upload import router as upload_router
from app.api.routes.analysis import router as analysis_router

# Include all routes
app.include_router(router, prefix="/api/v1/scoring", tags=["scoring"])
app.include_router(upload_router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Resume Screening AI"}

# Test configuration endpoint  
@app.get("/test-config")
async def test_config():
    return {
        "database_url": settings.database_url,
        "ai_provider": settings.ai_provider,
        "upload_dir": settings.upload_dir,
        "debug": settings.debug
    }

# Debug endpoint to see static directory structure
@app.get("/debug-static")
async def debug_static():
    def list_directory(path):
        result = {}
        if os.path.exists(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result[f"{item}/"] = list_directory(item_path)
                else:
                    result[item] = f"file ({os.path.getsize(item_path)} bytes)"
        return result
    
    return {
        "static_dir": "/app/static",
        "exists": os.path.exists("/app/static"),
        "contents": list_directory("/app/static") if os.path.exists("/app/static") else "Directory not found"
    }

# Mount static files (React frontend)
static_dir = "/app/static"
logger.info(f"Looking for static files in: {static_dir}")
logger.info(f"Static directory exists: {os.path.exists(static_dir)}")

if os.path.exists(static_dir):
    # List contents of static directory for debugging
    try:
        static_contents = os.listdir(static_dir)
        logger.info(f"Static directory contents: {static_contents}")
    except Exception as e:
        logger.error(f"Error listing static directory: {e}")
    
    # Don't mount /static separately - handle all routes through our handler
    
    # Serve React app for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        logger.info(f"Serving route: {full_path}")
        
        # Don't serve React app for API routes
        if full_path.startswith("api/") or full_path in ["health", "docs", "openapi.json", "redoc"]:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Handle static/ prefixed requests by removing the static/ prefix
        if full_path.startswith("static/"):
            full_path = full_path[7:]  # Remove 'static/' prefix
        
        # Try to serve static files first (CSS, JS, images, etc.)
        # First try the direct path
        static_file_path = os.path.join(static_dir, full_path)
        logger.info(f"Looking for static file: {static_file_path}")
        
        # If not found, try with extra 'static/' prefix (React build puts files in static/static/)
        if not os.path.exists(static_file_path):
            static_file_path = os.path.join(static_dir, "static", full_path)
            logger.info(f"Trying with static/ prefix: {static_file_path}")
        
        logger.info(f"File exists: {os.path.exists(static_file_path)}")
        
        if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
            # Determine the correct media type
            media_type, _ = mimetypes.guess_type(static_file_path)
            logger.info(f"Serving file: {static_file_path} with media type: {media_type}")
            return FileResponse(static_file_path, media_type=media_type)
        
        # If no static file found, serve index.html (React Router will handle routing)
        index_file = os.path.join(static_dir, "index.html")
        logger.info(f"Looking for index.html at: {index_file}")
        logger.info(f"Index file exists: {os.path.exists(index_file)}")
        
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
else:
    logger.error(f"Static directory not found: {static_dir}")
    
    @app.get("/")
    async def root():
        return {
            "message": "Resume Screening AI Backend", 
            "static_dir": static_dir,
            "static_exists": os.path.exists(static_dir),
            "current_dir": os.getcwd(),
            "dir_contents": os.listdir("/app") if os.path.exists("/app") else []
        }