import google.generativeai as genai
from app.core.config import settings
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
import asyncio
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    🌟 ENTERPRISE-GRADE AI ANALYZER 🌟
    
    Enhanced with:
    1. Skill Intelligence & Synonym Mapping
    2. Role-Specific Scoring Weights  
    3. Experience Quality Analysis
    """
    
    def __init__(self):
        self.provider = "google"
        self.model = None
        
        # 🌟 ENHANCEMENT 1: SKILL INTELLIGENCE DATABASE
        self.skill_synonyms = {
            # Programming Languages
            "javascript": ["js", "javascript", "java script", "node.js", "nodejs", "ecmascript"],
            "python": ["python", "python3", "python 3", "py", "python3.x"],
            "java": ["java", "java 8", "java 11", "java 17", "jdk", "openjdk"],
            "typescript": ["typescript", "ts", "type script"],
            "csharp": ["c#", "csharp", "c sharp", ".net", "dotnet"],
            "php": ["php", "php7", "php8", "php 7", "php 8"],
            "go": ["go", "golang", "go lang"],
            "rust": ["rust", "rust lang"],
            "swift": ["swift", "swift 5", "swiftui"],
            "kotlin": ["kotlin", "kt"],
            
            # Web Frameworks
            "react": ["react", "react.js", "reactjs", "react js", "react native"],
            "angular": ["angular", "angularjs", "angular.js", "angular 2+", "ng"],
            "vue": ["vue", "vue.js", "vuejs", "vue js", "vue 3", "nuxt"],
            "django": ["django", "django rest", "drf", "django framework"],
            "flask": ["flask", "flask-restful", "flask api"],
            "express": ["express", "express.js", "expressjs", "express js"],
            "spring": ["spring", "spring boot", "springboot", "spring framework"],
            "laravel": ["laravel", "laravel framework"],
            "rails": ["rails", "ruby on rails", "ror"],
            "fastapi": ["fastapi", "fast api"],
            
            # Databases
            "postgresql": ["postgresql", "postgres", "pg", "psql"],
            "mysql": ["mysql", "my sql"],
            "mongodb": ["mongodb", "mongo", "mongo db"],
            "redis": ["redis", "redis cache"],
            "elasticsearch": ["elasticsearch", "elastic search", "es"],
            "sqlite": ["sqlite", "sql lite"],
            
            # Cloud Platforms
            "aws": ["aws", "amazon web services", "amazon aws", "ec2", "s3", "lambda"],
            "azure": ["azure", "microsoft azure", "azure cloud"],
            "gcp": ["gcp", "google cloud", "google cloud platform", "gce"],
            "docker": ["docker", "containerization", "containers"],
            "kubernetes": ["kubernetes", "k8s", "kube"],
            
            # DevOps & Tools
            "jenkins": ["jenkins", "jenkins ci", "jenkins cd"],
            "git": ["git", "github", "gitlab", "version control"],
            "terraform": ["terraform", "tf", "infrastructure as code"],
            "ansible": ["ansible", "configuration management"],
            "nginx": ["nginx", "web server", "reverse proxy"],
            
            # Testing
            "jest": ["jest", "jest testing", "javascript testing"],
            "pytest": ["pytest", "python testing"],
            "junit": ["junit", "java testing"],
            "selenium": ["selenium", "web automation", "browser testing"],
            "cypress": ["cypress", "e2e testing"],
            
            # Data & AI
            "pandas": ["pandas", "data analysis", "data manipulation"],
            "numpy": ["numpy", "numerical computing"],
            "tensorflow": ["tensorflow", "tf", "machine learning", "deep learning"],
            "pytorch": ["pytorch", "torch", "deep learning"],
            "scikit-learn": ["scikit-learn", "sklearn", "machine learning"],
            "spark": ["spark", "apache spark", "big data"],
        }
        
        # 🌟 ENHANCEMENT 2: ROLE-SPECIFIC SCORING WEIGHTS
        self.role_weights = {
            "frontend_developer": {
                "programming_languages": 0.25,  # JavaScript/TypeScript focus
                "web_frameworks": 0.30,         # React/Angular/Vue critical
                "frontend_tools": 0.20,         # CSS/HTML/Webpack important
                "databases": 0.05,              # Less critical
                "devops_tools": 0.05,          # Nice to have
                "cloud_platforms": 0.05,       # Bonus
                "testing_tools": 0.10          # Important for quality
            },
            "backend_developer": {
                "programming_languages": 0.30,  # Core backend languages
                "web_frameworks": 0.25,         # API frameworks
                "databases": 0.25,              # Critical for data handling
                "cloud_platforms": 0.10,        # Deployment knowledge
                "devops_tools": 0.05,          # CI/CD awareness
                "testing_tools": 0.05           # Unit/integration testing
            },
            "fullstack_developer": {
                "programming_languages": 0.25,  # Balanced across stack
                "web_frameworks": 0.20,         # Both frontend & backend
                "databases": 0.15,              # Data layer understanding
                "frontend_tools": 0.15,         # UI/UX skills
                "cloud_platforms": 0.10,        # Deployment skills
                "devops_tools": 0.10,          # End-to-end ownership
                "testing_tools": 0.05
            },
            "devops_engineer": {
                "devops_tools": 0.35,          # Core DevOps tools
                "cloud_platforms": 0.30,       # Infrastructure management
                "programming_languages": 0.15, # Scripting languages
                "databases": 0.10,             # Database administration
                "web_frameworks": 0.05,        # Application understanding
                "testing_tools": 0.05          # Testing pipelines
            },
            "data_scientist": {
                "data_tools": 0.40,            # ML/Data science tools
                "programming_languages": 0.25, # Python/R focus
                "databases": 0.20,             # Data querying
                "cloud_platforms": 0.10,       # Cloud ML services
                "web_frameworks": 0.03,        # Dashboard/API creation
                "testing_tools": 0.02
            },
            "mobile_developer": {
                "mobile_development": 0.40,    # iOS/Android/React Native
                "programming_languages": 0.30, # Swift/Kotlin/Java
                "databases": 0.10,             # Mobile data storage
                "cloud_platforms": 0.10,       # Backend services
                "web_frameworks": 0.05,        # Hybrid development
                "testing_tools": 0.05          # Mobile testing
            },
            "default": {  # Generic software developer
                "programming_languages": 0.25,
                "web_frameworks": 0.20,
                "databases": 0.15,
                "cloud_platforms": 0.10,
                "devops_tools": 0.10,
                "frontend_tools": 0.10,
                "testing_tools": 0.05,
                "mobile_development": 0.03,
                "data_tools": 0.02
            }
        }
        
        # 🌟 ENHANCEMENT 3: EXPERIENCE QUALITY INDICATORS
        self.experience_quality_patterns = {
            "leadership_indicators": [
                r"led\s+(?:a\s+)?team\s+of\s+(\d+)",
                r"managed\s+(\d+)\s+(?:people|developers|engineers)",
                r"supervised\s+(\d+)",
                r"mentored\s+(\d+)",
                r"guided\s+(?:a\s+)?team",
                r"team\s+lead",
                r"tech\s+lead",
                r"senior\s+(?:developer|engineer)",
                r"principal\s+(?:developer|engineer)",
                r"architect"
            ],
            "impact_indicators": [
                r"increased\s+(?:performance|efficiency|revenue)\s+by\s+(\d+)%",
                r"reduced\s+(?:time|cost|errors)\s+by\s+(\d+)%",
                r"improved\s+.*\s+by\s+(\d+)%",
                r"saved\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|million|m)?",
                r"generated\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|million|m)?",
                r"processed\s+(\d+(?:,\d+)*)\s+(?:requests|transactions|users)",
                r"scaled\s+to\s+(\d+(?:,\d+)*)\s+(?:users|requests|concurrent)",
                r"serving\s+(\d+(?:,\d+)*)\s+(?:users|customers)"
            ],
            "innovation_indicators": [
                r"architected\s+(?:new|from\s+scratch)",
                r"designed\s+(?:and\s+implemented|new)",
                r"built\s+from\s+(?:ground\s+up|scratch)",
                r"pioneered",
                r"introduced\s+(?:new|modern)",
                r"migrated\s+(?:from|legacy)",
                r"modernized",
                r"refactored",
                r"optimized",
                r"automated"
            ],
            "collaboration_indicators": [
                r"cross-functional\s+(?:team|collaboration)",
                r"collaborated\s+with",
                r"worked\s+closely\s+with",
                r"partnered\s+with",
                r"coordinated\s+with",
                r"stakeholder\s+management",
                r"client\s+(?:facing|interaction)",
                r"presented\s+to",
                r"communicated\s+with"
            ]
        }
        
        # Initialize Google Gemini client
        if settings.google_api_key:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Advanced AI Analyzer initialized with enterprise features")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Gemini: {e}")
        else:
            logger.warning("⚠️ No Google API key found - check your .env file")
    
    def _detect_role_type_fixed(self, job_title: str, job_description: str, required_skills: dict = None) -> str:
        """
        🎯 IMPROVED: More accurate role detection with better text analysis
        """
        
        if not job_title:
            job_title = ""
        
        combined_text = f"{job_title} {job_description}".lower()
        logger.info(f"🔍 Analyzing role for: '{job_title}' (text length: {len(combined_text)})")
        
        # 🌟 IMPROVEMENT 1: Enhanced technology detection with more comprehensive lists
        frontend_techs = [
            "react", "angular", "vue", "javascript", "typescript", "jsx", "tsx",
            "html", "css", "scss", "sass", "bootstrap", "material-ui", "angular material",
            "frontend", "front-end", "ui", "user interface", "responsive design"
        ]
        
        backend_techs = [
            "python", "django", "flask", "fastapi", "java", "spring", "spring boot",
            "node.js", "nodejs", "express", "api", "rest", "restful", "graphql",
            "backend", "back-end", "server-side", "microservices", "django rest framework",
            "rest framework", "php", "laravel", "ruby", "rails", "go", "golang", ".net", "c#"
        ]
        
        fullstack_indicators = [
            "full stack", "fullstack", "full-stack", "end-to-end", "end to end",
            "frontend and backend", "backend and frontend", "front-end and back-end"
        ]
        
        devops_techs = [
            "docker", "kubernetes", "k8s", "jenkins", "aws", "azure", "gcp", "terraform", 
            "ansible", "devops", "ci/cd", "infrastructure", "deployment", "containerization"
        ]
        
        data_techs = [
            "python", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "machine learning",
            "data science", "ml", "ai", "artificial intelligence", "jupyter", "spark"
        ]
        
        # 🌟 IMPROVEMENT 2: Better counting with partial matches
        def count_tech_mentions(tech_list, text):
            count = 0
            matches = []
            for tech in tech_list:
                if tech in text:
                    count += 1
                    matches.append(tech)
            return count, matches
        
        frontend_count, frontend_matches = count_tech_mentions(frontend_techs, combined_text)
        backend_count, backend_matches = count_tech_mentions(backend_techs, combined_text)
        devops_count, devops_matches = count_tech_mentions(devops_techs, combined_text)
        data_count, data_matches = count_tech_mentions(data_techs, combined_text)
        
        # Check for explicit fullstack indicators
        fullstack_explicit = any(indicator in combined_text for indicator in fullstack_indicators)
        
        logger.info(f"🔢 Tech analysis:")
        logger.info(f"   Frontend: {frontend_count} matches {frontend_matches[:3]}")
        logger.info(f"   Backend: {backend_count} matches {backend_matches[:3]}")
        logger.info(f"   DevOps: {devops_count} matches {devops_matches[:3]}")
        logger.info(f"   Data: {data_count} matches {data_matches[:3]}")
        logger.info(f"   Fullstack explicit: {fullstack_explicit}")
        
        # 🌟 IMPROVEMENT 3: More intelligent decision logic
        
        # Explicit fullstack indicators trump everything
        if fullstack_explicit:
            logger.info(f"🏆 FULLSTACK: Explicit fullstack indicators found")
            return "fullstack_developer"
        
        # Strong fullstack profile (good in both frontend and backend)
        if frontend_count >= 3 and backend_count >= 3:
            logger.info(f"🏆 FULLSTACK: Strong in both stacks (FE:{frontend_count}, BE:{backend_count})")
            return "fullstack_developer"
        
        # Moderate fullstack profile 
        if frontend_count >= 2 and backend_count >= 2:
            logger.info(f"🏆 FULLSTACK: Moderate fullstack profile (FE:{frontend_count}, BE:{backend_count})")
            return "fullstack_developer"
        
        # Data science specialization
        if data_count >= 4:
            logger.info(f"🏆 DATA_SCIENTIST: Strong data science focus ({data_count} matches)")
            return "data_scientist"
        
        # DevOps specialization (but not if strong programming background)
        if devops_count >= 4 and (frontend_count + backend_count) < 4:
            logger.info(f"🏆 DEVOPS: Strong DevOps focus ({devops_count} matches)")
            return "devops_engineer"
        
        # Backend specialization
        if backend_count >= 4 and frontend_count < 2:
            logger.info(f"🏆 BACKEND: Strong backend focus ({backend_count} matches)")
            return "backend_developer"
        
        # Frontend specialization  
        if frontend_count >= 4 and backend_count < 2:
            logger.info(f"🏆 FRONTEND: Strong frontend focus ({frontend_count} matches)")
            return "frontend_developer"
        
        # Default logic based on highest count
        if backend_count > frontend_count:
            logger.info(f"🏆 BACKEND: Backend dominant ({backend_count} vs {frontend_count})")
            return "backend_developer"
        elif frontend_count > backend_count:
            logger.info(f"🏆 FRONTEND: Frontend dominant ({frontend_count} vs {backend_count})")
            return "frontend_developer"
        else:
            # Equal or both low - default to backend for most developer positions
            logger.info(f"🏆 DEFAULT: Equal counts, defaulting to backend")
            return "backend_developer"


    # 🎯 Also need to adjust DevOps weights to not over-penalize Python/Django
    def _get_role_specific_weights_fixed(self, detected_role: str) -> dict:
        """
        🎯 FIXED: Balanced weights that don't over-penalize certain roles
        """
        
        weights = {
            "fullstack_developer": {
                "programming_languages": 0.25,    # Balanced across stack
                "web_frameworks": 0.25,           # Critical for both FE & BE
                "databases": 0.15,                # Data layer important
                "frontend_tools": 0.10,           # UI skills matter
                "cloud_platforms": 0.10,          # Deployment knowledge
                "devops_tools": 0.08,            # CI/CD awareness
                "testing_tools": 0.05,           # Quality assurance
                "version_control": 0.02           # Basic requirement
            },
            
            "backend_developer": {
                "programming_languages": 0.35,    # Core backend languages
                "web_frameworks": 0.25,           # API frameworks crucial
                "databases": 0.25,                # Data handling critical
                "cloud_platforms": 0.08,          # Deployment knowledge
                "devops_tools": 0.05,            # CI/CD awareness
                "testing_tools": 0.02            # Unit testing
            },
            
            "frontend_developer": {
                "web_frameworks": 0.35,           # React/Angular focus
                "programming_languages": 0.25,    # JS/TS critical
                "frontend_tools": 0.25,           # CSS/HTML/Webpack
                "databases": 0.05,                # Less critical
                "cloud_platforms": 0.05,          # Deployment basics
                "devops_tools": 0.03,            # Nice to have
                "testing_tools": 0.02            # Frontend testing
            },
            
            "devops_engineer": {
                "devops_tools": 0.40,            # Core focus
                "cloud_platforms": 0.35,         # Infrastructure critical
                "programming_languages": 0.15,   # Scripting languages
                "databases": 0.05,               # DB administration
                "web_frameworks": 0.03,          # App understanding
                "testing_tools": 0.02            # Testing pipelines
            },
            
            "data_scientist": {
                "data_tools": 0.45,              # ML/DS tools critical
                "programming_languages": 0.25,   # Python/R focus
                "databases": 0.20,               # Data querying
                "cloud_platforms": 0.07,         # Cloud ML services
                "web_frameworks": 0.02,          # Dashboards/APIs
                "testing_tools": 0.01
            },
            
            "mobile_developer": {
                "mobile_development": 0.45,      # iOS/Android/RN
                "programming_languages": 0.30,   # Swift/Kotlin/Java
                "databases": 0.10,               # Mobile data storage
                "cloud_platforms": 0.10,         # Backend services
                "web_frameworks": 0.03,          # Hybrid development
                "testing_tools": 0.02            # Mobile testing
            }
        }
        
        return weights.get(detected_role, weights["backend_developer"])  # Safe fallback


    def _create_skill_synonym_database(self) -> dict:
        """
        🧠 Enhanced skill synonym database
        """
        return {
            # Database synonyms
            "database_skills": {
                "postgresql": ["postgres", "pg", "postgresql", "psql"],
                "mysql": ["mysql", "my sql", "mariadb"],
                "mongodb": ["mongodb", "mongo", "mongo db", "nosql"],
                "sqlite": ["sqlite", "sql lite"],
                "redis": ["redis", "redis cache", "in-memory db"]
            },
            
            # Programming language synonyms  
            "programming_languages": {
                "python": ["python", "python3", "python 3", "py"],
                "javascript": ["javascript", "js", "ecmascript", "es6", "node.js", "nodejs"],
                "typescript": ["typescript", "ts"],
                "java": ["java", "java 8", "java 11", "jdk"]
            },
            
            # Framework synonyms
            "web_frameworks": {
                "django": ["django", "django rest framework", "drf"],
                "react": ["react", "react.js", "reactjs", "react js"],
                "angular": ["angular", "angular 2+", "angularjs", "ng"],
                "vue": ["vue", "vue.js", "vuejs"]
            },
            
            # Cloud platform synonyms
            "cloud_platforms": {
                "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "amazon aws"],
                "azure": ["azure", "microsoft azure"],
                "gcp": ["gcp", "google cloud", "google cloud platform"]
            }
        }


    def _calculate_skill_match_with_synonyms(self, candidate_skill: str, required_skill: str) -> tuple:
        """
        🔍 Enhanced skill matching with synonym support
        Returns: (match_score: float, match_type: str)
        """
        candidate_lower = candidate_skill.lower().strip()
        required_lower = required_skill.lower().strip()
        
        # 1. Exact match
        if candidate_lower == required_lower:
            return (1.0, "exact")
        
        # 2. Synonym match
        synonyms = self._create_skill_synonym_database()
        for category, skill_groups in synonyms.items():
            for canonical_skill, variations in skill_groups.items():
                if required_lower in variations and candidate_lower in variations:
                    return (0.95, "synonym")
        
        # 3. Partial match (contains)
        if required_lower in candidate_lower or candidate_lower in required_lower:
            return (0.8, "partial")
        
        # 4. Related technologies (e.g., MySQL → PostgreSQL)
        database_relations = {
            "mysql": ["postgresql", "sqlite", "mariadb"],
            "postgresql": ["mysql", "sqlite"],
            "mongodb": ["dynamodb", "couchdb"],
        }
        
        for base_skill, related_skills in database_relations.items():
            if base_skill in required_lower and any(rel in candidate_lower for rel in related_skills):
                return (0.75, "related")
            if base_skill in candidate_lower and any(rel in required_lower for rel in related_skills):
                return (0.75, "related")
        
        # 5. No match
        return (0.0, "none")
    
    def _normalize_skill(self, skill: str) -> str:
        """🧠 Enhanced skill normalization with synonym mapping"""
        
        skill_lower = skill.lower().strip()
        
        # Check against our synonym database
        for canonical_skill, synonyms in self.skill_synonyms.items():
            if skill_lower in synonyms:
                return canonical_skill
        
        # Fallback: clean and standardize
        skill_clean = re.sub(r'[^\w\s\-\.\+#]', '', skill_lower)
        skill_clean = re.sub(r'\s+', ' ', skill_clean).strip()
        
        return skill_clean
    
    def _calculate_skill_relationships(self, candidate_skills: List[str]) -> Dict[str, float]:
        """🔗 Calculate skill relationship bonuses"""
        
        bonuses = {}
        normalized_skills = [self._normalize_skill(skill) for skill in candidate_skills]
        
        # Technology stack bonuses
        tech_stacks = {
            "mern_stack": (["mongodb", "express", "react", "javascript"], 1.2),
            "mean_stack": (["mongodb", "express", "angular", "javascript"], 1.2),
            "django_python": (["python", "django", "postgresql"], 1.15),
            "spring_java": (["java", "spring", "mysql"], 1.15),
            "react_ecosystem": (["react", "redux", "webpack", "jest"], 1.1),
            "aws_cloud": (["aws", "docker", "terraform", "kubernetes"], 1.2),
            "data_science": (["python", "pandas", "numpy", "tensorflow"], 1.25),
        }
        
        for stack_name, (required_skills, multiplier) in tech_stacks.items():
            matches = sum(1 for req_skill in required_skills if req_skill in normalized_skills)
            if matches >= len(required_skills) * 0.75:  # 75% of stack present
                bonus_strength = (matches / len(required_skills)) * (multiplier - 1.0)
                bonuses[stack_name] = bonus_strength
        
        return bonuses
    
    def _analyze_experience_quality(self, work_history: List[Dict], resume_text: str) -> Dict[str, Any]:
        """⭐ Advanced experience quality analysis"""
        
        quality_metrics = {
            "leadership_score": 0,
            "impact_score": 0,
            "innovation_score": 0,
            "collaboration_score": 0,
            "progression_score": 0,
            "quantified_achievements": [],
            "leadership_evidence": [],
            "impact_evidence": []
        }
        
        text_to_analyze = resume_text.lower()
        
        # 1. Leadership Analysis
        for pattern in self.experience_quality_patterns["leadership_indicators"]:
            matches = re.findall(pattern, text_to_analyze, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and match.isdigit():
                    team_size = int(match)
                    quality_metrics["leadership_score"] += min(team_size * 10, 50)  # Cap at 50
                    quality_metrics["leadership_evidence"].append(f"Led team of {team_size}")
                elif "lead" in match.lower() or "architect" in match.lower():
                    quality_metrics["leadership_score"] += 25
                    quality_metrics["leadership_evidence"].append(match)
        
        # 2. Impact Analysis
        for pattern in self.experience_quality_patterns["impact_indicators"]:
            matches = re.findall(pattern, text_to_analyze, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    quality_metrics["impact_score"] += 20
                    quality_metrics["quantified_achievements"].append(match)
                    quality_metrics["impact_evidence"].append(f"Quantified impact: {match}")
        
        # 3. Innovation Analysis
        innovation_count = 0
        for pattern in self.experience_quality_patterns["innovation_indicators"]:
            matches = len(re.findall(pattern, text_to_analyze, re.IGNORECASE))
            innovation_count += matches
        quality_metrics["innovation_score"] = min(innovation_count * 15, 75)
        
        # 4. Collaboration Analysis
        collaboration_count = 0
        for pattern in self.experience_quality_patterns["collaboration_indicators"]:
            matches = len(re.findall(pattern, text_to_analyze, re.IGNORECASE))
            collaboration_count += matches
        quality_metrics["collaboration_score"] = min(collaboration_count * 10, 50)
        
        # 5. Career Progression Analysis
        if work_history and len(work_history) > 1:
            progression_indicators = ["senior", "lead", "principal", "architect", "manager", "director"]
            
            # Sort by most recent (assuming work_history is chronological)
            recent_roles = [job.get("title", "").lower() for job in work_history[:3]]
            
            progression_score = 0
            for i, indicator in enumerate(progression_indicators):
                if any(indicator in role for role in recent_roles):
                    progression_score = (len(progression_indicators) - i) * 10
                    break
            
            quality_metrics["progression_score"] = progression_score
        
        # Calculate overall experience quality score
        total_score = (
            quality_metrics["leadership_score"] * 0.3 +
            quality_metrics["impact_score"] * 0.25 +
            quality_metrics["innovation_score"] * 0.2 +
            quality_metrics["collaboration_score"] * 0.15 +
            quality_metrics["progression_score"] * 0.1
        )
        
        quality_metrics["overall_quality_score"] = min(total_score, 100)
        
        return quality_metrics
    
    async def enhanced_resume_analysis(self, resume_text: str, job_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """🚀 ENHANCED resume analysis with all three improvements"""
        
        # Get basic analysis first
        basic_analysis = await self.analyze_resume_content(resume_text, job_analysis)
        
        # 🌟 ENHANCEMENT 1: Apply skill intelligence
        enhanced_skills = {}
        if "skills_by_category" in basic_analysis:
            for category, skills in basic_analysis["skills_by_category"].items():
                if isinstance(skills, list):
                    normalized_skills = []
                    for skill_item in skills:
                        if isinstance(skill_item, dict) and "name" in skill_item:
                            normalized_name = self._normalize_skill(skill_item["name"])
                            skill_item["normalized_name"] = normalized_name
                            normalized_skills.append(skill_item)
                        elif isinstance(skill_item, str):
                            normalized_skills.append({
                                "name": skill_item,
                                "normalized_name": self._normalize_skill(skill_item),
                                "proficiency": "intermediate"
                            })
                    enhanced_skills[category] = normalized_skills
                else:
                    enhanced_skills[category] = skills
        
        # Calculate skill relationship bonuses
        all_skills = []
        for category_skills in enhanced_skills.values():
            if isinstance(category_skills, list):
                all_skills.extend([s.get("normalized_name", s.get("name", "")) 
                                if isinstance(s, dict) else s for s in category_skills])
        
        skill_bonuses = self._calculate_skill_relationships(all_skills)
        
        # 🌟 ENHANCEMENT 3: Analyze experience quality
        work_history = basic_analysis.get("work_history", [])
        experience_quality = self._analyze_experience_quality(work_history, resume_text)
        
        # Combine all enhancements
        enhanced_analysis = {
            **basic_analysis,
            "enhanced_skills": enhanced_skills,
            "skill_relationship_bonuses": skill_bonuses,
            "experience_quality_analysis": experience_quality,
            "enhancement_features": {
                "skill_intelligence": True,
                "experience_quality": True,
                "relationship_bonuses": len(skill_bonuses) > 0
            }
        }
        
        return enhanced_analysis
    
    async def enhanced_job_analysis(self, job_description: str, job_title: str = None) -> Dict[str, Any]:
        """🎯 Enhanced job analysis with role detection"""
        
        # Get basic job analysis
        basic_analysis = await self.analyze_job_description(job_description, job_title)
        
        # 🌟 ENHANCEMENT 2: Detect role type for specific weighting
        detected_role = self._detect_role_type_fixed(job_title or "", job_description)
        role_weights = self.role_weights.get(detected_role, self.role_weights["default"])
        
        # Add enhanced information
        enhanced_analysis = {
            **basic_analysis,
            "detected_role_type": detected_role,
            "role_specific_weights": role_weights,
            "enhancement_features": {
                "role_detection": True,
                "adaptive_weighting": True
            }
        }
        
        return enhanced_analysis
    
    async def calculate_enhanced_score(self, resume_analysis: Dict, job_analysis: Dict) -> Dict[str, Any]:
        """🎯 Calculate final score using all enhancements"""
        
        # Get role-specific weights
        role_weights = job_analysis.get("role_specific_weights", self.role_weights["default"])
        
        # Basic skill matching with intelligence
        enhanced_skills = resume_analysis.get("enhanced_skills", {})
        required_skills = job_analysis.get("required_skills", {})
        
        skill_scores = {}
        total_weighted_score = 0
        total_weight = 0
        
        for category, weight in role_weights.items():
            if weight > 0 and category in required_skills:
                category_score = self._calculate_enhanced_category_score(
                    enhanced_skills.get(category, []),
                    required_skills.get(category, []),
                    resume_analysis.get("skill_relationship_bonuses", {})
                )
                skill_scores[category] = category_score
                total_weighted_score += category_score * weight
                total_weight += weight
        
        # Apply experience quality bonus
        experience_quality = resume_analysis.get("experience_quality_analysis", {})
        experience_bonus = experience_quality.get("overall_quality_score", 0) * 0.1  # 10% bonus
        
        # Calculate final score
        base_score = (total_weighted_score / total_weight) if total_weight > 0 else 0
        final_score = min(base_score + experience_bonus, 100)
        
        return {
            "enhanced_overall_score": round(final_score, 1),
            "base_score": round(base_score, 1),
            "experience_quality_bonus": round(experience_bonus, 1),
            "category_scores": skill_scores,
            "role_weights_applied": role_weights,
            "enhancements_applied": [
                "skill_intelligence",
                "role_specific_weighting", 
                "experience_quality_analysis"
            ]
        }
    
    def _calculate_enhanced_category_score(self, candidate_skills: List, required_skills: List, bonuses: Dict) -> float:
        """Calculate category score with skill intelligence"""
        
        if not required_skills:
            return 100  # No requirements = full score
        
        matched_skills = 0
        total_required = len(required_skills)
        
        # Normalize candidate skills
        candidate_normalized = []
        for skill_item in candidate_skills:
            if isinstance(skill_item, dict):
                normalized = skill_item.get("normalized_name", skill_item.get("name", ""))
                proficiency = skill_item.get("proficiency", "intermediate")
                candidate_normalized.append((normalized.lower(), proficiency))
            else:
                candidate_normalized.append((str(skill_item).lower(), "intermediate"))
        
        # Enhanced matching with synonyms
        for required_skill in required_skills:
            required_normalized = self._normalize_skill(required_skill)
            
            # Check for matches
            for candidate_skill, proficiency in candidate_normalized:
                if (required_normalized == candidate_skill or 
                    required_skill.lower() in candidate_skill or
                    candidate_skill in required_skill.lower()):
                    
                    # Apply proficiency multiplier
                    proficiency_multipliers = {
                        "expert": 1.0,
                        "advanced": 0.9,
                        "intermediate": 0.8,
                        "beginner": 0.6
                    }
                    multiplier = proficiency_multipliers.get(proficiency, 0.8)
                    matched_skills += multiplier
                    break
        
        # Calculate base score
        base_score = (matched_skills / total_required) * 100
        
        # Apply relationship bonuses
        bonus_multiplier = 1.0
        for bonus_name, bonus_value in bonuses.items():
            bonus_multiplier += bonus_value * 0.5  # Scale down bonus impact
        
        final_score = min(base_score * bonus_multiplier, 100)
        return final_score
    
    # Keep all original methods for backward compatibility
    # Add this method to your AIAnalyzer class (in ai_analyzer.py)

    async def analyze_job_description(self, job_description: str, job_title: str = None, use_enhancement: bool = True) -> Dict[str, Any]:
        """Enhanced job description analysis with integrated AI enhancement"""
        
        enhanced_description = job_description
        enhancement_info = {"was_enhanced": False}
        
        # 🌟 INTEGRATED ENHANCEMENT LOGIC
        if use_enhancement:
            try:
                logger.info("🔧 Enhancing job description first...")
                
                # Call the enhancement method
                enhancement_result = await self.enhance_job_description(job_description, job_title)
                
                if "error" not in enhancement_result:
                    # Use enhanced description
                    enhanced_description = enhancement_result["enhanced_description"]
                    job_title = enhancement_result.get("enhanced_title", job_title)
                    
                    enhancement_info = {
                        "was_enhanced": True,
                        "original_description": job_description,
                        "enhanced_description": enhanced_description,
                        "optimization_notes": enhancement_result.get("optimization_notes"),
                        "quality_improvement": enhancement_result.get("quality_score", 0)
                    }
                    
                    logger.info("✅ Job description enhanced successfully")
                else:
                    logger.warning("⚠️ Enhancement failed, using original description")
                    
            except Exception as e:
                logger.warning(f"⚠️ Enhancement failed: {e}, using original description")
        
        # Now analyze the (potentially enhanced) description
        prompt = f"""
    You are an expert HR analyst specializing in technical job requirements. Analyze this job description with HIGH PRECISION and extract detailed information. Return ONLY a valid JSON object.

    ANALYSIS INSTRUCTIONS:
    1. Read the job description completely before categorizing any skills
    2. Distinguish carefully between REQUIRED (must-have) vs PREFERRED (nice-to-have) skills
    3. Be precise with experience level requirements - if it says "3+ years" use 3, not 5
    4. Categorize skills correctly (e.g., "React" = web_frameworks, "Python" = programming_languages)
    5. Only include skills that are explicitly mentioned or clearly implied

    Job Title: {job_title or 'Not specified'}
    Job Description:
    {enhanced_description}

    SKILL CATEGORIZATION EXAMPLES:
    - programming_languages: Python, JavaScript, Java, C#, Go, Rust, PHP, Ruby, TypeScript, Kotlin, Swift
    - web_frameworks: React, Angular, Vue, Django, Flask, Express, Spring Boot, Laravel, FastAPI, Next.js
    - databases: MySQL, PostgreSQL, MongoDB, Redis, DynamoDB, Cassandra, Oracle, SQL Server
    - cloud_platforms: AWS, Azure, GCP, DigitalOcean, Heroku
    - devops_tools: Docker, Kubernetes, Jenkins, GitLab CI, Terraform, Ansible, GitHub Actions
    - frontend_tools: HTML, CSS, SASS, Webpack, Vite, Tailwind CSS, Bootstrap, Material-UI
    - testing_tools: Jest, Pytest, JUnit, Selenium, Cypress, Mocha, TestNG

    ⚠️ COMMON CATEGORIZATION MISTAKES TO AVOID (ANTI-PATTERNS):
    - ❌ WRONG: Putting "React" in programming_languages → ✅ CORRECT: React belongs in web_frameworks
    - ❌ WRONG: Putting "SQL" or "MySQL" in web_frameworks → ✅ CORRECT: SQL/MySQL belong in databases
    - ❌ WRONG: Putting "JavaScript" in web_frameworks → ✅ CORRECT: JavaScript belongs in programming_languages
    - ❌ WRONG: Putting "HTML/CSS" in programming_languages → ✅ CORRECT: HTML/CSS belong in frontend_tools
    - ❌ WRONG: Putting "Django" in programming_languages → ✅ CORRECT: Django belongs in web_frameworks
    - ❌ WRONG: Putting "Docker" in cloud_platforms → ✅ CORRECT: Docker belongs in devops_tools
    - ❌ WRONG: Putting "Git/GitHub" in devops_tools → ✅ CORRECT: Git/GitHub belong in version_control
    - ❌ WRONG: Categorizing soft skills like "Team Player", "Communication" as technical skills → ✅ CORRECT: Use soft_skills category
    - ❌ WRONG: Changing "3 years experience" to "5 years" → ✅ CORRECT: Use EXACT numbers from job description
    - ❌ WRONG: Adding skills not mentioned in the job description → ✅ CORRECT: Only extract explicitly stated skills

    VALIDATION CHECKLIST (Review before returning):
    ✓ Are all programming languages in programming_languages category?
    ✓ Are all frameworks (React, Django, etc.) in web_frameworks category?
    ✓ Are all databases in databases category?
    ✓ Did I preserve the EXACT experience years from the job description?
    ✓ Did I only include skills explicitly mentioned?

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

    STRICT EXTRACTION RULES:
    - Extract ONLY skills explicitly mentioned - do not infer or add related skills
    - Categorize skills using the examples above as reference
    - For required vs preferred: "must have", "required", "essential" = required; "nice to have", "preferred", "bonus" = preferred
    - For experience: Use EXACT numbers stated ("3+ years" = 3, "5-7 years" = 5, "minimum 2 years" = 2)
    - For seniority_level: Base on experience requirements and job title (0-2 years = junior, 2-5 = mid, 5-10 = senior, 10+ = lead/principal)
    - Use null for missing information - do not guess or assume
    - Validate your categorizations - common mistakes: React in programming_languages (should be web_frameworks), SQL in web_frameworks (should be databases)
    - Return only the JSON, no other text or explanations
    """
        
        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(prompt)
            
            try:
                job_analysis = json.loads(response)

                # 🌟 NEW: Apply validation to job analysis as well
                validated_job_analysis = self._validate_job_analysis(job_analysis)

                # Add role detection and weights
                detected_role = self._detect_role_type_fixed(job_title or "", enhanced_description)
                role_weights = self.role_weights.get(detected_role, self.role_weights["default"])

                # Enhanced result with all information
                enhanced_analysis = {
                    **validated_job_analysis,
                    "detected_role_type": detected_role,
                    "role_specific_weights": role_weights,
                    "enhancement_details": enhancement_info,
                    "enhancement_features": {
                        "role_detection": True,
                        "adaptive_weighting": True,
                        "integrated_enhancement": use_enhancement,
                        "job_validation_applied": True
                    }
                }
                
                logger.info("✅ Job description analyzed successfully with integrated enhancement")
                return enhanced_analysis
                
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                extracted_result = self._extract_json_from_response(response)
                
                # Add enhancement info even to extracted results
                extracted_result["enhancement_details"] = enhancement_info
                return extracted_result
                
        except Exception as e:
            logger.error(f"❌ Error analyzing job description: {str(e)}")
            raise Exception(f"Failed to analyze job description: {str(e)}")


    # 🌟 ADD the missing enhance_job_description method if it doesn't exist
    async def enhance_job_description(self, raw_description: str, job_title: str = None) -> Dict[str, Any]:
        """AI-powered job description enhancement and optimization"""
        
        logger.info("🔧 Enhancing job description with AI optimization")
        
        enhancement_prompt = f"""
    You are an expert HR professional and job description optimizer. Your task is to take a raw job description input and transform it into a clear, structured, and comprehensive job description that will enable accurate candidate matching.

    RAW JOB DESCRIPTION INPUT:
    Title: {job_title or 'Not specified'}
    Description: {raw_description}

    ENHANCEMENT REQUIREMENTS:
    1. Clean up grammar, spelling, and formatting
    2. Extract and organize all requirements clearly
    3. Standardize skill terminology (e.g., "JS" → "JavaScript", "React.js" → "React")
    4. Separate required vs preferred qualifications
    5. PRESERVE EXACT experience level requirements (do not change "3 years" to "5 years")
    6. Only clarify education requirements if they are vague or missing
    7. Remove ambiguous or contradictory statements (except experience years)
    8. Structure the content logically without changing core requirements

    Return ONLY a valid JSON object with this exact structure:
    {{
        "enhanced_title": "Clear, specific job title",
        "enhanced_description": "Complete, well-structured job description text",
        "optimization_notes": "What was improved or standardized",
        "quality_score": score_out_of_100_for_original_description
    }}

    RULES:
    - Use specific, standardized skill names from the tech industry
    - PRESERVE EXACT experience requirements as specified in the original (DO NOT modify years of experience)
    - If original says "3 years" keep it as "3 years", if it says "5+ years" keep it as "5+ years"
    - Only clarify experience requirements if they are ambiguous (e.g., "some experience" → "2-3 years")
    - Don't add requirements that weren't implied in the original
    - If information is missing, use null values
    - Focus on clarity and accuracy while preserving original intent
    - Return only the JSON, no other text
    """
        
        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(enhancement_prompt)
            
            try:
                enhancement_result = json.loads(response)
                logger.info("✅ Job description enhanced successfully")
                
                # Add metadata
                enhancement_result["original_description"] = raw_description
                enhancement_result["original_title"] = job_title
                enhancement_result["enhancement_timestamp"] = self._get_timestamp()
                
                return enhancement_result
                
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                return self._extract_json_from_response(response)
                
        except Exception as e:
            logger.error(f"❌ Error enhancing job description: {str(e)}")
            
            # Fallback: return basic structure with original content
            return {
                "enhanced_title": job_title or "Position",
                "enhanced_description": raw_description,
                "optimization_notes": f"Enhancement failed: {str(e)}",
                "quality_score": 50,
                "error": "Enhancement failed, using fallback analysis"
            }
    
    async def analyze_resume_content(self, resume_text: str, job_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """Improved resume analysis with better JSON structure and more detailed prompts"""
        
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
    You are a senior technical recruiter with 10+ years of experience analyzing software developer resumes. Your task is to extract information with HIGH ACCURACY and return ONLY a properly formatted JSON object.

    ANALYSIS INSTRUCTIONS:
    1. Read the ENTIRE resume carefully before making any assessments
    2. Base proficiency levels on concrete evidence (project complexity, years used, professional context)
    3. Calculate years_experience from actual work dates and project durations
    4. Only include skills that are explicitly mentioned or clearly demonstrated
    5. Be conservative with proficiency ratings - require strong evidence for "advanced" or "expert"

    Resume Content:
    {resume_text}
    {job_context}

    PROFICIENCY LEVEL CRITERIA (evidence-based, NOT just years):

    PRIMARY CRITERIA (Use these first):
    1. Project Complexity & Impact:
       - "expert": Architected systems from scratch, made critical technical decisions, measurable business impact
       - "advanced": Independently built complex features, optimized performance, solved challenging technical problems
       - "intermediate": Built complete features with guidance, contributed to production code regularly
       - "beginner": Worked on simple tasks, learning phase, assisted with basic implementations

    2. Evidence of Mastery:
       - "expert": Mentored others, led technical discussions, open-source contributions, technical writing
       - "advanced": Code reviews, technical presentations, cross-team collaboration, problem-solving leadership
       - "intermediate": Team collaboration, bug fixes, feature contributions, following best practices
       - "beginner": Learning resources, tutorials, personal projects, guided development

    SECONDARY CRITERIA (Use as supporting evidence):
    3. Years of Experience (as reference, not requirement):
       - "expert": Usually 5+ years, BUT can be less with exceptional depth
       - "advanced": Usually 3-5 years, BUT can be 2 years with strong project complexity
       - "intermediate": Usually 1-3 years, BUT can be 6 months with intensive professional use
       - "beginner": Usually 0-1 year, includes recent learners regardless of total career length

    IMPORTANT PROFICIENCY RULES:
    - A 2-year React developer who built complex SPAs and mentored others = "advanced" or "expert"
    - A 5-year developer who only maintains legacy code = "intermediate"
    - Base proficiency on IMPACT and COMPLEXITY, not just duration
    - If resume lacks evidence, default to "intermediate" for professional use, "beginner" for personal projects
    - Look for quantified achievements: "Improved performance by 40%", "Built system serving 1M users"

    CRITICAL: Return ONLY the JSON object below. No explanations, no markdown, no code blocks, just the raw JSON:

    {{
        "candidate_summary": "Brief 2-3 sentence professional summary",
        "contact_info": {{
            "name": "Full name or null",
            "email": "Email address or null", 
            "phone": "Phone number or null",
            "linkedin": "LinkedIn profile or null",
            "location": "City, State/Country or null",
            "portfolio": "Portfolio website or null"
        }},
        "skills_by_category": {{
            "programming_languages": [
                {{"name": "Python", "proficiency": "advanced", "years_experience": 2}},
                {{"name": "JavaScript", "proficiency": "intermediate", "years_experience": 1}}
            ],
            "web_frameworks": [
                {{"name": "Django", "proficiency": "advanced", "years_experience": 2}},
                {{"name": "React", "proficiency": "intermediate", "years_experience": 1}}
            ],
            "databases": [
                {{"name": "MySQL", "proficiency": "intermediate", "years_experience": 1}}
            ],
            "cloud_platforms": [
                {{"name": "AWS", "proficiency": "beginner", "years_experience": 1}}
            ],
            "devops_tools": [
                {{"name": "Docker", "proficiency": "beginner", "years_experience": 1}}
            ],
            "data_tools": [],
            "frontend_tools": [
                {{"name": "HTML", "proficiency": "advanced", "years_experience": 2}},
                {{"name": "CSS", "proficiency": "advanced", "years_experience": 2}}
            ],
            "mobile_development": [],
            "testing_tools": [],
            "version_control": [
                {{"name": "Git", "proficiency": "intermediate", "years_experience": 2}}
            ],
            "project_management": [],
            "other_technical": [],
            "soft_skills": [
                {{"name": "Team collaboration", "evidence": "Worked in Scrum teams"}},
                {{"name": "Problem solving", "evidence": "Resolved complex backend issues"}}
            ]
        }},
        "experience_analysis": {{
            "total_years": 2.5,
            "relevant_years": 2.5,
            "career_progression": "junior_to_mid",
            "industry_experience": ["healthcare", "technology"],
            "role_types": ["individual_contributor"],
            "company_sizes": ["mid_size"],
            "current_level": "mid"
        }},
        "work_history": [
            {{
                "company": "Company Name",
                "title": "Full Stack Developer", 
                "start_date": "2024-08",
                "end_date": "present",
                "duration_months": 6,
                "key_achievements": [
                    "Developed cloud-based automated system for insurance eligibility checks",
                    "Integrated frontend with backend APIs for real-time functionality"
                ],
                "technologies_used": ["Python", "React", "AWS Lambda", "Twilio"],
                "team_size": null,
                "role_type": "individual_contributor"
            }}
        ],
        "education": {{
            "degrees": [
                {{
                    "level": "Bachelor's",
                    "field": "Computer Science", 
                    "institution": "University Name",
                    "graduation_year": "2022",
                    "gpa": null,
                    "relevant_coursework": ["Data Structures", "Algorithms"]
                }}
            ],
            "certifications": []
        }},
        "projects": [
            {{
                "name": "Project Name",
                "description": "Brief description of what it does",
                "technologies": ["Python", "Django", "React"],
                "role": "Full Stack Developer",
                "impact": "Automated insurance eligibility checks"
            }}
        ],
        "achievements": [],
        "resume_quality": {{
            "formatting_score": 75,
            "completeness_score": 80,
            "quantification_score": 60,
            "ats_friendly": true,
            "keyword_optimization": 70,
            "overall_quality": 75,
            "improvement_suggestions": [
                "Add more quantified achievements",
                "Include specific metrics and numbers"
            ]
        }},
        "leadership_indicators": {{
            "has_leadership_experience": false,
            "team_sizes_managed": [],
            "leadership_skills": [],
            "leadership_evidence": []
        }},
        "career_insights": {{
            "specializations": ["Full Stack Development", "Web Applications"],
            "career_trajectory": "ascending",
            "job_stability": "stable",
            "learning_attitude": "continuous_learner",
            "innovation_indicators": ["Built automated systems", "Cloud integration"],
            "remote_work_experience": true
        }}
    }}

    STRICT EXTRACTION GUIDELINES:

    SKILLS EXTRACTION:
    - Only include skills EXPLICITLY mentioned in the resume
    - For years_experience: Count from first professional use to present (be precise with math)
    - For proficiency: Require EVIDENCE - don't guess or assume
    - Examples of evidence: "Led React development", "Optimized MySQL queries", "Architected microservices"
    - If no evidence for proficiency level, default to "intermediate" for professional use

    EXPERIENCE CALCULATION:
    - Calculate total_years from actual employment start/end dates
    - Calculate relevant_years as subset of total experience in technical roles
    - For current_level: "junior" (0-2 years), "mid" (2-5 years), "senior" (5-10 years), "lead" (10+ years)

    ACCURACY REQUIREMENTS:
    - DO NOT invent information not present in the resume
    - DO NOT extrapolate beyond what is clearly stated
    - USE EXACT DATES when calculating durations
    - VALIDATE your skill categorizations (e.g., React goes in web_frameworks, not programming_languages)

    QUALITY SCORING:
    - Base formatting_score on actual resume structure and organization
    - Base completeness_score on presence of contact info, experience, education, skills
    - Be honest about resume quality - don't inflate scores

    Return ONLY the JSON object. No other text whatsoever."""

        try:
            if not self.model:
                raise Exception("Google Gemini not initialized. Check your API key.")
            
            response = await self._call_gemini(prompt)
            
            # Clean the response to extract only JSON
            response_clean = response.strip()
            
            # Remove any markdown code blocks if present
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            response_clean = response_clean.strip()
            
            try:
                resume_analysis = json.loads(response_clean)

                # 🌟 NEW: Accuracy validation and correction
                validated_analysis = await self._validate_and_correct_analysis(resume_analysis, resume_text)

                logger.info("✅ Enhanced resume analyzed and validated successfully")
                return validated_analysis
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}")
                logger.warning(f"Response content: {response_clean[:500]}...")
                # Try to extract JSON from response
                return self._extract_json_from_response(response_clean)
                    
        except Exception as e:
            logger.error(f"❌ Error analyzing resume: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API asynchronously with enhanced configuration for better accuracy"""
        if not self.model:
            raise Exception("Google Gemini model not initialized. Check your API key in .env file.")

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=8000,
                        temperature=0.15,  # Optimized for structured extraction accuracy
                        candidate_count=1,
                        top_p=0.85,       # Balanced for consistent structured outputs
                        top_k=40          # Reduced for more deterministic responses
                    )
                )
            )

            # Check if response has text and is valid
            if not hasattr(response, 'text') or not response.text:
                raise Exception("Empty or invalid response from Gemini API")

            return response.text

        except Exception as e:
            logger.error(f"❌ Google Gemini API error: {str(e)}")
            if "API_KEY" in str(e).upper():
                raise Exception("Invalid Google API key. Please check your GOOGLE_API_KEY in .env file.")
            if "not found" in str(e).lower():
                raise Exception(f"Model not found. Using 'gemini-pro' model. Error: {str(e)}")
            raise Exception(f"Google Gemini API error: {str(e)}")
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from AI response that might have extra text"""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                raise Exception("No valid JSON found in AI response")
        except Exception as e:
            logger.error(f"Failed to extract JSON from response: {str(e)}")
            # Return a proper fallback structure that matches expected resume analysis format
            return {
                "contact_info": {
                    "name": "Unknown",
                    "email": None,
                    "phone": None,
                    "linkedin": None,
                    "location": None
                },
                "skills_by_category": {
                    "programming_languages": [],
                    "web_frameworks": [],
                    "databases": [],
                    "cloud_platforms": [],
                    "devops_tools": [],
                    "frontend_tools": [],
                    "testing_tools": [],
                    "version_control": [],
                    "soft_skills": []
                },
                "work_history": [],
                "education": {
                    "degrees": [],
                    "certifications": []
                },
                "projects": [],
                "experience_analysis": {
                    "total_years": 0,
                    "relevant_years": 0,
                    "current_level": "unknown"
                },
                "candidate_summary": f"Failed to parse AI response. Raw response: {response[:200]}...",
                "resume_quality": {
                    "overall_quality": 30,
                    "formatting_score": 30,
                    "completeness_score": 30
                },
                "leadership_indicators": {
                    "has_leadership_experience": False,
                    "team_sizes_managed": [],
                    "leadership_skills": []
                },
                "career_insights": {
                    "specializations": [],
                    "career_trajectory": "unknown",
                    "job_stability": "unknown"
                },
                "parsing_error": True,
                "error_message": str(e)
            }
    
    async def _validate_and_correct_analysis(self, analysis: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """🌟 NEW: Validate and correct analysis for better accuracy"""

        # Quick validation checks
        corrected_analysis = analysis.copy()

        # 1. Validate skill categorizations
        skills_by_category = corrected_analysis.get("skills_by_category", {})

        # Common categorization fixes
        corrections_made = []

        # Check for misplaced skills
        programming_langs = ["python", "javascript", "java", "c#", "go", "rust", "php", "ruby", "swift", "kotlin"]
        web_frameworks = ["react", "angular", "vue", "django", "flask", "express", "spring", "laravel"]
        databases = ["mysql", "postgresql", "mongodb", "redis", "sqlite", "dynamodb", "oracle"]

        # Fix common categorization errors - create a new skills structure
        corrected_skills_by_category = {}
        skills_to_move = []

        # First pass: identify skills that need to be moved
        for category, skills in skills_by_category.items():
            corrected_skills_by_category[category] = []
            if isinstance(skills, list):
                for skill_item in skills:
                    if isinstance(skill_item, dict):
                        skill_name = (skill_item.get("name") or "").lower()
                        moved = False

                        # Check if skill is in wrong category
                        if category == "programming_languages" and any(fw in skill_name for fw in web_frameworks):
                            skills_to_move.append((skill_item, "web_frameworks"))
                            corrections_made.append(f"Moved {skill_item.get('name')} from programming_languages to web_frameworks")
                            moved = True

                        elif category == "web_frameworks" and any(pl in skill_name for pl in programming_langs):
                            skills_to_move.append((skill_item, "programming_languages"))
                            corrections_made.append(f"Moved {skill_item.get('name')} from web_frameworks to programming_languages")
                            moved = True

                        if not moved:
                            corrected_skills_by_category[category].append(skill_item)
                    else:
                        corrected_skills_by_category[category].append(skill_item)

        # Second pass: add moved skills to their correct categories
        for skill_item, target_category in skills_to_move:
            if target_category not in corrected_skills_by_category:
                corrected_skills_by_category[target_category] = []
            corrected_skills_by_category[target_category].append(skill_item)

        skills_by_category = corrected_skills_by_category

        # 2. Validate experience calculations
        experience_analysis = corrected_analysis.get("experience_analysis", {})
        work_history = corrected_analysis.get("work_history", [])

        if work_history:
            # Recalculate total years more accurately
            total_months = 0
            for job in work_history:
                duration = job.get("duration_months", 0)
                if isinstance(duration, (int, float)) and duration > 0:
                    total_months += duration

            calculated_years = round(total_months / 12, 1)
            original_years = experience_analysis.get("total_years", 0)

            # If calculated differs significantly from original, use calculated
            if abs(calculated_years - original_years) > 0.5:
                experience_analysis["total_years"] = calculated_years
                corrections_made.append(f"Corrected total_years from {original_years} to {calculated_years}")

        # 3. Validate resume quality scores (ensure they're reasonable)
        resume_quality = corrected_analysis.get("resume_quality", {})
        contact_info = corrected_analysis.get("contact_info", {})

        # Check if scores are too high given the actual content
        has_contact = bool(contact_info.get("email") or contact_info.get("phone"))
        has_experience = bool(work_history)
        has_skills = bool([s for s in skills_by_category.values() if s])

        completeness_factors = sum([has_contact, has_experience, has_skills])
        reasonable_completeness = min(completeness_factors * 30, 90)

        current_completeness = resume_quality.get("completeness_score", 50)
        if current_completeness > reasonable_completeness + 10:
            resume_quality["completeness_score"] = reasonable_completeness
            corrections_made.append(f"Adjusted completeness_score from {current_completeness} to {reasonable_completeness}")

        # Update the corrected analysis
        corrected_analysis["skills_by_category"] = skills_by_category
        corrected_analysis["experience_analysis"] = experience_analysis
        corrected_analysis["resume_quality"] = resume_quality

        # Add validation metadata
        corrected_analysis["_validation_applied"] = True
        corrected_analysis["_corrections_made"] = corrections_made

        if corrections_made:
            logger.info(f"🔧 Applied {len(corrections_made)} accuracy corrections: {corrections_made}")

        return corrected_analysis

    def _validate_job_analysis(self, job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """🌟 NEW: Validate job analysis for accuracy"""

        corrected_analysis = job_analysis.copy()
        corrections_made = []

        # 1. Validate skill categorizations in job requirements
        required_skills = corrected_analysis.get("required_skills", {})
        preferred_skills = corrected_analysis.get("preferred_skills", {})

        # Common skill categorization fixes
        programming_langs = ["python", "javascript", "java", "c#", "go", "rust", "php", "ruby", "swift", "kotlin"]
        web_frameworks = ["react", "angular", "vue", "django", "flask", "express", "spring", "laravel", "fastapi"]
        databases = ["mysql", "postgresql", "mongodb", "redis", "sqlite", "dynamodb", "oracle", "sql"]

        for skill_set_name, skill_set in [("required_skills", required_skills), ("preferred_skills", preferred_skills)]:
            for category, skills in skill_set.items():
                if isinstance(skills, list):
                    corrected_skills = []
                    for skill in skills:
                        skill_lower = str(skill).lower()
                        moved = False

                        # Check if skill is in wrong category
                        if category == "programming_languages" and any(fw in skill_lower for fw in web_frameworks):
                            # Move to web_frameworks
                            if "web_frameworks" not in skill_set:
                                skill_set["web_frameworks"] = []
                            skill_set["web_frameworks"].append(skill)
                            corrections_made.append(f"Moved '{skill}' from {category} to web_frameworks in {skill_set_name}")
                            moved = True

                        elif category == "web_frameworks" and any(pl in skill_lower for pl in programming_langs):
                            # Move to programming_languages
                            if "programming_languages" not in skill_set:
                                skill_set["programming_languages"] = []
                            skill_set["programming_languages"].append(skill)
                            corrections_made.append(f"Moved '{skill}' from {category} to programming_languages in {skill_set_name}")
                            moved = True

                        elif category == "programming_languages" and any(db in skill_lower for db in databases):
                            # Move to databases
                            if "databases" not in skill_set:
                                skill_set["databases"] = []
                            skill_set["databases"].append(skill)
                            corrections_made.append(f"Moved '{skill}' from {category} to databases in {skill_set_name}")
                            moved = True

                        if not moved:
                            corrected_skills.append(skill)

                    skill_set[category] = corrected_skills

        # 2. Validate experience requirements logic
        min_exp = corrected_analysis.get("minimum_experience")
        pref_exp = corrected_analysis.get("preferred_experience")
        seniority = corrected_analysis.get("seniority_level")

        # Check if experience levels make sense
        if min_exp and pref_exp and min_exp > pref_exp:
            # Swap them
            corrected_analysis["minimum_experience"] = pref_exp
            corrected_analysis["preferred_experience"] = min_exp
            corrections_made.append(f"Swapped minimum_experience ({min_exp}) and preferred_experience ({pref_exp})")

        # Check if seniority matches experience requirements
        if min_exp and seniority:
            expected_seniority = "junior" if min_exp <= 2 else "mid" if min_exp <= 5 else "senior" if min_exp <= 10 else "lead"
            if seniority != expected_seniority:
                corrected_analysis["seniority_level"] = expected_seniority
                corrections_made.append(f"Corrected seniority_level from '{seniority}' to '{expected_seniority}' based on {min_exp} years requirement")

        # Add validation metadata
        corrected_analysis["_job_validation_applied"] = True
        corrected_analysis["_job_corrections_made"] = corrections_made

        if corrections_made:
            logger.info(f"🔧 Applied {len(corrections_made)} job analysis corrections: {corrections_made}")

        return corrected_analysis

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        return datetime.now().isoformat()
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Google Gemini with enhanced diagnostics"""
        try:
            if not self.model:
                return {
                    "status": "error",
                    "message": "Google API key not configured. Add GOOGLE_API_KEY to .env file.",
                    "provider": "google_gemini"
                }
            
            test_response = await self._call_gemini('''
Test the advanced resume analyzer with enterprise features.
Return exactly: {"test": "success", "message": "Advanced AI analyzer is working", "features": ["skill_intelligence", "role_weighting", "experience_quality"]}
            ''')
            
            return {
                "status": "connected",
                "provider": "google_gemini",
                "model": "gemini-2.0-flash-exp",
                "enterprise_features": [
                    "skill_intelligence_with_synonyms",
                    "role_specific_weighting",
                    "experience_quality_analysis",
                    "skill_relationship_bonuses",
                    "leadership_detection",
                    "impact_quantification"
                ],
                "test_response": test_response[:200] + "..." if len(test_response) > 200 else test_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "provider": "google_gemini"
            }