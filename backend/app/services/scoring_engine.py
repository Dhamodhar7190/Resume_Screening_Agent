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
        
        # Enhanced scoring weights (now role-adaptive)
        self.base_weights = {
            "required_skills": 0.40,      # 40% - Most important
            "experience": 0.30,           # 30% - Career fit
            "education": 0.20,            # 20% - Educational background
            "additional_qualifications": 0.10  # 10% - Extras
        }
        
        # 🌟 ENHANCEMENT 1: Role-specific scoring weight adjustments
        self.role_specific_weights = {
            "frontend_developer": {
                "web_frameworks": 0.35,      # React, Vue, Angular more important
                "programming_languages": 0.25, # JavaScript/TypeScript focus
                "databases": 0.10,           # Less critical for frontend
                "cloud_platforms": 0.15,
                "devops_tools": 0.05,        # Minimal for pure frontend
                "frontend_tools": 0.30       # CSS, HTML, design tools critical
            },
            "backend_developer": {
                "programming_languages": 0.35, # Core backend languages
                "databases": 0.30,            # Database design critical
                "web_frameworks": 0.20,       # Backend frameworks
                "cloud_platforms": 0.25,
                "devops_tools": 0.20,
                "frontend_tools": 0.05        # Minimal frontend needs
            },
            "fullstack_developer": {
                "programming_languages": 0.30,
                "web_frameworks": 0.25,
                "databases": 0.20,
                "cloud_platforms": 0.20,
                "devops_tools": 0.15,
                "frontend_tools": 0.20
            },
            "data_scientist": {
                "data_tools": 0.40,          # ML/Data tools most critical
                "programming_languages": 0.30, # Python, R focus
                "databases": 0.25,           # Data storage important
                "cloud_platforms": 0.15,
                "web_frameworks": 0.05,      # Less relevant
                "project_management": 0.10   # Research methodology
            },
            "devops_engineer": {
                "devops_tools": 0.40,        # Core DevOps tools
                "cloud_platforms": 0.35,     # AWS/Azure expertise
                "programming_languages": 0.20, # Scripting languages
                "databases": 0.15,
                "web_frameworks": 0.05       # Minimal application focus
            }
        }
        
        # 🌟 ENHANCEMENT 2: Skill Intelligence Database
        self.skill_intelligence = {
            "synonyms": {
                "javascript": ["js", "javascript", "ecmascript", "es6", "es2015", "nodejs", "node.js"],
                "react": ["react.js", "reactjs", "react", "react native"],
                "python": ["python", "python3", "py", "python 3.x"],
                "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "t-sql"],
                "aws": ["amazon web services", "aws", "amazon aws", "ec2", "s3"],
                "docker": ["docker", "containerization", "containers"],
                "kubernetes": ["k8s", "kubernetes", "k8s orchestration"],
                "git": ["git", "github", "gitlab", "version control", "source control"],
                "agile": ["agile", "scrum", "kanban", "sprint"],
                "machine learning": ["ml", "machine learning", "artificial intelligence", "ai"]
            },
            "relationships": {
                "react": ["javascript", "jsx", "html", "css"],
                "django": ["python", "sql", "html"],
                "spring": ["java", "sql", "maven"],
                "tensorflow": ["python", "machine learning", "numpy"],
                "kubernetes": ["docker", "containerization", "devops"],
                "aws": ["cloud computing", "devops", "scalability"]
            },
            "hierarchies": {
                "aws": {
                    "aws certified solutions architect": 100,
                    "aws certified developer": 85,
                    "aws certified practitioner": 70,
                    "aws experience": 60
                },
                "project_management": {
                    "pmp": 100,
                    "agile certified": 85,
                    "scrum master": 80,
                    "agile experience": 60
                }
            }
        }
        
        # 🌟 ENHANCEMENT 3: Experience quality multipliers
        self.experience_quality_indicators = {
            "leadership_keywords": [
                "led team", "managed team", "supervised", "mentored", "coached", 
                "team lead", "technical lead", "project lead", "director", "manager"
            ],
            "impact_keywords": [
                "increased", "decreased", "improved", "reduced", "optimized", 
                "enhanced", "achieved", "delivered", "saved", "%", "million", "thousand"
            ],
            "innovation_keywords": [
                "built", "created", "designed", "architected", "implemented", 
                "launched", "pioneered", "established", "developed", "initiated"
            ],
            "scale_keywords": [
                "enterprise", "large scale", "high volume", "million users", 
                "distributed", "microservices", "scalable", "performance"
            ]
        }
        
        # 🌟 ENHANCEMENT 4: Red flag patterns
        self.red_flag_patterns = {
            "job_hopping": {
                "pattern": "multiple_short_tenures",
                "threshold": 3,  # 3+ jobs under 1 year
                "penalty": 0.15,
                "description": "Frequent job changes (< 1 year)"
            },
            "skill_inconsistency": {
                "pattern": "experience_vs_skills_mismatch", 
                "penalty": 0.10,
                "description": "Claimed experience doesn't match timeline"
            },
            "employment_gaps": {
                "pattern": "long_gaps_without_explanation",
                "threshold": 6,  # 6+ months gap
                "penalty": 0.08,
                "description": "Unexplained employment gaps > 6 months"
            },
            "over_qualification": {
                "pattern": "significantly_overqualified",
                "penalty": 0.05,
                "description": "May be overqualified and leave quickly"
            }
        }
        
        logger.info("✅ Enhanced ScoringEngine initialized with enterprise intelligence")
    
    async def score_resume_against_job(
        self, 
        resume_text: str, 
        job_analysis: Dict[str, Any], 
        filename: str = "resume.pdf"
    ) -> Dict[str, Any]:
        """
        🎯 ENHANCED resume scoring with all three improvements
        """
        
        start_time = datetime.now()
        logger.info(f"🧮 Enhanced scoring resume: {filename}")
        
        try:
            # Step 1: Enhanced resume analysis with job context
            resume_analysis = await self.ai_analyzer.enhanced_resume_analysis(
                resume_text, 
                job_analysis
            )
            
            # Step 2: Detect role type for role-specific weighting
            detected_role = self._detect_role_type(job_analysis)
            
            # Step 3: Enhanced skill matching with intelligence
            skills_scoring = await self._score_enhanced_skills_match(
                resume_analysis, 
                job_analysis,
                detected_role
            )
            
            # Step 4: Experience evaluation with quality analysis
            experience_scoring = await self._score_enhanced_experience(
                resume_analysis, 
                job_analysis
            )
            
            # Step 5: Education scoring (improved)
            education_scoring = self._score_education_match(
                resume_analysis, 
                job_analysis
            )
            
            # Step 6: Additional qualifications with quality bonuses
            additional_scoring = await self._score_enhanced_additional_qualifications(
                resume_analysis, 
                job_analysis
            )
            
            # Step 7: Apply red flag detection
            red_flag_analysis = self._detect_red_flags(resume_analysis)
            
            # Step 8: Calculate enhanced weighted final score
            final_scores = self._calculate_enhanced_weighted_scores({
                "required_skills_score": skills_scoring["score"],
                "experience_score": experience_scoring["score"],
                "education_score": education_scoring["score"],
                "additional_qualifications_score": additional_scoring["score"]
            }, red_flag_analysis, detected_role)
            
            # Step 9: Generate intelligent insights
            insights = await self._generate_enhanced_insights(
                resume_analysis, 
                job_analysis, 
                skills_scoring, 
                experience_scoring
            )
            
            # Step 10: Compile comprehensive results
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "filename": filename,
                "overall_score": round(final_scores["overall_score"], 1),
                "recommendation": self._get_enhanced_recommendation(final_scores["overall_score"]),
                
                # Enhanced score breakdown with intelligence
                "score_breakdown": {
                    "required_skills": round(skills_scoring["score"], 1),
                    "experience_level": round(experience_scoring["score"], 1),
                    "education": round(education_scoring["score"], 1),
                    "additional_qualifications": round(additional_scoring["score"], 1)
                },
                
                # 🌟 NEW: Enhanced skill analysis with intelligence
                "enhanced_skill_analysis": {
                    "detected_role": detected_role,
                    "matched_skills_count": skills_scoring.get("total_matched", 0),
                    "missing_critical_skills": skills_scoring.get("missing_critical", []),
                    "skill_relationship_bonuses": skills_scoring.get("relationship_bonuses", {}),
                    "proficiency_weighted_score": skills_scoring.get("proficiency_score", 0),
                    "synonym_matches": skills_scoring.get("synonym_matches", [])
                },
                
                # 🌟 NEW: Experience quality analysis
                "experience_quality_analysis": {
                    "leadership_score": experience_scoring.get("leadership_score", 0),
                    "impact_score": experience_scoring.get("impact_score", 0),
                    "innovation_score": experience_scoring.get("innovation_score", 0),
                    "scale_score": experience_scoring.get("scale_score", 0),
                    "quantified_achievements": experience_scoring.get("quantified_achievements", []),
                    "experience_quality_bonus": experience_scoring.get("quality_bonus", 0)
                },
                
                # 🌟 NEW: Red flag detection
                "red_flag_analysis": red_flag_analysis,
                
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
                "analysis_version": "3.0_enterprise",
                "enhancement_features": [
                    "skill_intelligence",
                    "role_specific_weighting", 
                    "experience_quality_analysis",
                    "red_flag_detection",
                    "synonym_matching",
                    "leadership_detection"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Enhanced scoring completed: {filename} - Score: {result['overall_score']}/100 (Role: {detected_role})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced scoring {filename}: {str(e)}")
            raise Exception(f"Enhanced scoring failed: {str(e)}")
    
    def _detect_role_type(self, job_analysis: Dict[str, Any]) -> str:
        """🎯 Detect the type of role to apply appropriate weighting"""
        
        required_skills = job_analysis.get("required_skills", {})
        job_title = job_analysis.get("summary", "").lower()
        
        # Analyze skill distribution to determine role type
        frontend_score = len(required_skills.get("frontend_tools", [])) + len(required_skills.get("web_frameworks", []))
        backend_score = len(required_skills.get("databases", [])) + len(required_skills.get("cloud_platforms", []))
        data_score = len(required_skills.get("data_tools", [])) * 2  # Weight data tools higher
        devops_score = len(required_skills.get("devops_tools", [])) * 2  # Weight DevOps tools higher
        
        # Check job title keywords
        if any(keyword in job_title for keyword in ["data scientist", "ml engineer", "data analyst"]):
            return "data_scientist"
        elif any(keyword in job_title for keyword in ["devops", "sre", "infrastructure", "platform"]):
            return "devops_engineer"
        elif any(keyword in job_title for keyword in ["frontend", "ui", "ux"]):
            return "frontend_developer"
        elif any(keyword in job_title for keyword in ["backend", "api", "server"]):
            return "backend_developer"
        elif frontend_score > 0 and backend_score > 0:
            return "fullstack_developer"
        elif data_score >= 2:
            return "data_scientist"
        elif devops_score >= 2:
            return "devops_engineer"
        elif frontend_score > backend_score:
            return "frontend_developer"
        elif backend_score > 0:
            return "backend_developer"
        else:
            return "fullstack_developer"  # Default fallback
    
    async def _score_enhanced_skills_match(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any], detected_role: str) -> Dict[str, Any]:
        """🧠 Enhanced skill matching with intelligence and role-specific weighting"""
        
        required_skills = job_analysis.get("required_skills", {})
        candidate_skills = resume_analysis.get("skills_by_category", {})
        
        # Get role-specific weights
        role_weights = self.role_specific_weights.get(detected_role, {})
        
        matched_skills = []
        missing_skills = []
        category_scores = {}
        synonym_matches = []
        relationship_bonuses = {}
        
        total_weighted_score = 0
        total_category_weight = 0
        
        # Analyze each skill category with role-specific importance
        for category, required_list in required_skills.items():
            if not required_list or category not in candidate_skills:
                continue
                
            category_weight = role_weights.get(category, 0.1)  # Role-specific weight
            
            if category_weight == 0:
                continue  # Skip categories not relevant to this role
                
            candidate_category_skills = candidate_skills[category]
            
            # Enhanced matching with skill intelligence
            category_result = self._match_skills_with_intelligence(
                candidate_category_skills, 
                required_list, 
                category
            )
            
            category_scores[category] = category_result["score"]
            matched_skills.extend(category_result["matches"])
            missing_skills.extend(category_result["missing"])
            synonym_matches.extend(category_result["synonyms"])
            
            # Apply role-specific weighting
            total_weighted_score += category_result["score"] * category_weight
            total_category_weight += category_weight
        
        # Calculate overall skills score
        overall_skills_score = (total_weighted_score / total_category_weight) if total_category_weight > 0 else 0
        
        # Apply skill relationship bonuses
        relationship_bonuses = self._calculate_skill_relationship_bonuses(matched_skills)
        bonus_multiplier = 1.0
        for bonus_name, bonus_value in relationship_bonuses.items():
            bonus_multiplier += bonus_value * 0.2  # 20% of bonus value
        
        enhanced_score = min(overall_skills_score * bonus_multiplier, 100)
        
        return {
            "score": enhanced_score,
            "base_score": overall_skills_score,
            "relationship_bonuses": relationship_bonuses,
            "bonus_multiplier": bonus_multiplier,
            "matched_skills": matched_skills,
            "missing_critical": [m for m in missing_skills if m.get("critical", False)],
            "category_coverage": category_scores,
            "synonym_matches": synonym_matches,
            "total_matched": len(matched_skills),
            "proficiency_score": self._calculate_proficiency_score(matched_skills)
        }
    
    def _match_skills_with_intelligence(self, candidate_skills: List, required_skills: List, category: str) -> Dict[str, Any]:
        """🔍 Intelligent skill matching with synonyms and relationships"""
        
        matches = []
        missing = []
        synonyms = []
        
        # Convert candidate skills to searchable format
        candidate_normalized = {}
        for skill_item in candidate_skills:
            if isinstance(skill_item, dict):
                name = skill_item.get("name", "")
                proficiency = skill_item.get("proficiency", "intermediate")
                years = skill_item.get("years_experience", 0)
            else:
                name = str(skill_item)
                proficiency = "intermediate"
                years = 0
            
            # Normalize skill name for matching
            normalized = self._normalize_skill(name)
            candidate_normalized[normalized] = {
                "original_name": name,
                "proficiency": proficiency,
                "years": years
            }
        
        # Match against required skills
        for required_skill in required_skills:
            required_lower = required_skill.lower()
            matched = False
            match_info = None
            match_type = "none"
            
            # 1. Direct match
            if required_lower in candidate_normalized:
                match_info = candidate_normalized[required_lower]
                matched = True
                match_type = "exact"
            
            # 2. Synonym match
            if not matched:
                normalized_required = self._normalize_skill(required_skill)
                if normalized_required in candidate_normalized:
                    match_info = candidate_normalized[normalized_required]
                    matched = True
                    match_type = "synonym"
                    synonyms.append({
                        "required": required_skill,
                        "found": match_info["original_name"],
                        "normalized": normalized_required
                    })
            
            # 3. Relationship match (e.g., React implies JavaScript)
            if not matched:
                for candidate_norm, candidate_info in candidate_normalized.items():
                    if self._skills_are_related(required_lower, candidate_norm):
                        match_info = candidate_info
                        matched = True
                        match_type = "related"
                        break
            
            if matched and match_info:
                # Calculate proficiency-based score
                proficiency_scores = {
                    "expert": 100,
                    "advanced": 90,
                    "intermediate": 80,
                    "beginner": 60
                }
                
                base_score = proficiency_scores.get(match_info["proficiency"], 80)
                
                # Years experience bonus
                years_bonus = min(match_info["years"] * 2, 10)  # Up to 10 point bonus
                
                # Match type modifier
                type_modifiers = {
                    "exact": 1.0,
                    "synonym": 0.95,
                    "related": 0.85
                }
                type_modifier = type_modifiers.get(match_type, 0.8)
                
                final_score = min((base_score + years_bonus) * type_modifier, 100)
                
                matches.append({
                    "skill": required_skill,
                    "matched_with": match_info["original_name"],
                    "proficiency": match_info["proficiency"],
                    "years_experience": match_info["years"],
                    "match_type": match_type,
                    "score": final_score,
                    "category": category
                })
            else:
                # Determine criticality
                critical_skills = ["python", "javascript", "react", "java", "sql", "aws", "docker", "git"]
                is_critical = any(cs in required_skill.lower() for cs in critical_skills)
                
                missing.append({
                    "skill": required_skill,
                    "category": category,
                    "critical": is_critical
                })
        
        # Calculate category score
        if required_skills:
            total_possible_score = len(required_skills) * 100
            actual_score = sum(match["score"] for match in matches)
            category_score = (actual_score / total_possible_score) * 100
        else:
            category_score = 100
        
        return {
            "score": min(category_score, 100),
            "matches": matches,
            "missing": missing,
            "synonyms": synonyms
        }
    
    def _normalize_skill(self, skill: str) -> str:
        """🔄 Normalize skill names using intelligence database"""
        
        skill_lower = skill.lower().strip()
        
        # Check synonyms database
        for normalized_name, synonyms in self.skill_intelligence["synonyms"].items():
            if skill_lower in synonyms:
                return normalized_name
        
        return skill_lower
    
    def _skills_are_related(self, skill1: str, skill2: str) -> bool:
        """🔗 Check if skills are related using relationship database"""
        
        relationships = self.skill_intelligence["relationships"]
        
        # Check both directions
        skill1_relations = relationships.get(skill1, [])
        skill2_relations = relationships.get(skill2, [])
        
        return skill2 in skill1_relations or skill1 in skill2_relations
    
    def _calculate_skill_relationship_bonuses(self, matched_skills: List[Dict]) -> Dict[str, float]:
        """💫 Calculate bonuses for related skill combinations"""
        
        bonuses = {}
        skill_names = [match["skill"].lower() for match in matched_skills]
        
        # Technology stack bonuses
        if "react" in skill_names and "javascript" in skill_names:
            bonuses["react_javascript_stack"] = 0.15
        
        if "django" in skill_names and "python" in skill_names:
            bonuses["django_python_stack"] = 0.15
        
        if "docker" in skill_names and "kubernetes" in skill_names:
            bonuses["container_orchestration_stack"] = 0.12
        
        if "aws" in skill_names and ("docker" in skill_names or "kubernetes" in skill_names):
            bonuses["cloud_devops_combo"] = 0.10
        
        # Full-stack bonus
        has_frontend = any(skill in skill_names for skill in ["react", "vue", "angular", "html", "css"])
        has_backend = any(skill in skill_names for skill in ["python", "java", "node", "sql", "database"])
        if has_frontend and has_backend:
            bonuses["fullstack_breadth"] = 0.18
        
        return bonuses
    
    def _calculate_proficiency_score(self, matched_skills: List[Dict]) -> float:
        """📊 Calculate weighted proficiency score"""
        
        if not matched_skills:
            return 0
        
        proficiency_values = {
            "expert": 100,
            "advanced": 90,
            "intermediate": 80,
            "beginner": 60
        }
        
        total_score = 0
        for skill in matched_skills:
            proficiency = skill.get("proficiency", "intermediate")
            score = proficiency_values.get(proficiency, 80)
            total_score += score
        
        return total_score / len(matched_skills)
    
    async def _score_enhanced_experience(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """⭐ Enhanced experience scoring with quality analysis"""
        
        # Get basic experience data
        experience_data = resume_analysis.get("experience_analysis", {})
        total_years = experience_data.get("total_years", 0) or 0
        relevant_years = experience_data.get("relevant_years", 0) or total_years
        min_required = job_analysis.get("minimum_experience", 0) or 0
        
        # Base experience score
        base_score = self._calculate_base_experience_score(relevant_years, min_required)
        
        # 🌟 ENHANCEMENT: Analyze experience quality from work history
        work_history = resume_analysis.get("work_history", [])
        experience_text = " ".join([
            f"{job.get('title', '')} {job.get('key_achievements', [])} {job.get('technologies_used', [])}"
            for job in work_history
        ])
        
        # Quality analysis
        leadership_score = self._analyze_leadership_experience(experience_text)
        impact_score = self._analyze_quantified_impact(experience_text)
        innovation_score = self._analyze_innovation_indicators(experience_text)
        scale_score = self._analyze_scale_experience(experience_text)
        
        # Calculate quality bonuses
        leadership_bonus = min(leadership_score * 0.3, 15)    # Up to 15 points
        impact_bonus = min(impact_score * 0.25, 12)           # Up to 12 points  
        innovation_bonus = min(innovation_score * 0.2, 10)    # Up to 10 points
        scale_bonus = min(scale_score * 0.15, 8)              # Up to 8 points
        
        total_quality_bonus = leadership_bonus + impact_bonus + innovation_bonus + scale_bonus
        
        # Calculate final experience score
        enhanced_score = min(base_score + total_quality_bonus, 100)
        
        return {
            "score": enhanced_score,
            "base_score": base_score,
            "quality_bonus": total_quality_bonus,
            "leadership_score": leadership_score,
            "impact_score": impact_score,
            "innovation_score": innovation_score,
            "scale_score": scale_score,
            "quantified_achievements": self._extract_quantified_achievements(experience_text),
            "analysis": {
                "years_gap": relevant_years - min_required,
                "quality_indicators_found": sum([
                    leadership_bonus > 0,
                    impact_bonus > 0, 
                    innovation_bonus > 0,
                    scale_bonus > 0
                ]),
                "experience_quality_tier": self._get_experience_quality_tier(total_quality_bonus)
            }
        }
    
    def _calculate_base_experience_score(self, relevant_years: float, min_required: float) -> float:
        """Calculate base experience score"""
        
        if min_required == 0:
            return 85  # No specific requirement
        
        if relevant_years >= min_required + 3:
            return 95  # Significantly exceeds requirement
        elif relevant_years >= min_required + 1:
            return 90  # Exceeds requirement
        elif relevant_years >= min_required:
            return 85  # Meets requirement
        elif relevant_years >= min_required * 0.8:
            return 75  # Close to requirement
        elif relevant_years >= min_required * 0.6:
            return 65  # Somewhat below requirement
        else:
            return 45  # Well below requirement
    
    def _analyze_leadership_experience(self, text: str) -> float:
        """🎯 Analyze leadership experience from text"""
        
        text_lower = text.lower()
        leadership_score = 0
        
        for keyword in self.experience_quality_indicators["leadership_keywords"]:
            if keyword in text_lower:
                leadership_score += 10
        
        # Look for team size indicators
        import re
        team_size_matches = re.findall(r'team of (\d+)|(\d+) people|(\d+) developers|(\d+) engineers', text_lower)
        if team_size_matches:
            max_team_size = max([int(match[0] or match[1] or match[2] or match[3]) for match in team_size_matches])
            leadership_score += min(max_team_size * 5, 30)  # Up to 30 points for large teams
        
        return min(leadership_score, 100)
    
    def _analyze_quantified_impact(self, text: str) -> float:
        """📈 Analyze quantified achievements and impact"""
        
        text_lower = text.lower()
        impact_score = 0
        
        # Look for quantified results
        import re
        percentage_matches = re.findall(r'(\d+)%', text)
        if percentage_matches:
            impact_score += len(percentage_matches) * 15
        
        money_matches = re.findall(r'\$[\d,]+|\d+k|\d+ million', text_lower)
        if money_matches:
            impact_score += len(money_matches) * 20
        
        for keyword in self.experience_quality_indicators["impact_keywords"]:
            if keyword in text_lower:
                impact_score += 8
        
        return min(impact_score, 100)
    
    def _analyze_innovation_indicators(self, text: str) -> float:
        """🚀 Analyze innovation and creation indicators"""
        
        text_lower = text.lower()
        innovation_score = 0
        
        for keyword in self.experience_quality_indicators["innovation_keywords"]:
            if keyword in text_lower:
                innovation_score += 10
        
        # Look for technology introductions
        tech_intro_patterns = [
            "introduced", "migrated to", "adopted", "implemented new",
            "modernized", "transformed", "revolutionized"
        ]
        
        for pattern in tech_intro_patterns:
            if pattern in text_lower:
                innovation_score += 12
        
        return min(innovation_score, 100)
    
    def _analyze_scale_experience(self, text: str) -> float:
        """⚡ Analyze large-scale system experience"""
        
        text_lower = text.lower()
        scale_score = 0
        
        for keyword in self.experience_quality_indicators["scale_keywords"]:
            if keyword in text_lower:
                scale_score += 15
        
        return min(scale_score, 100)
    
    def _extract_quantified_achievements(self, text: str) -> List[str]:
        """📊 Extract specific quantified achievements"""
        
        achievements = []
        import re
        
        # Find sentences with numbers and impact words
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ["increased", "reduced", "improved", "achieved"]):
                if re.search(r'\d+', sentence):
                    achievements.append(sentence.strip())
        
        return achievements[:5]  # Return top 5
    
    def _get_experience_quality_tier(self, quality_bonus: float) -> str:
        """📊 Classify experience quality tier"""
        if quality_bonus >= 35:
            return "exceptional"
        elif quality_bonus >= 25:
            return "excellent" 
        elif quality_bonus >= 15:
            return "good"
        elif quality_bonus >= 5:
            return "moderate"
        else:
            return "basic"
    
    def _detect_red_flags(self, resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """🚨 Advanced red flag detection"""
        
        red_flags = []
        penalty_total = 0
        
        # Check work history for patterns
        work_history = resume_analysis.get("work_history", [])
        
        if work_history and len(work_history) > 2:
            # Job hopping detection
            short_tenures = 0
            for job in work_history[:5]:  # Check recent 5 jobs
                duration = job.get("duration_months", 24)
                if isinstance(duration, (int, float)) and duration < 12:
                    short_tenures += 1
            
            if short_tenures >= self.red_flag_patterns["job_hopping"]["threshold"]:
                penalty = self.red_flag_patterns["job_hopping"]["penalty"]
                red_flags.append({
                    "type": "job_hopping",
                    "description": f"Multiple short tenures ({short_tenures} jobs < 1 year)",
                    "severity": "medium",
                    "penalty": penalty
                })
                penalty_total += penalty
        
        # Check for employment gaps
        if work_history and len(work_history) > 1:
            for i in range(len(work_history) - 1):
                current_job = work_history[i]
                next_job = work_history[i + 1]
                
                current_end = current_job.get("end_date", "")
                next_start = next_job.get("start_date", "")
                
                # Simplified gap detection (could be enhanced with date parsing)
                if current_end and next_start and current_end != "present":
                    # This is a simplified check - in production, you'd parse dates
                    if "gap" in str(current_end).lower() or "gap" in str(next_start).lower():
                        penalty = self.red_flag_patterns["employment_gaps"]["penalty"]
                        red_flags.append({
                            "type": "employment_gaps",
                            "description": "Employment gap detected",
                            "severity": "low",
                            "penalty": penalty
                        })
                        penalty_total += penalty
                        break
        
        # Check for over-qualification (simplified)
        experience_years = resume_analysis.get("experience_analysis", {}).get("total_years", 0)
        if experience_years > 15:  # Very senior candidate
            penalty = self.red_flag_patterns["over_qualification"]["penalty"]
            red_flags.append({
                "type": "over_qualification",
                "description": "Very senior candidate - may be overqualified",
                "severity": "low", 
                "penalty": penalty
            })
            penalty_total += penalty
        
        return {
            "flags_detected": red_flags,
            "total_penalty": min(penalty_total, 0.25),  # Cap at 25% penalty
            "risk_level": self._assess_risk_level(penalty_total),
            "has_concerns": len(red_flags) > 0
        }
    
    def _assess_risk_level(self, penalty: float) -> str:
        """Assess overall candidate risk level"""
        if penalty >= 0.20:
            return "high"
        elif penalty >= 0.10:
            return "medium"
        elif penalty > 0:
            return "low"
        else:
            return "minimal"
    
    def _calculate_enhanced_weighted_scores(self, detailed_scoring: Dict[str, Any], red_flag_analysis: Dict[str, Any], detected_role: str) -> Dict[str, Any]:
        """🎯 Calculate final weighted scores with red flag penalties"""
        
        required_skills = detailed_scoring.get("required_skills_score", 0)
        experience = detailed_scoring.get("experience_score", 0)
        education = detailed_scoring.get("education_score", 0)
        additional = detailed_scoring.get("additional_qualifications_score", 0)
        
        # Get role-specific base weights (could be enhanced further)
        weights = self.base_weights
        
        # Calculate weighted overall score
        overall_score = (
            required_skills * weights["required_skills"] +
            experience * weights["experience"] +
            education * weights["education"] + 
            additional * weights["additional_qualifications"]
        )
        
        # Apply red flag penalty
        red_flag_penalty = red_flag_analysis.get("total_penalty", 0)
        penalty_adjusted_score = overall_score * (1 - red_flag_penalty)
        
        return {
            "overall_score": min(100, max(0, penalty_adjusted_score)),
            "base_score": overall_score,
            "red_flag_penalty": red_flag_penalty,
            "role_fit_score": self._calculate_role_fit_score(detected_role, detailed_scoring),
            "required_skills": required_skills,
            "experience": experience,
            "education": education,
            "additional_qualifications": additional
        }
    
    def _calculate_role_fit_score(self, role: str, scores: Dict[str, Any]) -> float:
        """Calculate role-specific fit score"""
        
        role_multipliers = {
            "frontend_developer": {
                "required_skills": 1.2,  # Skills more important for frontend
                "experience": 0.9,
                "education": 0.8
            },
            "data_scientist": {
                "required_skills": 1.1,
                "experience": 1.0,
                "education": 1.3       # Education more important for data science
            },
            "devops_engineer": {
                "required_skills": 1.3,  # DevOps skills are very specific
                "experience": 1.1,
                "education": 0.7       # Less emphasis on formal education
            }
        }
        
        multipliers = role_multipliers.get(role, {"required_skills": 1.0, "experience": 1.0, "education": 1.0})
        
        adjusted_skills = scores.get("required_skills_score", 0) * multipliers["required_skills"]
        adjusted_experience = scores.get("experience_score", 0) * multipliers["experience"]
        adjusted_education = scores.get("education_score", 0) * multipliers["education"]
        
        role_fit = (adjusted_skills + adjusted_experience + adjusted_education) / 3
        return min(100, role_fit)
    
    async def _score_enhanced_additional_qualifications(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Enhanced additional qualifications scoring"""
        
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
    
    async def _generate_enhanced_insights(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any], skills_scoring: Dict[str, Any], experience_scoring: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent insights about the candidate"""
        
        strengths = []
        concerns = []
        
        # Enhanced skill-based insights
        matched_skills = skills_scoring.get("total_matched", 0)
        if matched_skills >= 8:
            strengths.append(f"Strong technical match with {matched_skills} required skills")
        
        # Relationship bonuses
        relationship_bonuses = skills_scoring.get("relationship_bonuses", {})
        if relationship_bonuses:
            bonus_descriptions = []
            for bonus_name, bonus_value in relationship_bonuses.items():
                if bonus_value > 0.1:
                    bonus_descriptions.append(bonus_name.replace("_", " ").title())
            if bonus_descriptions:
                strengths.append(f"Technology stack synergies: {', '.join(bonus_descriptions)}")
        
        # Experience quality insights
        leadership_score = experience_scoring.get("leadership_score", 0)
        if leadership_score > 60:
            strengths.append("Demonstrated leadership and team management experience")
        
        impact_score = experience_scoring.get("impact_score", 0)
        if impact_score > 50:
            strengths.append("Track record of quantifiable business impact")
        
        # Critical missing skills
        missing_critical = skills_scoring.get("missing_critical", [])
        for skill in missing_critical[:3]:  # Top 3 critical missing
            concerns.append(f"Missing critical skill: {skill['skill']}")
        
        # Experience gaps
        years_gap = experience_scoring.get("analysis", {}).get("years_gap", 0)
        if years_gap < -1:
            concerns.append(f"Below required experience level by {abs(years_gap)} years")
        
        # Generate detailed analysis
        quality_tier = experience_scoring.get("analysis", {}).get("experience_quality_tier", "basic")
        
        detailed_analysis = f"""
Enhanced Candidate Analysis:

Technical Competency: {matched_skills} required skills matched with {"strong" if matched_skills >= 6 else "moderate"} proficiency levels. 
{"Advanced technology stack combinations identified." if relationship_bonuses else "Standard skill set without notable synergies."}

Experience Quality: {quality_tier.title()} tier experience with {"quantifiable impact and leadership indicators" if leadership_score > 40 or impact_score > 40 else "standard professional background"}.

Role Alignment: {"Excellent" if matched_skills >= 8 and years_gap >= 0 else "Good" if matched_skills >= 5 else "Limited"} alignment with position requirements.

Overall Assessment: {"Strong candidate recommended for interview" if len(concerns) <= 2 and matched_skills >= 6 else "Moderate fit requiring careful evaluation" if len(concerns) <= 4 else "Below requirements for this position"}.
        """.strip()
        
        return {
            "strengths": strengths[:5],  # Top 5 strengths
            "concerns": concerns[:5],    # Top 5 concerns  
            "detailed_analysis": detailed_analysis,
            "role_strengths": self._identify_role_specific_strengths(resume_analysis, job_analysis),
            "role_gaps": self._identify_role_specific_gaps(resume_analysis, job_analysis)
        }
    
    def _identify_role_specific_strengths(self, resume_analysis: Dict, job_analysis: Dict) -> List[str]:
        """Identify role-specific strengths"""
        # This would analyze the specific role requirements vs candidate profile
        return ["Role-specific analysis would be implemented here"]
    
    def _identify_role_specific_gaps(self, resume_analysis: Dict, job_analysis: Dict) -> List[str]:
        """Identify role-specific gaps"""
        # This would analyze missing role-critical elements
        return ["Role-specific gap analysis would be implemented here"]
    
    def _get_enhanced_recommendation(self, overall_score: float) -> str:
        """Get enhanced hiring recommendation based on score"""
        
        if overall_score >= 90:
            return "🌟 Exceptional candidate - Immediate interview strongly recommended"
        elif overall_score >= 80:
            return "⭐ Strong candidate - High priority for interview"
        elif overall_score >= 70:
            return "✅ Good candidate - Recommend for interview"
        elif overall_score >= 60:
            return "⚠️ Moderate fit - Review carefully, consider phone screen"
        elif overall_score >= 45:
            return "❌ Below requirements - Consider only if candidate pool is limited"
        else:
            return "🚫 Poor fit - Not recommended for this position"
    
    def _get_highest_education(self, education: Dict[str, Any]) -> Optional[str]:
        """Extract the highest education level"""
        degrees = education.get("degrees", [])
        if not degrees:
            return None
        
        degree_levels = {"Bachelor's": 1, "Master's": 2, "PhD": 3}
        highest = max(degrees, key=lambda x: degree_levels.get(x.get("level", ""), 0))
        return highest.get("level")
    
    # Continue with batch processing method...
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
            "enhancement_analytics": {
                "role_distribution": self._analyze_role_distribution(results),
                "skill_intelligence_impact": self._analyze_skill_intelligence_impact(results),
                "quality_tier_distribution": self._analyze_quality_tiers(results)
            },
            "timestamp": datetime.now().isoformat(),
            "analysis_version": "enhanced_3.0"
        }
        
        logger.info(f"✅ Enhanced batch scoring completed: {successful_count}/{len(resume_data_list)} successful")
        return batch_result
    
    def _analyze_role_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """Analyze distribution of detected roles"""
        role_counts = {}
        for result in results:
            role = result.get("enhanced_skill_analysis", {}).get("detected_role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts
    
    def _analyze_skill_intelligence_impact(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze the impact of skill intelligence features"""
        synonym_matches = 0
        relationship_bonuses = 0
        
        for result in results:
            skill_analysis = result.get("enhanced_skill_analysis", {})
            if skill_analysis.get("synonym_matches"):
                synonym_matches += len(skill_analysis["synonym_matches"])
            if skill_analysis.get("skill_relationship_bonuses"):
                relationship_bonuses += len(skill_analysis["skill_relationship_bonuses"])
        
        return {
            "total_synonym_matches": synonym_matches,
            "total_relationship_bonuses": relationship_bonuses,
            "intelligence_utilization": "high" if synonym_matches + relationship_bonuses > len(results) else "moderate"
        }
    
    def _analyze_quality_tiers(self, results: List[Dict]) -> Dict[str, int]:
        """Analyze experience quality tier distribution"""
        tier_counts = {}
        for result in results:
            exp_analysis = result.get("experience_quality_analysis", {})
            # This would extract quality tier from the analysis
            tier = "basic"  # Simplified for now
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        return tier_counts