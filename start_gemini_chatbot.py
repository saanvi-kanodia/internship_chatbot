"""Start an AI-enhanced chatbot (Gemini) that loads internships CSV and serves a simple CLI.

This script will use `chatbot.ai_enhanced_bot.AIEnhancedInternshipBot` when a Gemini API key
is available via environment or --api-key, otherwise it falls back to the rule-based bot.
"""
import argparse
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Prefer python-dotenv if available
load_dotenv()

from chatbot.internship_bot import InternshipBot

try:
    from chatbot.ai_enhanced_bot import AIEnhancedInternshipBot
except Exception:
    AIEnhancedInternshipBot = None


def main():
    parser = argparse.ArgumentParser(description='Start Gemini-backed internship chatbot')
    parser.add_argument('--csv', default='data/internships.csv', help='Path to internships CSV')
    parser.add_argument('--api-key', help='Gemini API key (overrides environment)')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--ai-timeout', type=int, default=10, help='Timeout for AI calls in seconds')
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    api_key = os.getenv('GEMINI_API_KEY')

    if api_key and AIEnhancedInternshipBot is not None:
        bot = AIEnhancedInternshipBot(args.csv, api_key, ai_timeout=args.ai_timeout)
        print('AI-enhanced Gemini chatbot started')
    else:
        bot = InternshipBot(args.csv)
        print('Rule-based chatbot started')

    # Simple CLI loop
    print('\nType queries (quit to exit)')
    while True:
        try:
            q = input('You: ').strip()
            if q.lower() in ('quit', 'exit'):
                break
            if not q:
                continue
            resp = bot.process_query(q)
            print('\nBot:')
            print(resp)
        except KeyboardInterrupt:
            print('\nExiting')
            break


if __name__ == '__main__':
    main()
