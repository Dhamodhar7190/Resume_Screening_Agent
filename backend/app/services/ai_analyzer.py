import google.generativeai as genai
from app.core.config import settings
from typing import Dict, List, Optional, Any
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Enhanced AI service for intelligent resume and job analysis using Google Gemini"""
    
    def __init__(self):
        self.provider = "google"
        self.model = None
        
        # Enhanced skill categories for better organization
        self.skill_categories = {
            "programming_languages": ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "TypeScript"],
            "web_frameworks": ["React", "Angular", "Vue.js", "Django", "Flask", "FastAPI", "Express.js", "Spring", "Laravel", "Rails"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server", "Cassandra", "DynamoDB"],
            "cloud_platforms": ["AWS", "Azure", "Google Cloud", "GCP", "DigitalOcean", "Heroku", "Vercel", "Netlify"],
            "devops_tools": ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "Terraform", "Ansible", "Chef", "Puppet"],
            "data_tools": ["Pandas", "NumPy", "TensorFlow", "PyTorch", "Scikit-learn", "Apache Spark", "Hadoop", "Airflow"],
            "frontend_tools": ["HTML", "CSS", "Sass", "Bootstrap", "Tailwind CSS", "Webpack", "Vite", "jQuery"],
            "mobile_development": ["iOS", "Android", "React Native", "Flutter", "Xamarin", "Ionic"],
            "testing_tools": ["Jest", "Pytest", "Selenium", "Cypress", "JUnit", "Mocha", "PHPUnit"],
            "version_control": ["Git", "GitHub", "GitLab", "Bitbucket", "SVN"],
            "project_management": ["Agile", "Scrum", "Kanban", "Jira", "Trello", "Asana", "Monday.com"]
        }
        
        # Initialize Google Gemini client
        if settings.google_api_key:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Enhanced Google Gemini client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Gemini: {e}")
        else:
            logger.warning("⚠️ No Google API key found - check your .env file")
    
    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Enhanced job description analysis with better categorization"""
        
        prompt = f"""
Analyze this job description and extract detailed information. Return ONLY a valid JSON object:

Job Description:
{job_description}

Return exactly this JSON structure:
{{
    "required_skills": {{
        "programming_languages": ["list of required programming languages"],
        "web_frameworks": ["list of required web frameworks"],
        "databases": ["list of required databases"],
        "cloud_platforms": ["list of required cloud platforms"],
        "devops_tools": ["list of required DevOps tools"],
        "data_tools": ["list of required data science/ML tools"],
        "frontend_tools": ["list of required frontend tools"],
        "mobile_development": ["list of mobile development requirements"],
        "testing_tools": ["list of testing frameworks/tools"],
        "version_control": ["list of version control systems"],
        "project_management": ["list of project management methodologies"],
        "other_technical": ["other technical skills not in above categories"],
        "soft_skills": ["communication", "leadership", "teamwork", etc.]
    }},
    "preferred_skills": {{
        "programming_languages": ["nice-to-have programming languages"],
        "web_frameworks": ["nice-to-have frameworks"],
        "databases": ["nice-to-have databases"],
        "cloud_platforms": ["nice-to-have cloud platforms"],
        "devops_tools": ["nice-to-have DevOps tools"],
        "data_tools": ["nice-to-have data tools"],
        "other_technical": ["other nice-to-have technical skills"],
        "soft_skills": ["nice-to-have soft skills"]
    }},
    "minimum_experience": number_of_years_required_or_null,
    "preferred_experience": number_of_years_preferred_or_null,
    "education_requirements": {{
        "required_degree": "Bachelor's/Master's/PhD or null",
        "preferred_degree": "Bachelor's/Master's/PhD or null",
        "field_of_study": ["Computer Science", "Engineering", etc.],
        "certifications": ["list of required/preferred certifications"]
    }},
    "key_responsibilities": ["main job duties and responsibilities"],
    "industry": "industry or domain",
    "seniority_level": "junior/mid/senior/lead/principal/executive",
    "remote_work": "remote/hybrid/onsite/flexible",
    "team_size": "size of team they'll work with or null",
    "role_type": "individual_contributor/team_lead/manager/director",
    "summary": "comprehensive summary of the ideal candidate profile"
}}

Rules:
- Extract specific skills and technologies mentioned
- Categorize skills properly into the provided categories
- Distinguish between required vs preferred qualifications
- Use null for missing information
- Be specific about experience levels and educational requirements
- Return only the JSON, no other text
"""
        
        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(prompt)
            
            try:
                job_analysis = json.loads(response)
                logger.info("✅ Enhanced job description analyzed successfully")
                return job_analysis
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                return self._extract_json_from_response(response)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing job description: {str(e)}")
            raise Exception(f"Failed to analyze job description: {str(e)}")
    
    async def analyze_resume_content(self, resume_text: str, job_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """Enhanced resume analysis with detailed skill categorization and career insights"""
        
        job_context = ""
        if job_analysis:
            job_context = f"""

JOB CONTEXT: This resume is being evaluated for a position requiring:
- Technical Skills: {job_analysis.get('required_skills', {})}
- Experience Level: {job_analysis.get('minimum_experience', 'Not specified')} years
- Education: {job_analysis.get('education_requirements', {})}
- Seniority: {job_analysis.get('seniority_level', 'Not specified')}
"""
        
        prompt = f"""
Analyze this resume with enhanced detail and intelligence. Return ONLY a valid JSON object:

Resume Text:
{resume_text}
{job_context}

Return exactly this JSON structure:
{{
    "candidate_summary": "2-3 sentence professional summary of the candidate",
    "contact_info": {{
        "name": "full name or null",
        "email": "email address or null",
        "phone": "phone number or null",
        "linkedin": "linkedin profile or null",
        "location": "city, state/country or null",
        "portfolio": "portfolio website or null"
    }},
    "skills_by_category": {{
        "programming_languages": [
            {{"name": "Python", "proficiency": "expert/advanced/intermediate/beginner", "years_experience": 3}}
        ],
        "web_frameworks": [
            {{"name": "React", "proficiency": "advanced", "years_experience": 2}}
        ],
        "databases": [
            {{"name": "PostgreSQL", "proficiency": "intermediate", "years_experience": 1}}
        ],
        "cloud_platforms": [...],
        "devops_tools": [...],
        "data_tools": [...],
        "frontend_tools": [...],
        "mobile_development": [...],
        "testing_tools": [...],
        "version_control": [...],
        "project_management": [...],
        "other_technical": [...],
        "soft_skills": [
            {{"name": "Leadership", "evidence": "Led team of 5 developers"}}
        ]
    }},
    "experience_analysis": {{
        "total_years": number_of_years_total_experience,
        "relevant_years": number_of_years_relevant_to_job,
        "career_progression": "junior_to_mid/mid_to_senior/senior_to_lead/lateral/unclear",
        "industry_experience": ["fintech", "healthcare", "e-commerce", etc.],
        "role_types": ["individual_contributor", "team_lead", "manager", "director"],
        "company_sizes": ["startup", "mid_size", "enterprise"],
        "current_level": "junior/mid/senior/lead/principal/director"
    }},
    "work_history": [
        {{
            "company": "company name",
            "title": "job title",
            "start_date": "YYYY-MM or YYYY",
            "end_date": "YYYY-MM or present",
            "duration_months": number_of_months,
            "key_achievements": ["quantified achievements with impact"],
            "technologies_used": ["tech stack used in this role"],
            "team_size": "size of team or null",
            "role_type": "individual_contributor/team_lead/manager"
        }}
    ],
    "education": {{
        "degrees": [
            {{
                "level": "Bachelor's/Master's/PhD",
                "field": "Computer Science",
                "institution": "university name",
                "graduation_year": "YYYY",
                "gpa": "3.8/4.0 or null",
                "relevant_coursework": ["relevant courses"]
            }}
        ],
        "certifications": [
            {{
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "YYYY-MM",
                "expiry": "YYYY-MM or null"
            }}
        ]
    }},
    "projects": [
        {{
            "name": "project name",
            "description": "what the project does",
            "technologies": ["tech stack used"],
            "role": "your role in the project",
            "impact": "quantified impact or outcome"
        }}
    ],
    "achievements": [
        {{
            "title": "achievement title",
            "description": "achievement description",
            "impact": "quantified impact",
            "date": "YYYY or null"
        }}
    ],
    "resume_quality": {{
        "formatting_score": score_0_to_100,
        "completeness_score": score_0_to_100,
        "quantification_score": score_0_to_100,
        "ats_friendly": true_or_false,
        "keyword_optimization": score_0_to_100,
        "overall_quality": score_0_to_100,
        "improvement_suggestions": ["specific suggestions for resume improvement"]
    }},
    "leadership_indicators": {{
        "has_leadership_experience": true_or_false,
        "team_sizes_managed": [5, 3, 12],
        "leadership_skills": ["mentoring", "project management", "strategic planning"],
        "leadership_evidence": ["specific examples of leadership"]
    }},
    "career_insights": {{
        "specializations": ["areas of expertise"],
        "career_trajectory": "ascending/stable/transitioning/unclear",
        "job_stability": "stable/frequent_changes/gap_periods",
        "learning_attitude": "continuous_learner/specialized/traditional",
        "innovation_indicators": ["open source contributions", "patents", "side projects"],
        "remote_work_experience": true_or_false
    }}
}}

Analysis Guidelines:
- Extract skills with proficiency levels based on context clues
- Estimate experience years for each skill from job history
- Identify quantified achievements (numbers, percentages, impact)
- Assess resume quality and ATS-friendliness
- Analyze career progression and growth trajectory
- Look for leadership and innovation indicators
- Use null for missing information
- Be specific and evidence-based in assessments
- Return only the JSON, no other text
"""
        
        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(prompt)
            
            try:
                resume_analysis = json.loads(response)
                
                # Post-process to ensure data quality
                resume_analysis = self._enhance_resume_analysis(resume_analysis)
                
                logger.info("✅ Enhanced resume analyzed successfully")
                return resume_analysis
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                return self._extract_json_from_response(response)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing resume: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
    
    def _enhance_resume_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process resume analysis to ensure data quality and consistency"""
        
        # Ensure all skill categories exist
        if "skills_by_category" not in analysis:
            analysis["skills_by_category"] = {}
        
        for category in self.skill_categories.keys():
            if category not in analysis["skills_by_category"]:
                analysis["skills_by_category"][category] = []
        
        # Ensure soft_skills category exists
        if "soft_skills" not in analysis["skills_by_category"]:
            analysis["skills_by_category"]["soft_skills"] = []
        
        # Calculate total skills count
        total_technical_skills = sum(
            len(skills) for category, skills in analysis["skills_by_category"].items() 
            if category != "soft_skills"
        )
        analysis["total_technical_skills"] = total_technical_skills
        analysis["total_soft_skills"] = len(analysis["skills_by_category"].get("soft_skills", []))
        
        # Enhanced career insights
        if "experience_analysis" in analysis:
            exp = analysis["experience_analysis"]
            
            # Calculate career velocity (progression speed)
            total_years = exp.get("total_years", 0)
            current_level = exp.get("current_level", "junior")
            
            if total_years > 0:
                if current_level in ["lead", "principal", "director"] and total_years < 8:
                    analysis["career_velocity"] = "fast"
                elif current_level == "senior" and total_years < 5:
                    analysis["career_velocity"] = "fast"
                elif current_level == "mid" and total_years < 3:
                    analysis["career_velocity"] = "fast"
                else:
                    analysis["career_velocity"] = "normal"
            else:
                analysis["career_velocity"] = "unknown"
        
        # Add skill diversity score
        skills_categories_with_skills = sum(
            1 for category, skills in analysis["skills_by_category"].items()
            if category != "soft_skills" and len(skills) > 0
        )
        analysis["skill_diversity_score"] = min(100, (skills_categories_with_skills / len(self.skill_categories)) * 100)
        
        return analysis
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API asynchronously with enhanced configuration"""
        if not self.model:
            raise Exception("Google Gemini model not initialized. Check your API key in .env file.")
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=8000,  # Increased for more detailed analysis
                        temperature=0.1,  # Low temperature for consistent results
                        candidate_count=1,
                        top_p=0.8,
                        top_k=40
                    )
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Google Gemini API error: {str(e)}")
            if "API_KEY" in str(e).upper():
                raise Exception("Invalid Google API key. Please check your GOOGLE_API_KEY in .env file.")
            raise Exception(f"Google Gemini API error: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Google Gemini with enhanced diagnostics"""
        try:
            if not self.model:
                return {
                    "status": "error",
                    "message": "Google API key not configured. Add GOOGLE_API_KEY to .env file.",
                    "provider": "google_gemini"
                }
            
            # Test with enhanced analysis prompt
            test_response = await self._call_gemini('''
Analyze this test: "John Doe, Software Engineer with 3 years Python experience at Tech Corp."
Return exactly: {"test": "success", "message": "Enhanced Google Gemini is working", "skills_found": ["Python"]}
            ''')
            
            return {
                "status": "connected",
                "provider": "google_gemini",
                "model": "gemini-1.5-flash",
                "features": ["enhanced_skill_categorization", "career_analysis", "resume_quality_scoring"],
                "test_response": test_response[:200] + "..." if len(test_response) > 200 else test_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "provider": "google_gemini"
            }
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from AI response that might have extra text"""
        try:
            # Look for JSON block in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                raise Exception("No valid JSON found in AI response")
        except Exception as e:
            logger.error(f"Failed to extract JSON from response: {str(e)}")
            return {
                "error": "Failed to parse enhanced AI response", 
                "raw_response": response[:300] + "..." if len(response) > 300 else response,
                "message": "The AI returned invalid JSON format",
                "skills_by_category": {category: [] for category in self.skill_categories.keys()},
                "candidate_summary": "Analysis failed - please try again",
                "resume_quality": {"overall_quality": 0, "improvement_suggestions": ["Resume analysis failed"]}
            }