"""
Internship recommendation chatbot backend.
"""
import pandas as pd
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from models.internship import Internship


class InternshipBot:
    """Main chatbot class for internship recommendations."""
    
    def __init__(self, csv_path: str = "data/internships.csv"):
        self.csv_path = csv_path
        self.df = None
        self.logger = logging.getLogger('chatbot')
        self.load_data()
        
        # User profile for recommendations
        self.user_profile = {
            'skills': [],
            'education_level': '',
            'preferred_location': '',
            'preferred_mode': '',
            'stipend_expectation': '',
            'interests': []
        }
    
    def load_data(self):
        """Load internship data from CSV."""
        try:
            if Path(self.csv_path).exists():
                self.df = pd.read_csv(self.csv_path)
                self.logger.info(f"Loaded {len(self.df)} internships from {self.csv_path}")
            else:
                self.logger.warning(f"CSV file {self.csv_path} not found. Please run pipeline.py first.")
                self.df = pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def reload_data(self):
        """Reload data from CSV (useful after new scraping)."""
        self.load_data()
    
    def filter_internships(self, 
                          location: str = None,
                          mode: str = None,
                          target_audience: str = None,
                          skills: List[str] = None,
                          organization: str = None,
                          min_stipend: str = None,
                          tags: List[str] = None,
                          limit: int = 10) -> pd.DataFrame:
        """
        Filter internships based on criteria.
        
        Args:
            location: Filter by location
            mode: Filter by work mode (Remote/Onsite/Hybrid)
            target_audience: Filter by target audience (UG/PG/PhD)
            skills: Filter by required skills
            organization: Filter by organization
            min_stipend: Filter by minimum stipend
            tags: Filter by tags
            limit: Maximum number of results
        
        Returns:
            Filtered DataFrame
        """
        if self.df.empty:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        # Location filter
        if location:
            location_lower = location.lower()
            filtered_df = filtered_df[
                filtered_df['location'].str.lower().str.contains(location_lower, na=False) |
                filtered_df['country'].str.lower().str.contains(location_lower, na=False)
            ]
        
        # Mode filter
        if mode:
            mode_lower = mode.lower()
            filtered_df = filtered_df[
                filtered_df['mode'].str.lower().str.contains(mode_lower, na=False)
            ]
        
        # Target audience filter
        if target_audience:
            audience_lower = target_audience.lower()
            filtered_df = filtered_df[
                filtered_df['target_audience'].str.lower().str.contains(audience_lower, na=False)
            ]
        
        # Skills filter
        if skills:
            skills_lower = [skill.lower() for skill in skills]
            skill_mask = filtered_df['skills_required'].str.lower().str.contains('|'.join(skills_lower), na=False)
            filtered_df = filtered_df[skill_mask]
        
        # Organization filter
        if organization:
            org_lower = organization.lower()
            filtered_df = filtered_df[
                filtered_df['organization'].str.lower().str.contains(org_lower, na=False)
            ]
        
        # Stipend filter
        if min_stipend:
            # Extract numeric value from stipend
            def extract_stipend_value(stipend_str):
                if pd.isna(stipend_str) or not stipend_str:
                    return 0
                # Extract numbers from stipend string
                numbers = re.findall(r'\d+', str(stipend_str))
                return int(numbers[0]) if numbers else 0
            
            filtered_df['stipend_numeric'] = filtered_df['stipend'].apply(extract_stipend_value)
            min_stipend_val = extract_stipend_value(min_stipend)
            filtered_df = filtered_df[filtered_df['stipend_numeric'] >= min_stipend_val]
            filtered_df = filtered_df.drop('stipend_numeric', axis=1)
        
        # Tags filter
        if tags:
            tags_lower = [tag.lower() for tag in tags]
            tag_mask = filtered_df['tags'].str.lower().str.contains('|'.join(tags_lower), na=False)
            filtered_df = filtered_df[tag_mask]
        
        return filtered_df.head(limit)
    
    def search_internships(self, query: str, limit: int = 10) -> pd.DataFrame:
        """
        Search internships using natural language query.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
        
        Returns:
            Filtered DataFrame
        """
        if self.df.empty:
            return pd.DataFrame()
        
        query_lower = query.lower()
        
        # Extract search criteria from query
        location = None
        mode = None
        skills = []
        tags = []
        organization = None
        
        # Location extraction
        location_keywords = ['bangalore', 'mumbai', 'delhi', 'hyderabad', 'chennai', 'pune', 'kolkata', 'gurgaon', 'noida', 'india']
        for loc in location_keywords:
            if loc in query_lower:
                location = loc.title()
                break
        
        # Mode extraction
        if 'remote' in query_lower:
            mode = 'Remote'
        elif 'onsite' in query_lower or 'office' in query_lower:
            mode = 'Onsite'
        elif 'hybrid' in query_lower:
            mode = 'Hybrid'
        
        # Skills extraction
        skill_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 
                         'machine learning', 'ai', 'data science', 'web development', 'mobile development', 'android', 'ios']
        for skill in skill_keywords:
            if skill in query_lower:
                skills.append(skill)
        
        # Organization extraction
        org_keywords = ['google', 'microsoft', 'amazon', 'facebook', 'apple', 'netflix', 'uber', 'airbnb', 'tesla']
        for org in org_keywords:
            if org in query_lower:
                organization = org.title()
                break
        
        # Tag extraction
        tag_keywords = ['ai/ml', 'web development', 'data science', 'mobile', 'blockchain', 'cybersecurity', 'devops']
        for tag in tag_keywords:
            if tag in query_lower:
                tags.append(tag)
        
        # Apply filters
        return self.filter_internships(
            location=location,
            mode=mode,
            skills=skills if skills else None,
            organization=organization,
            tags=tags if tags else None,
            limit=limit
        )
    
    def recommend_internships(self, user_profile: Dict[str, Any] = None, limit: int = 10) -> pd.DataFrame:
        """
        Recommend internships based on user profile.
        
        Args:
            user_profile: User profile dictionary
            limit: Maximum number of results
        
        Returns:
            Recommended internships DataFrame
        """
        if user_profile:
            self.user_profile.update(user_profile)
        
        if self.df.empty:
            return pd.DataFrame()
        
        # Calculate relevance scores
        recommendations = self.df.copy()
        recommendations['relevance_score'] = 0
        
        # Score based on skills match
        if self.user_profile['skills']:
            for skill in self.user_profile['skills']:
                skill_mask = recommendations['skills_required'].str.lower().str.contains(skill.lower(), na=False)
                recommendations.loc[skill_mask, 'relevance_score'] += 2
        
        # Score based on location preference
        if self.user_profile['preferred_location']:
            location_mask = recommendations['location'].str.lower().str.contains(
                self.user_profile['preferred_location'].lower(), na=False
            )
            recommendations.loc[location_mask, 'relevance_score'] += 1
        
        # Score based on mode preference
        if self.user_profile['preferred_mode']:
            mode_mask = recommendations['mode'].str.lower().str.contains(
                self.user_profile['preferred_mode'].lower(), na=False
            )
            recommendations.loc[mode_mask, 'relevance_score'] += 1
        
        # Score based on education level
        if self.user_profile['education_level']:
            education_mask = recommendations['target_audience'].str.lower().str.contains(
                self.user_profile['education_level'].lower(), na=False
            )
            recommendations.loc[education_mask, 'relevance_score'] += 1
        
        # Sort by relevance score and return top results
        recommendations = recommendations.sort_values('relevance_score', ascending=False)
        return recommendations.head(limit)
    
    def ask_clarifying_questions(self, query: str) -> List[str]:
        """
        Generate clarifying questions based on vague query.
        
        Args:
            query: User's initial query
        
        Returns:
            List of clarifying questions
        """
        questions = []
        query_lower = query.lower()
        
        # Check if location is mentioned
        location_keywords = ['bangalore', 'mumbai', 'delhi', 'hyderabad', 'chennai', 'pune', 'kolkata', 'gurgaon', 'noida', 'india', 'remote']
        if not any(loc in query_lower for loc in location_keywords):
            questions.append("What location are you interested in? (e.g., Bangalore, Mumbai, Remote)")
        
        # Check if work mode is mentioned
        mode_keywords = ['remote', 'onsite', 'office', 'hybrid']
        if not any(mode in query_lower for mode in mode_keywords):
            questions.append("What work mode do you prefer? (Remote, Onsite, or Hybrid)")
        
        # Check if skills are mentioned
        skill_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'machine learning', 'ai', 'data science']
        if not any(skill in query_lower for skill in skill_keywords):
            questions.append("What skills or technologies are you interested in? (e.g., Python, React, AI/ML)")
        
        # Check if stipend is mentioned
        stipend_keywords = ['stipend', 'salary', 'paid', 'unpaid', 'compensation']
        if not any(stipend in query_lower for stipend in stipend_keywords):
            questions.append("Are you looking for paid internships? What's your stipend expectation?")
        
        # Check if duration is mentioned
        duration_keywords = ['duration', 'months', 'weeks', 'summer', 'winter', 'semester']
        if not any(duration in query_lower for duration in duration_keywords):
            questions.append("What duration are you looking for? (e.g., 2 months, 6 months, summer)")
        
        return questions
    
    def format_internship_results(self, df: pd.DataFrame) -> str:
        """
        Format internship results for display.
        
        Args:
            df: DataFrame containing internships
        
        Returns:
            Formatted string
        """
        if df.empty:
            return "No internships found matching your criteria."
        
        result = f"Found {len(df)} internship(s):\n\n"
        
        for idx, row in df.iterrows():
            result += f"**{idx + 1}. {row['title']}**\n"
            result += f"   Organization: {row['organization']}\n"
            result += f"   Location: {row['location']}, {row['country']}\n"
            result += f"   Mode: {row['mode']}\n"
            result += f"   Target Audience: {row['target_audience']}\n"
            if row['stipend']:
                result += f"   Stipend: {row['stipend']}\n"
            if row['skills_required']:
                result += f"   Skills: {row['skills_required']}\n"
            if row['application_link']:
                result += f"   Apply: {row['application_link']}\n"
            result += "\n"
        
        return result
    
    def process_query(self, query: str) -> str:
        """
        Process user query and return response.
        
        Args:
            query: User's query
        
        Returns:
            Bot's response
        """
        query_lower = query.lower()
        
        # Check if query is too vague
        if len(query.split()) < 3:
            questions = self.ask_clarifying_questions(query)
            if questions:
                return f"Your query seems a bit vague. Could you please clarify:\n\n" + "\n".join(f"• {q}" for q in questions)
        
        # Search for internships
        results = self.search_internships(query, limit=10)
        
        if results.empty:
            return "No internships found matching your criteria. Try adjusting your search terms or be more specific about what you're looking for."
        
        return self.format_internship_results(results)
