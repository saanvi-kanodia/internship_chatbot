"""
AI-enhanced chatbot using Gemini for more intelligent responses.
"""
import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
import concurrent.futures
from functools import lru_cache
from time import perf_counter
from chatbot.internship_bot import InternshipBot


class AIEnhancedInternshipBot(InternshipBot):
    """Internship bot enhanced with Gemini AI for better understanding and responses."""
    
    def __init__(self, csv_path: str = "data/internships.csv", api_key: str = None, ai_timeout: int = 10):
        super().__init__(csv_path)
        self.logger = logging.getLogger('ai_enhanced_bot')
        self.ai_timeout = ai_timeout
        
        # Initialize Gemini
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.ai_enabled = True
                self.logger.info("Gemini AI enabled")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None
                self.ai_enabled = False
                self.logger.info("Falling back to rule-based responses")
        else:
            self.model = None
            self.ai_enabled = False
            self.logger.info("Gemini AI disabled - using rule-based responses")
    
    def process_query_with_ai(self, query: str) -> str:
        """
        Process query using Gemini AI for better understanding and response generation.
        
        Args:
            query: User's query
        
        Returns:
            AI-generated response
        """
        if not self.ai_enabled:
            return self.process_query(query)  # Fallback to rule-based
        
        # Fast path: try rule-based search first (very quick). If results exist, return them.
        try:
            quick_results = self.search_internships(query, limit=10)
            if not quick_results.empty:
                self.logger.debug(f"Quick rule-based search returned {len(quick_results)} result(s) for query='{query}'")
                return self.format_internship_results(quick_results)
        except Exception:
            # If quick search errors, continue to AI path
            pass

        # Prepare context about available internships
        context = self._prepare_context()

        # Create prompt for Gemini
        prompt = f"""
You are an internship recommendation assistant. Based on the following internship data,
help the user find relevant opportunities.

Available Internships Data:
{context}

User Query: {query}

Please provide a helpful response that:
1. Directly addresses the user's query
2. Lists relevant internships with key details
3. Provides actionable advice
4. Is conversational and helpful

Format your response clearly with internship details.
"""

        # Use a thread + timeout wrapper so a slow/blocked AI call doesn't hang the bot
        try:
            self.logger.debug(f"Calling AI for query='{query}' with timeout={self.ai_timeout}s")
            ai_text = self._safe_generate(prompt, timeout=self.ai_timeout)
            if ai_text:
                return ai_text
            else:
                # Empty AI reply: fallback
                return self.process_query(query)
        except Exception as e:
            self.logger.error(f"AI processing failed or timed out: {e}")
            return self.process_query(query)

    def _safe_generate(self, prompt: str, timeout: int = 10) -> str:
        """Call the Gemini model in a worker thread and enforce a timeout.

        Returns the generated text or raises an exception on timeout/error.
        """
        if not self.ai_enabled or not self.model:
            raise RuntimeError("AI not enabled")

        def _call_model():
            try:
                resp = self.model.generate_content(prompt)
                # Guard against different response shapes
                if hasattr(resp, 'text'):
                    return resp.text
                elif isinstance(resp, dict) and 'content' in resp:
                    return resp['content']
                else:
                    return str(resp)
            except Exception as exc:
                # Re-raise to be captured by the future
                raise

        start = perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_call_model)
            try:
                result = future.result(timeout=timeout)
                elapsed = perf_counter() - start
                self.logger.debug(f"AI call completed in {elapsed:.2f}s")
                return result
            except concurrent.futures.TimeoutError:
                future.cancel()
                elapsed = perf_counter() - start
                self.logger.warning(f"AI call timed out after {elapsed:.2f}s")
                raise TimeoutError('AI call timed out')
    
    def _prepare_context(self) -> str:
        """Prepare context about available internships for AI."""
        if self.df.empty:
            return "No internship data available."
        
        # Get sample of internships for context
        sample_size = min(10, len(self.df))
        sample_df = self.df.head(sample_size)
        
        context_parts = []
        for _, row in sample_df.iterrows():
            context_parts.append(f"""
            Title: {row['title']}
            Organization: {row['organization']}
            Location: {row['location']}, {row['country']}
            Mode: {row['mode']}
            Target Audience: {row['target_audience']}
            Skills: {row['skills_required']}
            Stipend: {row['stipend']}
            """)
        
        return "\n".join(context_parts)
    
    def get_ai_recommendations(self, user_profile: Dict[str, Any], query: str = "") -> str:
        """
        Get AI-powered recommendations based on user profile.
        
        Args:
            user_profile: User profile dictionary
            query: Optional additional query context
        
        Returns:
            AI-generated recommendations
        """
        if not self.ai_enabled:
            # Fallback to rule-based recommendations
            results = self.recommend_internships(user_profile)
            return self.format_internship_results(results)
        
        try:
            # Prepare profile context
            profile_context = f"""
            User Profile:
            - Skills: {', '.join(user_profile.get('skills', []))}
            - Education Level: {user_profile.get('education_level', 'Not specified')}
            - Preferred Location: {user_profile.get('preferred_location', 'Not specified')}
            - Preferred Mode: {user_profile.get('preferred_mode', 'Not specified')}
            - Interests: {', '.join(user_profile.get('interests', []))}
            """
            
            # Prepare internship data
            internship_context = self._prepare_context()
            
            # Create prompt
            prompt = f"""
            You are an expert career advisor. Based on the user's profile and available internships, 
            provide personalized recommendations.
            
            {profile_context}
            
            Available Internships:
            {internship_context}
            
            Additional Query: {query}
            
            Please provide:
            1. Top 5 most relevant internships with detailed explanations
            2. Why each internship matches the user's profile
            3. Any gaps in skills that the user should consider developing
            4. General career advice based on their profile
            
            Be specific and actionable in your recommendations.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"AI recommendations failed: {e}")
            # Fallback to rule-based
            results = self.recommend_internships(user_profile)
            return self.format_internship_results(results)
    
    def ask_clarifying_questions_ai(self, query: str) -> List[str]:
        """
        Use AI to generate more intelligent clarifying questions.
        
        Args:
            query: User's initial query
        
        Returns:
            List of clarifying questions
        """
        if not self.ai_enabled:
            return self.ask_clarifying_questions(query)
        
        try:
            prompt = f"""
            The user asked: "{query}"
            
            This query seems vague or incomplete for finding internships. 
            Generate 3-5 specific, helpful clarifying questions that would help 
            me understand what internships they're looking for.
            
            Focus on:
            - Location preferences
            - Skills/technologies of interest
            - Work mode (remote/onsite/hybrid)
            - Stipend expectations
            - Duration preferences
            - Industry/domain interests
            
            Make the questions conversational and specific to internship searching.
            """
            
            response = self.model.generate_content(prompt)
            # Parse response into individual questions
            questions = [q.strip() for q in response.text.split('\n') if q.strip() and '?' in q]
            return questions[:5]  # Limit to 5 questions
            
        except Exception as e:
            self.logger.error(f"AI clarifying questions failed: {e}")
            return self.ask_clarifying_questions(query)
    
    def process_query(self, query: str) -> str:
        """Override to use AI-enhanced processing."""
        if self.ai_enabled:
            return self.process_query_with_ai(query)
        else:
            # Fallback to parent class method
            return super().process_query(query)
