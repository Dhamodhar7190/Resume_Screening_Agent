import google.generativeai as genai
from app.core.config import settings
from typing import Dict, List, Optional, Any
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Service for AI-powered analysis using Google Gemini"""
    
    def __init__(self):
        self.provider = "google"
        self.model = None
        
        # Initialize Google Gemini client
        if settings.google_api_key:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free model
                logger.info("✅ Google Gemini client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Gemini: {e}")
        else:
            logger.warning("⚠️ No Google API key found - check your .env file")
    
    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description and extract structured requirements using Google Gemini
        """
        
        prompt = f"""
Analyze this job description and extract information. Return ONLY a valid JSON object with no additional text or explanation:

Job Description:
{job_description}

Return exactly this JSON structure:
{{
    "required_skills": ["list of must-have technical skills"],
    "preferred_skills": ["list of nice-to-have skills"],
    "minimum_experience": number_of_years_required_or_null,
    "education_requirements": ["degree requirements"],
    "key_responsibilities": ["main job duties"],
    "industry": "industry or domain",
    "seniority_level": "junior/mid/senior/executive",
    "remote_work": "remote/hybrid/onsite/null",
    "summary": "brief summary of the role"
}}

Rules:
- Extract specific skills like "Python", "AWS", "SQL", not generic terms
- Use null for missing information
- Return only the JSON, no other text
"""
        
        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(prompt)
            
            # Try to parse JSON response
            try:
                job_analysis = json.loads(response)
                logger.info("✅ Job description analyzed successfully with Google Gemini")
                return job_analysis
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                return self._extract_json_from_response(response)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing job description: {str(e)}")
            raise Exception(f"Failed to analyze job description: {str(e)}")
    
    async def analyze_resume_content(self, resume_text: str, job_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze resume content and extract structured information using Google Gemini
        """
        
        job_context = ""
        if job_analysis:
            job_context = f"""

CONTEXT: This resume is being evaluated for a position requiring:
- Required skills: {job_analysis.get('required_skills', [])}
- Experience level: {job_analysis.get('minimum_experience', 'Not specified')} years  
- Education: {job_analysis.get('education_requirements', [])}
"""
        
        prompt = f"""
Analyze this resume and extract information. Return ONLY a valid JSON object with no additional text or explanation:

Resume Text:
{resume_text}
{job_context}

Return exactly this JSON structure:
{{
    "candidate_name": "full name or null",
    "email": "email address or null",
    "phone": "phone number or null",
    "linkedin": "linkedin profile or null",
    "years_experience": number_of_years_total_experience_or_null,
    "education_level": "highest degree or null",
    "technical_skills": ["list of technical skills found"],
    "soft_skills": ["list of soft skills"],
    "work_experience": [
        {{
            "company": "company name",
            "title": "job title",
            "duration": "time period",
            "key_achievements": ["main accomplishments"]
        }}
    ],
    "education": [
        {{
            "degree": "degree type", 
            "institution": "school name",
            "year": "graduation year or period"
        }}
    ],
    "certifications": ["list of certifications"],
    "projects": ["notable projects mentioned"],
    "summary": "brief professional summary"
}}

Rules:
- Extract only information clearly stated in the resume
- Use null for missing information
- Return only the JSON, no other text
"""
        
        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(prompt)
            
            try:
                resume_analysis = json.loads(response)
                logger.info("✅ Resume analyzed successfully with Google Gemini")
                return resume_analysis
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                return self._extract_json_from_response(response)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing resume: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API asynchronously"""
        if not self.model:
            raise Exception("Google Gemini model not initialized. Check your API key in .env file.")
        
        try:
            # Run the synchronous call in a thread pool to make it async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=settings.max_tokens,
                        temperature=settings.temperature,
                        candidate_count=1,
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
        """Test connection to Google Gemini"""
        try:
            if not self.model:
                return {
                    "status": "error",
                    "message": "Google API key not configured. Add GOOGLE_API_KEY to .env file."
                }
            
            # Test with simple prompt
            test_response = await self._call_gemini('Respond with this exact JSON: {"test": "success", "message": "Google Gemini is working"}')
            
            return {
                "status": "connected",
                "provider": "google_gemini",
                "model": "gemini-1.5-flash",
                "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
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
                "error": "Failed to parse AI response", 
                "raw_response": response[:200] + "..." if len(response) > 200 else response,
                "message": "The AI returned invalid JSON format"
            }