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
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Advanced AI Analyzer initialized with enterprise features")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Gemini: {e}")
        else:
            logger.warning("⚠️ No Google API key found - check your .env file")
    
    def _detect_role_type_fixed(self, job_title: str, job_description: str, required_skills: dict = None) -> str:
        """
        🎯 FIXED: Role detection that properly identifies Full Stack Developers
        
        This version addresses the issue where Full Stack developers were being 
        misclassified as frontend developers.
        """
        
        if not job_title:
            job_title = ""
        
        combined_text = f"{job_title} {job_description}".lower()
        logger.info(f"🔍 Analyzing role for: '{job_title}' (text length: {len(combined_text)})")
        
        # Initialize role scores
        role_scores = {}
        
        # 🌟 PRIORITY 1: Check for explicit Full Stack indicators
        fullstack_patterns = [
            r"full\s*[-\s]*stack",
            r"fullstack",
            r"end[-\s]*to[-\s]*end",
            r"frontend.*backend|backend.*frontend",
            r"front[-\s]*end.*back[-\s]*end|back[-\s]*end.*front[-\s]*end",
            r"ui.*api|api.*ui",
            r"client.*server|server.*client",
            r"both.*frontend.*backend|both.*backend.*frontend"
        ]
        
        fullstack_score = 0
        fullstack_matches = []
        
        for pattern in fullstack_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                fullstack_score += len(matches)
                fullstack_matches.extend(matches)
        
        # 🌟 PRIORITY 2: Technology stack analysis
        frontend_techs = ["react", "angular", "vue", "javascript", "typescript", "css", "html"]
        backend_techs = ["python", "django", "java", "spring", "api", "rest", "flask", "fastapi"]
        devops_techs = ["docker", "kubernetes", "jenkins", "aws", "azure", "gcp", "terraform", "ansible"]
        
        # Count technology mentions
        frontend_count = sum(1 for tech in frontend_techs if tech in combined_text)
        backend_count = sum(1 for tech in backend_techs if tech in combined_text)
        devops_count = sum(1 for tech in devops_techs if tech in combined_text)
        
        logger.info(f"🔢 Tech counts - Frontend: {frontend_count}, Backend: {backend_count}, DevOps: {devops_count}")
        logger.info(f"🔢 FullStack score: {fullstack_score}, Matches: {fullstack_matches}")
        
        # 🎯 DECISION LOGIC
        
        # If explicit Full Stack indicators found
        if fullstack_score >= 1:
            # Check if they have both frontend and backend skills
            if frontend_count >= 1 and backend_count >= 2:
                logger.info(f"🏆 FULLSTACK: Explicit indicators ({fullstack_score}) + Both stacks (FE:{frontend_count}, BE:{backend_count})")
                return "fullstack_developer"
            elif backend_count >= 2:
                logger.info(f"🏆 FULLSTACK→BACKEND: Has fullstack title but stronger backend focus")
                return "backend_developer"
            else:
                logger.info(f"🏆 FULLSTACK: Explicit indicators found, defaulting to fullstack")
                return "fullstack_developer"
        
        # If no explicit fullstack but has both frontend and backend
        if frontend_count >= 2 and backend_count >= 2:
            logger.info(f"🏆 FULLSTACK: Strong in both stacks (FE:{frontend_count}, BE:{backend_count})")
            return "fullstack_developer"
        
        # Check for role-specific patterns
        role_patterns = {
            "backend_developer": [
                r"backend|back[-\s]*end",
                r"api\s+development",
                r"server[-\s]*side",
                r"database.*design",
                r"microservices",
                r"rest.*api|restful",
            ],
            "frontend_developer": [
                r"frontend|front[-\s]*end",
                r"ui/ux",
                r"user\s+interface",
                r"responsive\s+design",
                r"single\s+page\s+application",
                r"component.*development"
            ],
            "devops_engineer": [
                r"devops|dev\s+ops",
                r"infrastructure",
                r"deployment",
                r"ci/cd|continuous\s+integration",
                r"containerization",
                r"orchestration",
                r"infrastructure.*code"
            ]
        }
        
        # Calculate pattern-based scores
        for role, patterns in role_patterns.items():
            pattern_score = sum(1 for pattern in patterns if re.search(pattern, combined_text, re.IGNORECASE))
            role_scores[role] = pattern_score
        
        # Add technology-based bonuses
        role_scores["frontend_developer"] += frontend_count
        role_scores["backend_developer"] += backend_count
        role_scores["devops_engineer"] += devops_count
        
        # 🚫 DEVOPS PENALTY: Don't over-classify as DevOps
        # Reduce DevOps score if person has strong programming background
        if backend_count >= 2 or frontend_count >= 2:
            role_scores["devops_engineer"] = max(0, role_scores["devops_engineer"] - 2)
            logger.info(f"📉 DevOps penalty applied due to strong programming background")
        
        # Find the best role
        if role_scores:
            sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
            best_role, best_score = sorted_roles[0]
            
            logger.info(f"🎯 Final scores: {dict(sorted_roles)}")
            
            if best_score >= 2:
                logger.info(f"🏆 Selected: {best_role} (score: {best_score})")
                return best_role
        
        # 🔄 FALLBACK LOGIC
        # If primarily backend technologies, default to backend
        if backend_count > frontend_count and backend_count >= 2:
            logger.info(f"🏆 FALLBACK→BACKEND: Backend tech dominance ({backend_count} vs {frontend_count})")
            return "backend_developer"
        
        # If primarily frontend technologies, default to frontend
        if frontend_count > backend_count and frontend_count >= 2:
            logger.info(f"🏆 FALLBACK→FRONTEND: Frontend tech dominance ({frontend_count} vs {backend_count})")
            return "frontend_developer"
        
        # Ultimate fallback
        logger.info(f"🏆 FALLBACK→DEFAULT: No clear winner")
        return "backend_developer"  # Safe default for most developer positions


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
    Analyze this job description and extract detailed information. Return ONLY a valid JSON object:

    Job Title: {job_title or 'Not specified'}
    Job Description:
    {enhanced_description}

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
                
                # Add role detection and weights
                detected_role = self._detect_role_type_fixed(job_title or "", enhanced_description)
                role_weights = self.role_weights.get(detected_role, self.role_weights["default"])
                
                # Enhanced result with all information
                enhanced_analysis = {
                    **job_analysis,
                    "detected_role_type": detected_role,
                    "role_specific_weights": role_weights,
                    "enhancement_details": enhancement_info,
                    "enhancement_features": {
                        "role_detection": True,
                        "adaptive_weighting": True,
                        "integrated_enhancement": use_enhancement
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
    5. Clarify experience levels and education requirements
    6. Remove ambiguous or contradictory statements
    7. Add industry-standard requirements if missing obvious ones
    8. Structure the content logically

    Return ONLY a valid JSON object with this exact structure:
    {{
        "enhanced_title": "Clear, specific job title",
        "enhanced_description": "Complete, well-structured job description text",
        "optimization_notes": "What was improved or standardized",
        "quality_score": score_out_of_100_for_original_description
    }}

    RULES:
    - Use specific, standardized skill names from the tech industry
    - Be realistic about experience requirements
    - Don't add requirements that weren't implied in the original
    - If information is missing, use null values
    - Focus on clarity and accuracy
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
        """Keep original method for compatibility"""
        
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
                logger.info("✅ Enhanced resume analyzed successfully")
                return resume_analysis
            except json.JSONDecodeError:
                logger.warning("Response wasn't valid JSON, attempting to extract")
                return self._extract_json_from_response(response)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing resume: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
    
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
                        max_output_tokens=8000,
                        temperature=0.1,
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
            return {
                "error": "Failed to parse enhanced AI response", 
                "raw_response": response[:300] + "..." if len(response) > 300 else response,
                "message": "The AI returned invalid JSON format"
            }
    
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
                "model": "gemini-1.5-flash",
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