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
    enhance_with_ai: Optional[bool] = True  # 🌟 NEW: Enable AI enhancement by default

class JobEnhancementRequest(BaseModel):
    """🌟 NEW: Dedicated endpoint for job description enhancement"""
    description: str
    title: Optional[str] = None

class ResumeTextRequest(BaseModel):
    resume_text: str
    job_context: Optional[Dict] = None

@router.post("/enhance-job-description")
async def enhance_job_description(
    request: JobEnhancementRequest
) -> Dict[str, Any]:
    """
    🌟 NEW: AI-powered job description enhancement
    
    This endpoint:
    1. Takes raw job description input from user
    2. Uses Google Gemini to clean, structure, and optimize it
    3. Returns enhanced description with extracted requirements
    4. Provides quality improvement metrics
    """
    
    logger.info(f"🔧 Enhancing job description: {request.title or 'Untitled Job'}")
    
    try:
        if not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty"
            )
        
        # Enhance with Google Gemini
        enhancement_result = await ai_analyzer.enhance_job_description(
            request.description, 
            request.title
        )
        
        result = {
            "status": "success",
            "enhancement": enhancement_result,
            "ai_provider": "google_gemini",
            "features": ["grammar_correction", "skill_standardization", "requirement_extraction", "structure_optimization"],
            "message": "Job description enhanced successfully with AI optimization"
        }
        
        # Add quality improvement metrics
        if "quality_score" in enhancement_result:
            result["improvement_metrics"] = {
                "original_quality": "estimated_from_input",
                "enhanced_quality": enhancement_result["quality_score"],
                "improvement_areas": enhancement_result.get("optimization_notes", ""),
                "was_enhanced": True
            }
        
        logger.info("✅ Job description enhancement completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error enhancing job description: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enhancing job description: {str(e)}"
        )

@router.post("/analyze-job")
async def analyze_job_description(
    request: JobDescriptionRequest
) -> Dict[str, Any]:
    """
    Enhanced job description analysis with optional AI optimization
    
    This endpoint:
    1. Optionally enhances the job description first (if enhance_with_ai=True)
    2. Uses Google Gemini to extract structured requirements
    3. Returns detailed analysis with skill categorization
    4. Includes enhancement details if optimization was used
    """
    
    logger.info(f"📊 Analyzing job description: {request.title or 'Untitled Job'}")
    
    try:
        if not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty"
            )
        
        # Analyze with optional enhancement
        analysis = await ai_analyzer.analyze_job_description(
            request.description,
            request.title,
            use_enhancement=request.enhance_with_ai
        )
        
        result = {
            "status": "success",
            "job_title": request.title,
            "company": request.company,
            "analysis": analysis,
            "ai_provider": "google_gemini",
            "features": ["enhanced_skill_categorization", "requirement_extraction", "experience_analysis"],
            "message": f"Job description analyzed successfully {'with AI enhancement' if request.enhance_with_ai else 'without enhancement'}"
        }
        
        # Add enhancement information if available
        if "enhancement_details" in analysis:
            result["enhancement_info"] = {
                "was_enhanced": analysis["enhancement_details"]["was_enhanced"],
                "optimization_applied": request.enhance_with_ai
            }
            
            if analysis["enhancement_details"]["was_enhanced"]:
                result["enhancement_info"]["improvements"] = analysis["enhancement_details"].get("optimization_notes")
                result["enhancement_info"]["quality_boost"] = analysis["enhancement_details"].get("quality_improvement")
        
        logger.info("✅ Enhanced job analysis completed successfully")
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
    3. Returns structured candidate profile with enhanced categorization
    """
    
    logger.info("📋 Analyzing resume text with Google Gemini")
    
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
            "features": ["skill_categorization", "experience_analysis", "career_insights", "resume_quality_scoring"],
            "message": "Resume analyzed successfully with enhanced Google Gemini"
        }
        
        logger.info("✅ Enhanced resume analysis completed successfully")
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
    
    logger.info("🔍 Checking enhanced Google Gemini AI status")
    
    # Test Google Gemini connection
    connection_test = await ai_analyzer.test_connection()
    
    return {
        "current_provider": "google_gemini",
        "google_api_configured": bool(settings.google_api_key),
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
        "model": "gemini-1.5-flash",
        "connection_test": connection_test,
        "status": "ready" if connection_test.get("status") == "connected" else "not_ready",
        "new_features": [
            "job_description_enhancement",
            "ai_prompt_optimization", 
            "improved_skill_categorization",
            "career_trajectory_analysis",
            "resume_quality_scoring"
        ]
    }

@router.post("/compare-job-descriptions")
async def compare_job_descriptions(
    request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🌟 NEW: Compare multiple job descriptions
    
    This endpoint:
    1. Takes multiple job descriptions
    2. Enhances each one
    3. Provides comparison analysis
    4. Shows similarities and differences
    """
    
    logger.info("🔄 Comparing multiple job descriptions")
    
    try:
        job_descriptions = request.get("job_descriptions", [])
        
        if len(job_descriptions) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 job descriptions required for comparison"
            )
        
        if len(job_descriptions) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 job descriptions allowed for comparison"
            )
        
        # Enhance and analyze each job description
        analyzed_jobs = []
        for i, job_desc in enumerate(job_descriptions):
            title = job_desc.get("title", f"Job {i+1}")
            description = job_desc.get("description", "")
            
            if not description.strip():
                continue
                
            analysis = await ai_analyzer.analyze_job_description(
                description, 
                title, 
                use_enhancement=True
            )
            
            analyzed_jobs.append({
                "title": title,
                "analysis": analysis,
                "index": i + 1
            })
        
        # Generate comparison insights
        comparison_result = {
            "status": "success",
            "total_jobs_analyzed": len(analyzed_jobs),
            "jobs": analyzed_jobs,
            "comparison_insights": {
                "common_skills": _find_common_skills(analyzed_jobs),
                "experience_range": _analyze_experience_requirements(analyzed_jobs),
                "education_patterns": _analyze_education_requirements(analyzed_jobs),
                "seniority_distribution": _analyze_seniority_levels(analyzed_jobs)
            },
            "ai_provider": "google_gemini",
            "message": f"Successfully compared {len(analyzed_jobs)} job descriptions"
        }
        
        logger.info(f"✅ Job comparison completed for {len(analyzed_jobs)} positions")
        return comparison_result
        
    except Exception as e:
        logger.error(f"❌ Error comparing job descriptions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing job descriptions: {str(e)}"
        )

