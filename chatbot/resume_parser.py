"""
Resume parsing functionality for profile-based recommendations.
"""
import PyPDF2
import re
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path


class ResumeParser:
    """Parse resume PDF and extract profile information."""
    
    def __init__(self):
        self.logger = logging.getLogger('resume_parser')
        
        # Common skills keywords
        self.technical_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node.js',
            'django', 'flask', 'spring', 'express', 'mongodb', 'postgresql', 'mysql', 'sql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github', 'gitlab',
            'machine learning', 'ml', 'artificial intelligence', 'ai', 'data science',
            'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'opencv', 'nlp', 'natural language processing', 'computer vision', 'blockchain',
            'ethereum', 'solidity', 'web3', 'mobile development', 'ios', 'android',
            'flutter', 'react native', 'swift', 'kotlin', 'cybersecurity', 'penetration testing',
            'devops', 'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'unix',
            'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'scala', 'r',
            'tableau', 'power bi', 'excel', 'nosql', 'redis', 'elasticsearch',
            'kafka', 'rabbitmq', 'microservices', 'api', 'rest', 'graphql',
            'frontend', 'backend', 'full stack', 'ui/ux', 'design', 'figma',
            'adobe', 'photoshop', 'illustrator', 'sketch', 'agile', 'scrum'
        ]
        
        # Soft skills keywords
        self.soft_skills = [
            'leadership', 'teamwork', 'communication', 'problem solving', 'analytical',
            'creative', 'innovative', 'adaptable', 'time management', 'project management',
            'mentoring', 'collaboration', 'presentation', 'negotiation', 'critical thinking'
        ]
        
        # Education level keywords
        self.education_keywords = {
            'phd': ['phd', 'doctorate', 'doctoral', 'ph.d'],
            'masters': ['masters', 'mba', 'mtech', 'ms', 'postgraduate', 'm.sc', 'm.a', 'm.com'],
            'bachelors': ['bachelor', 'btech', 'bca', 'bsc', 'undergraduate', 'ug', 'b.e', 'b.a', 'b.com']
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical and soft skills from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = []
        
        # Extract technical skills
        for skill in self.technical_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_education_level(self, text: str) -> str:
        """
        Extract education level from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            Education level (UG/PG/PhD)
        """
        text_lower = text.lower()
        
        # Check for PhD
        for keyword in self.education_keywords['phd']:
            if keyword in text_lower:
                return 'PhD'
        
        # Check for Masters
        for keyword in self.education_keywords['masters']:
            if keyword in text_lower:
                return 'PG'
        
        # Check for Bachelors
        for keyword in self.education_keywords['bachelors']:
            if keyword in text_lower:
                return 'UG'
        
        return 'Unknown'
    
    def extract_experience(self, text: str) -> Dict[str, Any]:
        """
        Extract work experience information.
        
        Args:
            text: Resume text
        
        Returns:
            Experience information dictionary
        """
        experience = {
            'years_of_experience': 0,
            'internships': 0,
            'projects': 0,
            'companies': []
        }
        
        text_lower = text.lower()
        
        # Extract years of experience
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    experience['years_of_experience'] = max(experience['years_of_experience'], int(matches[0]))
                except ValueError:
                    continue
        
        # Count internships
        internship_keywords = ['intern', 'internship', 'trainee', 'co-op']
        for keyword in internship_keywords:
            experience['internships'] += len(re.findall(keyword, text_lower))
        
        # Count projects
        project_keywords = ['project', 'portfolio', 'github', 'repository']
        for keyword in project_keywords:
            experience['projects'] += len(re.findall(keyword, text_lower))
        
        # Extract company names (simple approach)
        company_patterns = [
            r'worked\s+at\s+([a-zA-Z\s&]+)',
            r'company\s*:\s*([a-zA-Z\s&]+)',
            r'employer\s*:\s*([a-zA-Z\s&]+)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text_lower)
            experience['companies'].extend([match.strip().title() for match in matches])
        
        experience['companies'] = list(set(experience['companies']))  # Remove duplicates
        
        return experience
    
    def extract_interests(self, text: str) -> List[str]:
        """
        Extract interests and domains from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            List of interests
        """
        interests = []
        text_lower = text.lower()
        
        # Domain keywords
        domain_keywords = {
            'AI/ML': ['artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'ai', 'ml'],
            'Web Development': ['web development', 'frontend', 'backend', 'full stack', 'web applications'],
            'Data Science': ['data science', 'data analysis', 'data visualization', 'statistics', 'analytics'],
            'Mobile Development': ['mobile development', 'ios', 'android', 'mobile apps', 'react native', 'flutter'],
            'Blockchain': ['blockchain', 'cryptocurrency', 'ethereum', 'solidity', 'web3', 'defi'],
            'Cybersecurity': ['cybersecurity', 'security', 'penetration testing', 'ethical hacking'],
            'DevOps': ['devops', 'deployment', 'ci/cd', 'infrastructure', 'cloud'],
            'Game Development': ['game development', 'unity', 'unreal engine', 'gaming'],
            'UI/UX': ['ui/ux', 'user interface', 'user experience', 'design', 'figma', 'sketch']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                interests.append(domain)
        
        return interests
    
    def parse_resume(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse resume and extract complete profile.
        
        Args:
            pdf_path: Path to resume PDF
        
        Returns:
            Complete user profile dictionary
        """
        if not Path(pdf_path).exists():
            self.logger.error(f"Resume file {pdf_path} not found")
            return {}
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            self.logger.error(f"Could not extract text from {pdf_path}")
            return {}
        
        # Extract profile information
        profile = {
            'skills': self.extract_skills(text),
            'education_level': self.extract_education_level(text),
            'experience': self.extract_experience(text),
            'interests': self.extract_interests(text),
            'preferred_location': '',  # Will be filled by user
            'preferred_mode': '',  # Will be filled by user
            'stipend_expectation': ''  # Will be filled by user
        }
        
        self.logger.info(f"Parsed resume: {len(profile['skills'])} skills, {profile['education_level']} education level")
        
        return profile
    
    def parse_text_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse resume from text (for testing or alternative input methods).
        
        Args:
            text: Resume text
        
        Returns:
            Complete user profile dictionary
        """
        if not text:
            return {}
        
        # Extract profile information
        profile = {
            'skills': self.extract_skills(text),
            'education_level': self.extract_education_level(text),
            'experience': self.extract_experience(text),
            'interests': self.extract_interests(text),
            'preferred_location': '',
            'preferred_mode': '',
            'stipend_expectation': ''
        }
        
        return profile
