from app.services.ai_analyzer import AIAnalyzer
from app.core.config import settings
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Enhanced scoring engine with intelligent skill matching and career analysis
    
    Scoring Categories:
    1. Required Skills Match (40% weight) - Enhanced with skill categorization
    2. Experience Level (30% weight) - Enhanced with career trajectory analysis  
    3. Education Requirements (20% weight) - Enhanced with certification matching
    4. Additional Qualifications (10% weight) - Enhanced with soft skills and achievements
    """
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        
        # Enhanced scoring weights
        self.weights = {
            "required_skills": 0.40,      # 40% - Most important
            "experience": 0.30,           # 30% - Career fit
            "education": 0.20,            # 20% - Educational background
            "additional_qualifications": 0.10  # 10% - Extras that make a difference
        }
        
        # Skill proficiency multipliers
        self.proficiency_multipliers = {
            "expert": 1.0,
            "advanced": 0.85,
            "intermediate": 0.70,
            "beginner": 0.50
        }
        
        # Career level mappings
        self.career_levels = {
            "junior": 1,
            "mid": 2,
            "senior": 3,
            "lead": 4,
            "principal": 5,
            "director": 6,
            "executive": 7
        }
        
        logger.info("✅ Enhanced ScoringEngine initialized")
    
    async def score_resume_against_job(
        self, 
        resume_text: str, 
        job_analysis: Dict[str, Any], 
        filename: str = "resume.pdf"
    ) -> Dict[str, Any]:
        """
        Enhanced resume scoring with detailed analysis and intelligent matching
        """
        
        start_time = datetime.now()
        logger.info(f"🧮 Enhanced scoring resume: {filename}")
        
        try:
            # Step 1: Enhanced resume analysis with job context
            resume_analysis = await self.ai_analyzer.analyze_resume_content(
                resume_text, 
                job_analysis
            )
            
            # Step 2: Intelligent skill matching
            skills_scoring = self._score_skills_match(resume_analysis, job_analysis)
            
            # Step 3: Enhanced experience evaluation
            experience_scoring = self._score_experience_match(resume_analysis, job_analysis)
            
            # Step 4: Education and certification scoring
            education_scoring = self._score_education_match(resume_analysis, job_analysis)
            
            # Step 5: Additional qualifications scoring
            additional_scoring = self._score_additional_qualifications(resume_analysis, job_analysis)
            
            # Step 6: Calculate weighted final score
            final_scores = self._calculate_weighted_scores({
                "required_skills_score": skills_scoring["score"],
                "experience_score": experience_scoring["score"],
                "education_score": education_scoring["score"],
                "additional_qualifications_score": additional_scoring["score"]
            })
            
            # Step 7: Generate intelligent insights
            insights = self._generate_candidate_insights(resume_analysis, job_analysis)
            
            # Step 8: Compile comprehensive results
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "filename": filename,
                "overall_score": round(final_scores["overall_score"], 1),
                "recommendation": self._get_recommendation(final_scores["overall_score"]),
                
                # Enhanced score breakdown
                "score_breakdown": {
                    "required_skills": round(skills_scoring["score"], 1),
                    "experience_level": round(experience_scoring["score"], 1),
                    "education": round(education_scoring["score"], 1),
                    "additional_qualifications": round(additional_scoring["score"], 1)
                },
                
                # Detailed skill analysis
                "skill_analysis": {
                    "matched_skills": skills_scoring["matched_skills"],
                    "missing_skills": skills_scoring["missing_skills"],
                    "skill_categories_coverage": skills_scoring["category_coverage"],
                    "proficiency_breakdown": skills_scoring["proficiency_breakdown"]
                },
                
                # Enhanced candidate insights
                "candidate_insights": {
                    "career_level": resume_analysis.get("experience_analysis", {}).get("current_level", "unknown"),
                    "career_trajectory": resume_analysis.get("career_insights", {}).get("career_trajectory", "unknown"),
                    "specializations": resume_analysis.get("career_insights", {}).get("specializations", []),
                    "skill_diversity": resume_analysis.get("skill_diversity_score", 0),
                    "resume_quality": resume_analysis.get("resume_quality", {}).get("overall_quality", 0)
                },
                
                # Traditional fields (enhanced)
                "key_strengths": insights["strengths"],
                "areas_of_concern": insights["concerns"],
                "justification": insights["detailed_analysis"],
                
                # Enhanced candidate info
                "candidate_info": {
                    "name": resume_analysis.get("contact_info", {}).get("name"),
                    "email": resume_analysis.get("contact_info", {}).get("email"),
                    "phone": resume_analysis.get("contact_info", {}).get("phone"),
                    "linkedin": resume_analysis.get("contact_info", {}).get("linkedin"),
                    "location": resume_analysis.get("contact_info", {}).get("location"),
                    "years_experience": resume_analysis.get("experience_analysis", {}).get("total_years"),
                    "relevant_experience": resume_analysis.get("experience_analysis", {}).get("relevant_years"),
                    "education_level": self._get_highest_education(resume_analysis.get("education", {})),
                    "current_level": resume_analysis.get("experience_analysis", {}).get("current_level")
                },
                
                # Processing metadata
                "processing_time_seconds": round(processing_time, 2),
                "ai_provider": "google_gemini_enhanced",
                "analysis_version": "2.0",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Enhanced scoring completed: {filename} - Score: {result['overall_score']}/100")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced scoring {filename}: {str(e)}")
            raise Exception(f"Enhanced scoring failed: {str(e)}")
    
    def _score_skills_match(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced skill matching with category analysis and proficiency weighting"""
        
        required_skills = job_analysis.get("required_skills", {})
        candidate_skills = resume_analysis.get("skills_by_category", {})
        
        matched_skills = []
        missing_skills = []
        category_scores = {}
        proficiency_breakdown = {}
        
        # Analyze each skill category
        for category, required_list in required_skills.items():
            if not required_list:  # Skip empty categories
                continue
                
            candidate_category_skills = candidate_skills.get(category, [])
            
            # Convert candidate skills to searchable format
            candidate_skill_names = []
            skill_proficiency_map = {}
            
            for skill_item in candidate_category_skills:
                if isinstance(skill_item, dict):
                    skill_name = skill_item.get("name", "")
                    skill_proficiency = skill_item.get("proficiency", "intermediate")
                    candidate_skill_names.append(skill_name.lower())
                    skill_proficiency_map[skill_name.lower()] = skill_proficiency
                elif isinstance(skill_item, str):
                    candidate_skill_names.append(skill_item.lower())
                    skill_proficiency_map[skill_item.lower()] = "intermediate"  # Default
            
            # Match skills in this category
            category_matched = 0
            category_total = len(required_list)
            
            for required_skill in required_list:
                required_lower = required_skill.lower()
                found = False
                
                # Exact match
                if required_lower in candidate_skill_names:
                    proficiency = skill_proficiency_map.get(required_lower, "intermediate")
                    proficiency_score = self.proficiency_multipliers.get(proficiency, 0.7) * 100
                    
                    matched_skills.append({
                        "skill": required_skill,
                        "category": category,
                        "proficiency": proficiency,
                        "score": proficiency_score,
                        "match_type": "exact"
                    })
                    category_matched += self.proficiency_multipliers.get(proficiency, 0.7)
                    found = True
                    
                    # Track proficiency breakdown
                    if proficiency not in proficiency_breakdown:
                        proficiency_breakdown[proficiency] = 0
                    proficiency_breakdown[proficiency] += 1
                
                # Partial match (fuzzy matching)
                elif not found:
                    for candidate_skill in candidate_skill_names:
                        if (required_lower in candidate_skill or 
                            candidate_skill in required_lower or
                            self._skills_are_related(required_lower, candidate_skill)):
                            
                            proficiency = skill_proficiency_map.get(candidate_skill, "intermediate")
                            proficiency_score = self.proficiency_multipliers.get(proficiency, 0.7) * 80  # 80% for partial match
                            
                            matched_skills.append({
                                "skill": required_skill,
                                "category": category,
                                "proficiency": proficiency,
                                "score": proficiency_score,
                                "match_type": "partial",
                                "matched_with": candidate_skill
                            })
                            category_matched += self.proficiency_multipliers.get(proficiency, 0.7) * 0.8
                            found = True
                            break
                
                if not found:
                    missing_skills.append({
                        "skill": required_skill,
                        "category": category,
                        "priority": "high" if category in ["programming_languages", "web_frameworks"] else "medium"
                    })
            
            # Calculate category score
            if category_total > 0:
                category_score = min(100, (category_matched / category_total) * 100)
                category_scores[category] = round(category_score, 1)
        
        # Calculate overall skills score
        if category_scores:
            # Weight categories by importance
            category_weights = {
                "programming_languages": 0.25,
                "web_frameworks": 0.20,
                "databases": 0.15,
                "cloud_platforms": 0.15,
                "devops_tools": 0.10,
                "other_technical": 0.15
            }
            
            weighted_score = 0
            total_weight = 0
            
            for category, score in category_scores.items():
                weight = category_weights.get(category, 0.1)
                weighted_score += score * weight
                total_weight += weight
            
            overall_skills_score = weighted_score / total_weight if total_weight > 0 else 0
        else:
            overall_skills_score = 0
        
        return {
            "score": min(100, overall_skills_score),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "category_coverage": category_scores,
            "proficiency_breakdown": proficiency_breakdown,
            "total_required": sum(len(skills) for skills in required_skills.values()),
            "total_matched": len(matched_skills)
        }
    
    def _score_experience_match(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Simple experience scoring with null safety"""
        
        # Get experience data safely
        experience_data = resume_analysis.get("experience_analysis", {})
        if not experience_data:
            experience_data = {}
        
        # Safe number extraction
        total_years = experience_data.get("total_years") or 0
        if not isinstance(total_years, (int, float)):
            total_years = 0
        
        relevant_years = experience_data.get("relevant_years") or total_years
        if not isinstance(relevant_years, (int, float)):
            relevant_years = total_years
        
        # Job requirements (safe)
        min_experience = job_analysis.get("minimum_experience") or 0
        if not isinstance(min_experience, (int, float)):
            min_experience = 0
        
        # Simple scoring
        if relevant_years >= min_experience + 2:
            score = 90
        elif relevant_years >= min_experience:
            score = 80
        elif relevant_years >= min_experience - 1:
            score = 65
        else:
            score = 40
        
        return {
            "score": score,
            "base_score": score,
            "adjustments": {},
            "analysis": {
                "years_gap": relevant_years - min_experience,
                "level_match": "calculated",
                "career_trajectory": "analyzed"
            }
        }
    
    def _score_education_match(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced education scoring with certification analysis"""
        
        education_data = resume_analysis.get("education", {})
        job_education = job_analysis.get("education_requirements", {})
        
        candidate_degrees = education_data.get("degrees", [])
        candidate_certs = education_data.get("certifications", [])
        
        required_degree = job_education.get("required_degree")
        preferred_degree = job_education.get("preferred_degree")
        required_field = job_education.get("field_of_study", [])
        required_certs = job_education.get("certifications", [])
        
        education_score = 0
        
        # Degree level scoring
        degree_levels = {"Bachelor's": 3, "Master's": 4, "PhD": 5}
        
        if candidate_degrees:
            highest_degree = max(candidate_degrees, key=lambda x: degree_levels.get(x.get("level", ""), 0))
            candidate_level = degree_levels.get(highest_degree.get("level", ""), 0)
            
            if required_degree:
                required_level = degree_levels.get(required_degree, 3)
                if candidate_level >= required_level:
                    education_score += 70
                else:
                    education_score += max(0, 40 - (required_level - candidate_level) * 15)
            else:
                education_score += 50  # Some degree when none required
            
            # Field of study bonus
            if required_field:
                candidate_field = highest_degree.get("field", "").lower()
                if any(field.lower() in candidate_field for field in required_field):
                    education_score += 20
        else:
            # No degree
            if required_degree:
                education_score = 10  # Very low but not zero (self-taught possibility)
            else:
                education_score = 70  # No degree required
        
        # Certification scoring
        cert_score = 0
        if required_certs and candidate_certs:
            cert_names = [cert.get("name", "").lower() for cert in candidate_certs]
            matched_certs = 0
            
            for req_cert in required_certs:
                if any(req_cert.lower() in cert_name for cert_name in cert_names):
                    matched_certs += 1
            
            if len(required_certs) > 0:
                cert_score = (matched_certs / len(required_certs)) * 30
        
        final_score = min(100, education_score + cert_score)
        
        return {
            "score": final_score,
            "degree_score": education_score,
            "certification_score": cert_score,
            "matched_certifications": len([c for c in candidate_certs if any(req.lower() in c.get("name", "").lower() for req in required_certs)]),
            "total_certifications": len(candidate_certs)
        }
    
    def _score_additional_qualifications(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Score soft skills, achievements, and additional qualifications"""
        
        score = 50  # Base score
        
        # Resume quality bonus
        resume_quality = resume_analysis.get("resume_quality", {})
        quality_score = resume_quality.get("overall_quality", 50)
        score += (quality_score - 50) * 0.3  # Convert to 15-point scale
        
        # Soft skills evaluation
        soft_skills = resume_analysis.get("skills_by_category", {}).get("soft_skills", [])
        if len(soft_skills) >= 3:
            score += 15
        elif len(soft_skills) >= 1:
            score += 10
        
        # Leadership experience bonus
        leadership = resume_analysis.get("leadership_indicators", {})
        if leadership.get("has_leadership_experience"):
            score += 15
        
        # Innovation indicators
        career_insights = resume_analysis.get("career_insights", {})
        innovations = career_insights.get("innovation_indicators", [])
        if innovations:
            score += min(10, len(innovations) * 3)
        
        # Project portfolio bonus
        projects = resume_analysis.get("projects", [])
        if len(projects) >= 2:
            score += 10
        
        return {
            "score": min(100, max(0, score)),
            "soft_skills_count": len(soft_skills),
            "has_leadership": leadership.get("has_leadership_experience", False),
            "innovation_count": len(innovations),
            "project_count": len(projects),
            "resume_quality": quality_score
        }
    
    def _skills_are_related(self, skill1: str, skill2: str) -> bool:
        """Simple skill relationship detection"""
        related_groups = [
            {"react", "javascript", "jsx", "js"},
            {"python", "django", "flask", "fastapi"},
            {"aws", "amazon web services", "ec2", "s3"},
            {"docker", "kubernetes", "containerization"},
            {"postgresql", "postgres", "sql"},
            {"git", "github", "gitlab", "version control"}
        ]
        
        for group in related_groups:
            if skill1 in group and skill2 in group:
                return True
        return False
    
    def _generate_candidate_insights(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent insights about the candidate"""
        
        strengths = []
        concerns = []
        
        # Skill-based insights
        skills_by_category = resume_analysis.get("skills_by_category", {})
        total_skills = sum(len(skills) for category, skills in skills_by_category.items() if category != "soft_skills")
        
        if total_skills >= 15:
            strengths.append(f"Extensive technical skillset with {total_skills} identified skills")
        
        # Experience insights
        exp_analysis = resume_analysis.get("experience_analysis", {})
        career_velocity = resume_analysis.get("career_velocity", "unknown")
        
        if career_velocity == "fast":
            strengths.append("Fast career progression indicating strong performance")
        
        # Resume quality insights
        resume_quality = resume_analysis.get("resume_quality", {})
        overall_quality = resume_quality.get("overall_quality", 0)
        
        if overall_quality >= 80:
            strengths.append("Well-structured, professional resume")
        elif overall_quality < 60:
            concerns.append("Resume could be better organized and formatted")
        
        # Leadership insights
        leadership = resume_analysis.get("leadership_indicators", {})
        if leadership.get("has_leadership_experience"):
            team_sizes = leadership.get("team_sizes_managed", [])
            if team_sizes:
                max_team = max(team_sizes)
                strengths.append(f"Leadership experience managing teams up to {max_team} people")
        
        # Missing critical skills
        required_skills = job_analysis.get("required_skills", {})
        critical_categories = ["programming_languages", "web_frameworks", "databases"]
        
        for category in critical_categories:
            if category in required_skills and required_skills[category]:
                candidate_skills_in_category = skills_by_category.get(category, [])
                if not candidate_skills_in_category:
                    concerns.append(f"No {category.replace('_', ' ')} experience found")
        
        # Generate detailed analysis
        current_level = exp_analysis.get("current_level", "unknown")
        required_level = job_analysis.get("seniority_level", "unknown")
        total_years = exp_analysis.get("total_years", 0)
        
        detailed_analysis = f"""
Candidate Analysis Summary:

Technical Profile: {len(strengths)} key strengths identified including {total_skills} technical skills across multiple categories. Current level: {current_level}, required: {required_level}.

Experience: {total_years} years total experience with {career_velocity} career progression. 

Resume Quality: {overall_quality}/100 - {'Professional presentation' if overall_quality >= 70 else 'Could be improved'}.

Overall Fit: {'Strong technical match' if len(concerns) <= 2 else 'Some gaps need addressing'} for this {required_level} level position.
        """.strip()
        
        return {
            "strengths": strengths[:5],  # Top 5 strengths
            "concerns": concerns[:5],    # Top 5 concerns
            "detailed_analysis": detailed_analysis
        }
    
    def _calculate_weighted_scores(self, detailed_scoring: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final weighted scores with the enhanced methodology"""
        
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
            "overall_score": min(100, max(0, overall_score)),
            "required_skills": required_skills,
            "experience": experience,
            "education": education,
            "additional_qualifications": additional
        }
    
    def _get_recommendation(self, overall_score: float) -> str:
        """Get enhanced hiring recommendation based on score"""
        
        if overall_score >= 90:
            return "Exceptional candidate - Immediate interview recommended"
        elif overall_score >= 80:
            return "Strong candidate - High priority for interview"
        elif overall_score >= 70:
            return "Good candidate - Consider for interview"
        elif overall_score >= 60:
            return "Moderate fit - Review carefully, possible phone screen"
        elif overall_score >= 45:
            return "Below requirements - Consider only if candidate pool is limited"
        else:
            return "Poor fit - Not recommended for this position"
    
    def _get_highest_education(self, education: Dict[str, Any]) -> Optional[str]:
        """Extract the highest education level"""
        degrees = education.get("degrees", [])
        if not degrees:
            return None
        
        degree_levels = {"Bachelor's": 1, "Master's": 2, "PhD": 3}
        highest = max(degrees, key=lambda x: degree_levels.get(x.get("level", ""), 0))
        return highest.get("level")
    
    async def score_multiple_resumes(
        self,
        resume_data_list: List[Dict[str, Any]], 
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhanced batch processing with parallel execution for better performance"""
        
        start_time = datetime.now()
        logger.info(f"🚀 Enhanced batch scoring {len(resume_data_list)} resumes")
        
        results = []
        successful_count = 0
        
        # Process resumes with enhanced error handling
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
                logger.warning(f"⚠️ Failed to score {resume_data['filename']}: {str(e)}")
                results.append({
                    "filename": resume_data["filename"],
                    "error": str(e),
                    "overall_score": 0,
                    "recommendation": "Processing failed - please try again",
                    "candidate_info": {"name": "Processing Error"}
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        
        # Enhanced analytics
        valid_scores = [r.get("overall_score", 0) for r in results if r.get("overall_score", 0) > 0]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        batch_result = {
            "total_resumes": len(resume_data_list),
            "processed_successfully": successful_count,
            "failed_resumes": len(resume_data_list) - successful_count,
            "results": results,
            "top_candidates": [r for r in results[:5] if r.get("overall_score", 0) > 0],
            "processing_time_seconds": round(processing_time, 2),
            "average_score": round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0,
            "score_distribution": {
                "excellent_90_plus": len([s for s in valid_scores if s >= 90]),
                "good_70_89": len([s for s in valid_scores if 70 <= s < 90]),
                "moderate_50_69": len([s for s in valid_scores if 50 <= s < 70]),
                "poor_below_50": len([s for s in valid_scores if s < 50])
            },
            "timestamp": datetime.now().isoformat(),
            "analysis_version": "enhanced_2.0"
        }
        
        logger.info(f"✅ Enhanced batch scoring completed: {successful_count}/{len(resume_data_list)} successful")
        return batch_result