"""
Command-line interface for the internship chatbot.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from chatbot.internship_bot import InternshipBot
from chatbot.ai_enhanced_bot import AIEnhancedInternshipBot
from chatbot.resume_parser import ResumeParser
from api_config import get_gemini_api_key, print_api_key_instructions


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def interactive_mode(bot: InternshipBot):
    """Run interactive chat mode."""
    print("\n🤖 Internship Recommendation Bot")
    print("=" * 50)
    print("Type 'help' for commands, 'quit' to exit\n")
    
    while True:
        try:
            query = input("You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            elif query.lower() == 'help':
                print_help()
                continue
            elif query.lower() == 'reload':
                bot.reload_data()
                print("✅ Data reloaded successfully!")
                continue
            elif query.lower() == 'profile':
                show_profile(bot)
                continue
            elif query.lower().startswith('set profile'):
                set_profile_interactive(bot)
                continue
            elif query.lower().startswith('parse resume'):
                parse_resume_interactive(bot)
                continue
            elif not query:
                continue
            
            # Process query
            response = bot.process_query(query)
            print(f"\nBot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
• help - Show this help message
• reload - Reload internship data from CSV
• profile - Show current user profile
• set profile - Set user profile interactively
• parse resume <path> - Parse resume PDF and set profile
• quit/exit/q - Exit the bot

Example Queries:
• "Show me internships in Bangalore with stipend"
• "List AI/ML internships that are remote"
• "Find Python internships for undergraduates"
• "Recommend internships based on my profile"
• "Show me Google internships"
"""
    print(help_text)


def show_profile(bot: InternshipBot):
    """Show current user profile."""
    profile = bot.user_profile
    print("\n📋 Current User Profile:")
    print("-" * 30)
    print(f"Skills: {', '.join(profile['skills']) if profile['skills'] else 'Not set'}")
    print(f"Education Level: {profile['education_level'] or 'Not set'}")
    print(f"Preferred Location: {profile['preferred_location'] or 'Not set'}")
    print(f"Preferred Mode: {profile['preferred_mode'] or 'Not set'}")
    print(f"Stipend Expectation: {profile['stipend_expectation'] or 'Not set'}")
    print(f"Interests: {', '.join(profile['interests']) if profile['interests'] else 'Not set'}")
    print()


def set_profile_interactive(bot: InternshipBot):
    """Set user profile interactively."""
    print("\n🔧 Setting User Profile")
    print("-" * 25)
    
    # Skills
    skills_input = input("Enter your skills (comma-separated): ").strip()
    if skills_input:
        bot.user_profile['skills'] = [skill.strip() for skill in skills_input.split(',')]
    
    # Education level
    print("\nEducation Level options: UG, PG, PhD")
    education = input("Enter your education level: ").strip().upper()
    if education in ['UG', 'PG', 'PHD']:
        bot.user_profile['education_level'] = education
    
    # Preferred location
    location = input("Enter preferred location: ").strip()
    if location:
        bot.user_profile['preferred_location'] = location
    
    # Preferred mode
    print("\nWork Mode options: Remote, Onsite, Hybrid")
    mode = input("Enter preferred work mode: ").strip().title()
    if mode in ['Remote', 'Onsite', 'Hybrid']:
        bot.user_profile['preferred_mode'] = mode
    
    # Stipend expectation
    stipend = input("Enter stipend expectation (e.g., 5000, 10000+): ").strip()
    if stipend:
        bot.user_profile['stipend_expectation'] = stipend
    
    # Interests
    interests_input = input("Enter your interests (comma-separated): ").strip()
    if interests_input:
        bot.user_profile['interests'] = [interest.strip() for interest in interests_input.split(',')]
    
    print("✅ Profile updated successfully!\n")


def parse_resume_interactive(bot: InternshipBot):
    """Parse resume and set profile."""
    resume_path = input("Enter path to resume PDF: ").strip()
    
    if not resume_path:
        print("❌ No resume path provided")
        return
    
    if not Path(resume_path).exists():
        print(f"❌ Resume file not found: {resume_path}")
        return
    
    try:
        parser = ResumeParser()
        profile = parser.parse_resume(resume_path)
        
        if profile:
            # Update bot profile with parsed information
            bot.user_profile.update(profile)
            print("✅ Resume parsed successfully!")
            print(f"Found {len(profile['skills'])} skills and {len(profile['interests'])} interests")
        else:
            print("❌ Could not parse resume")
    
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")


def run_single_query(bot: InternshipBot, query: str):
    """Run a single query and exit."""
    response = bot.process_query(query)
    print(response)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Internship Recommendation Bot')
    parser.add_argument('--csv', default='data/internships.csv', 
                       help='Path to internships CSV file')
    parser.add_argument('--query', help='Single query to process (non-interactive mode)')
    parser.add_argument('--resume', help='Path to resume PDF for profile parsing')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    parser.add_argument('--ai', action='store_true',
                       help='Enable AI-enhanced responses using Gemini')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        setup_logging()
    
    # Initialize bot (AI-enhanced or regular)
    api_key = args.api_key or get_gemini_api_key()
    
    # Auto-detect AI capability
    if api_key or args.ai:
        if not api_key:
            print("🔑 No Gemini API key found.")
            print_api_key_instructions()
            print("❌ AI mode requires Gemini API key. Falling back to rule-based mode.")
            bot = InternshipBot(args.csv)
            print("🔧 Rule-based mode enabled")
        else:
            bot = AIEnhancedInternshipBot(args.csv, api_key)
            print("🤖 AI-enhanced mode enabled with Gemini")
    else:
        bot = InternshipBot(args.csv)
        print("🔧 Rule-based mode enabled")
    
    if bot.df.empty:
        print("❌ No internship data found. Please run pipeline.py first to scrape internships.")
        sys.exit(1)
    
    # Parse resume if provided
    if args.resume:
        try:
            parser = ResumeParser()
            profile = parser.parse_resume(args.resume)
            if profile:
                bot.user_profile.update(profile)
                print(f"✅ Resume parsed: {len(profile['skills'])} skills found")
        except Exception as e:
            print(f"❌ Error parsing resume: {e}")
            sys.exit(1)
    
    # Run in single query mode or interactive mode
    if args.query:
        run_single_query(bot, args.query)
    else:
        interactive_mode(bot)


if __name__ == "__main__":
    main()