# Helper functions for job comparison
def _find_common_skills(analyzed_jobs: list) -> Dict[str, Any]:
    """Find skills that appear across multiple job descriptions"""
    
    all_skills = {}
    total_jobs = len(analyzed_jobs)
    
    for job in analyzed_jobs:
        job_skills = job["analysis"].get("required_skills", {})
        for category, skills in job_skills.items():
            if not isinstance(skills, list):
                continue
                
            for skill in skills:
                skill_key = f"{category}:{skill}"
                if skill_key not in all_skills:
                    all_skills[skill_key] = 0
                all_skills[skill_key] += 1
    
    # Find skills that appear in 50%+ of jobs
    common_threshold = max(1, total_jobs // 2)
    common_skills = {
        skill.split(":", 1)[1]: count 
        for skill, count in all_skills.items() 
        if count >= common_threshold
    }
    
    return {
        "skills": common_skills,
        "threshold": f"Appears in {common_threshold}+ out of {total_jobs} jobs"
    }

def _analyze_experience_requirements(analyzed_jobs: list) -> Dict[str, Any]:
    """Analyze experience requirements across jobs"""
    
    experience_levels = []
    for job in analyzed_jobs:
        min_exp = job["analysis"].get("minimum_experience")
        if min_exp is not None:
            experience_levels.append(min_exp)
    
    if not experience_levels:
        return {"message": "No experience requirements specified"}
    
    return {
        "min_experience": min(experience_levels),
        "max_experience": max(experience_levels),
        "average_experience": sum(experience_levels) / len(experience_levels),
        "jobs_with_requirements": len(experience_levels),
        "total_jobs": len(analyzed_jobs)
    }

def _analyze_education_requirements(analyzed_jobs: list) -> Dict[str, Any]:
    """Analyze education requirements across jobs"""
    
    degree_requirements = []
    for job in analyzed_jobs:
        edu_req = job["analysis"].get("education_requirements", {})
        required_degree = edu_req.get("required_degree")
        if required_degree:
            degree_requirements.append(required_degree)
    
    degree_counts = {}
    for degree in degree_requirements:
        degree_counts[degree] = degree_counts.get(degree, 0) + 1
    
    return {
        "degree_distribution": degree_counts,
        "most_common": max(degree_counts.keys(), key=degree_counts.get) if degree_counts else None,
        "jobs_with_requirements": len(degree_requirements),
        "total_jobs": len(analyzed_jobs)
    }

def _analyze_seniority_levels(analyzed_jobs: list) -> Dict[str, Any]:
    """Analyze seniority levels across jobs"""
    
    seniority_levels = []
    for job in analyzed_jobs:
        level = job["analysis"].get("seniority_level")
        if level:
            seniority_levels.append(level)
    
    level_counts = {}
    for level in seniority_levels:
        level_counts[level] = level_counts.get(level, 0) + 1
    
    return {
        "level_distribution": level_counts,
        "most_common": max(level_counts.keys(), key=level_counts.get) if level_counts else None,
        "jobs_with_levels": len(seniority_levels),
        "total_jobs": len(analyzed_jobs)
    }