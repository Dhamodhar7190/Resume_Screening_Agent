from app.services.ai_analyzer import AIAnalyzer
from app.core.config import settings
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Resume scoring and ranking engine using Google Gemini AI
    
    Scoring Categories (from project requirements):
    1. Required Skills Match (40% weight)
    2. Experience Level (30% weight)  
    3. Education Requirements (20% weight)
    4. Additional Qualifications (10% weight)
    """
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        
        # Scoring weights from project specification
        self.weights = {
            "required_skills": 0.40,      # 40%
            "experience": 0.30,           # 30%
            "education": 0.20,            # 20%
            "additional_qualifications": 0.10  # 10%
        }
        
        # Score interpretation thresholds
        self.score_thresholds = {
            90: "Exceptional match, immediate interview",
            75: "Strong match, high priority", 
            60: "Good match, consider for interview",
            45: "Moderate match, review carefully",
            0: "Weak match, likely not suitable"
        }
        
        logger.info("✅ ScoringEngine initialized with Google Gemini")
    
    async def score_resume_against_job(
        self, 
        resume_text: str, 
        job_analysis: Dict[str, Any], 
        filename: str = "resume.pdf"
    ) -> Dict[str, Any]:
        """
        Score a resume against job requirements using AI analysis
        
        Args:
            resume_text: Extracted resume text
            job_analysis: Structured job requirements from analyze_job_description  
            filename: Resume filename for reference
            
        Returns:
            Complete scoring results with breakdown and recommendations
        """
        
        start_time = datetime.now()
        logger.info(f"🔍 Scoring resume: {filename}")
        
        try:
            # Step 1: Analyze resume content with job context
            resume_analysis = await self.ai_analyzer.analyze_resume_content(
                resume_text, 
                job_analysis
            )
            
            # Step 2: Generate detailed scoring using AI
            detailed_scoring = await self._generate_ai_scoring(
                resume_analysis, 
                job_analysis
            )
            
            # Step 3: Calculate final scores
            final_scores = self._calculate_weighted_scores(detailed_scoring)
            
            # Step 4: Generate recommendations
            recommendation = self._get_recommendation(final_scores["overall_score"])
            
            # Step 5: Compile complete results
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "filename": filename,
                "overall_score": round(final_scores["overall_score"], 1),
                "recommendation": recommendation,
                "score_breakdown": {
                    "required_skills": round(detailed_scoring["required_skills_score"], 1),
                    "experience_level": round(detailed_scoring["experience_score"], 1), 
                    "education": round(detailed_scoring["education_score"], 1),
                    "additional_qualifications": round(detailed_scoring["additional_qualifications_score"], 1)
                },
                "skill_matches": detailed_scoring.get("skill_matches", []),
                "key_strengths": detailed_scoring.get("key_strengths", []),
                "areas_of_concern": detailed_scoring.get("areas_of_concern", []),
                "justification": detailed_scoring.get("justification", ""),
                "candidate_info": {
                    "name": resume_analysis.get("candidate_name"),
                    "email": resume_analysis.get("email"),
                    "phone": resume_analysis.get("phone"),
                    "years_experience": resume_analysis.get("years_experience"),
                    "education_level": resume_analysis.get("education_level")
                },
                "processing_time_seconds": round(processing_time, 2),
                "ai_provider": "google_gemini",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Resume scored: {filename} - Score: {result['overall_score']}/100")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error scoring resume {filename}: {str(e)}")
            raise Exception(f"Failed to score resume: {str(e)}")
    
    async def score_multiple_resumes(
        self,
        resume_data_list: List[Dict[str, Any]], 
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score multiple resumes and return ranked results
        
        Args:
            resume_data_list: List of {text, filename} dicts
            job_analysis: Job requirements analysis
            
        Returns:
            Batch processing results with rankings
        """
        
        start_time = datetime.now()
        logger.info(f"🔍 Batch scoring {len(resume_data_list)} resumes")
        
        results = []
        successful_count = 0
        
        for resume_data in resume_data_list:
            try:
                score_result = await self.score_resume_against_job(
                    resume_data["text"],
                    job_analysis,
                    resume_data["filename"]
                )
                results.append(score_result)
                successful_count += 1
                
            except Exception as e:
                # Continue processing other resumes even if one fails
                logger.warning(f"⚠️ Failed to score {resume_data['filename']}: {str(e)}")
                results.append({
                    "filename": resume_data["filename"],
                    "error": str(e),
                    "overall_score": 0,
                    "recommendation": "Processing failed"
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        
        # Get top candidates
        top_candidates = [r for r in results[:5] if r.get("overall_score", 0) > 0]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        batch_result = {
            "total_resumes": len(resume_data_list),
            "processed_successfully": successful_count,
            "failed_resumes": len(resume_data_list) - successful_count,
            "results": results,
            "top_candidates": top_candidates,
            "processing_time_seconds": round(processing_time, 2),
            "average_score": round(sum(r.get("overall_score", 0) for r in results) / len(results), 1) if results else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Batch scoring completed: {successful_count}/{len(resume_data_list)} successful")
        return batch_result
    
    async def _generate_ai_scoring(
        self, 
        resume_analysis: Dict[str, Any], 
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to generate detailed scoring analysis"""
        
        scoring_prompt = f"""
Analyze this candidate against job requirements and provide detailed scoring. Return ONLY valid JSON:

JOB REQUIREMENTS:
- Required Skills: {job_analysis.get('required_skills', [])}
- Preferred Skills: {job_analysis.get('preferred_skills', [])}
- Minimum Experience: {job_analysis.get('minimum_experience', 'Not specified')} years
- Education Requirements: {job_analysis.get('education_requirements', [])}
- Seniority Level: {job_analysis.get('seniority_level', 'Not specified')}

CANDIDATE PROFILE:
- Technical Skills: {resume_analysis.get('technical_skills', [])}
- Years Experience: {resume_analysis.get('years_experience', 'Not specified')}
- Education Level: {resume_analysis.get('education_level', 'Not specified')}
- Work Experience: {resume_analysis.get('work_experience', [])}
- Certifications: {resume_analysis.get('certifications', [])}

Return this exact JSON structure with scores out of 100:
{{
    "required_skills_score": number_0_to_100,
    "experience_score": number_0_to_100,
    "education_score": number_0_to_100,
    "additional_qualifications_score": number_0_to_100,
    "skill_matches": [
        {{
            "skill": "skill name",
            "required": true_or_false,
            "found": true_or_false,
            "confidence": number_0_to_1
        }}
    ],
    "key_strengths": ["list of candidate strengths"],
    "areas_of_concern": ["list of potential concerns"],
    "justification": "detailed explanation of scoring rationale with specific examples"
}}

Scoring Guidelines:
- Required Skills (40%): Score based on how many required skills are matched
- Experience (30%): Compare years of experience to minimum requirement
- Education (20%): Match education level to requirements  
- Additional Qualifications (10%): Certifications, preferred skills, projects
- Be specific and reference actual skills/experience found
"""
        
        try:
            response = await self.ai_analyzer._call_gemini(scoring_prompt)
            
            # Parse the AI scoring response
            import json
            scoring_result = json.loads(response)
            return scoring_result
            
        except json.JSONDecodeError:
            # Try to extract JSON if AI response has extra text
            return self.ai_analyzer._extract_json_from_response(response)
        except Exception as e:
            logger.error(f"❌ AI scoring generation failed: {str(e)}")
            # Return fallback scoring
            return self._generate_fallback_scoring(resume_analysis, job_analysis)
    
    def _calculate_weighted_scores(self, detailed_scoring: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final weighted scores"""
        
        # Get individual scores
        required_skills = detailed_scoring.get("required_skills_score", 0)
        experience = detailed_scoring.get("experience_score", 0)
        education = detailed_scoring.get("education_score", 0)
        additional = detailed_scoring.get("additional_qualifications_score", 0)
        
        # Calculate weighted overall score
        overall_score = (
            required_skills * self.weights["required_skills"] +
            experience * self.weights["experience"] +
            education * self.weights["education"] + 
            additional * self.weights["additional_qualifications"]
        )
        
        return {
            "overall_score": min(100, max(0, overall_score)),  # Clamp between 0-100
            "required_skills": required_skills,
            "experience": experience,
            "education": education,
            "additional_qualifications": additional
        }
    
    def _get_recommendation(self, overall_score: float) -> str:
        """Get hiring recommendation based on score"""
        
        for threshold, recommendation in self.score_thresholds.items():
            if overall_score >= threshold:
                return recommendation
        
        return "Weak match, likely not suitable"
    
    def _generate_fallback_scoring(
        self, 
        resume_analysis: Dict[str, Any], 
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic scoring if AI fails"""
        
        logger.warning("⚠️ Using fallback scoring method")
        
        # Simple keyword matching fallback
        required_skills = job_analysis.get("required_skills", [])
        candidate_skills = resume_analysis.get("technical_skills", [])
        
        # Basic skills matching
        skills_matched = 0
        for req_skill in required_skills:
            for cand_skill in candidate_skills:
                if req_skill.lower() in cand_skill.lower():
                    skills_matched += 1
                    break
        
        skills_score = (skills_matched / max(1, len(required_skills))) * 100
        
        return {
            "required_skills_score": min(100, skills_score),
            "experience_score": 70,  # Default neutral score
            "education_score": 70,   # Default neutral score
            "additional_qualifications_score": 50,
            "skill_matches": [],
            "key_strengths": ["Analysis using fallback method"],
            "areas_of_concern": ["Could not perform detailed AI analysis"],
            "justification": "Basic keyword matching used due to AI analysis failure"
        }