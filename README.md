# Internship Scraping and Recommendation System

A comprehensive Python system that scrapes internships from multiple sources and provides intelligent recommendations through a chatbot interface.

## 🚀 Features

### Internship Scraping

- **Multiple Sources**: Internshala, AICTE, Google STEP, and more
- **Unified Schema**: Consistent data format across all sources
- **Deduplication**: Automatic removal of duplicate internships
- **Comprehensive Data**: Title, organization, location, skills, stipend, and more

### Chatbot Backend

- **Natural Language Queries**: "Show me AI/ML internships in Bangalore"
- **Profile-based Recommendations**: Parse resume and get personalized suggestions
- **Interactive Mode**: Ask clarifying questions for vague queries
- **Filtering**: Location, mode, skills, organization, stipend, and more
- **AI-Enhanced Responses**: Optional Gemini AI integration for smarter responses

### Resume Parsing

- **PDF Processing**: Extract skills, education, and experience
- **Smart Matching**: Match profile against internship requirements
- **Keyword Extraction**: Identify technical and soft skills

## 📁 Project Structure

```
placement_portal/
├── scrapers/                 # Web scrapers for different sources
│   ├── base_scraper.py      # Base scraper class
│   └── google_step_scraper.py
├── chatbot/                 # Chatbot backend
│   ├── internship_bot.py    # Main bot logic
│   ├── resume_parser.py     # Resume parsing
│   └── cli.py              # Command-line interface
├── models/                  # Data models
│   └── internship.py       # Internship schema
├── data/                   # Data storage
│   └── internships.csv     # Scraped internships
├── pipeline.py             # Main scraping pipeline
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd placement_portal
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (optional, for advanced text processing):

   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

5. **Setup AI features** (optional, for Gemini AI integration):
   ```bash
   # Add your Gemini API key to .env file
   echo "GEMINI_API_KEY=your_api_key_here" >> .env
   ```

## 🚀 Quick Start

### 1. Scrape Internships

Run the pipeline to scrape internships from all sources:

```bash
python pipeline.py
```

This will:

- Scrape internships from Internshala, AICTE, and Google STEP
- Deduplicate results
- Save to `data/internships.csv`
- Generate summary statistics

### 2. Start the Chatbot

#### Interactive Mode

```bash
python -m chatbot.cli
```

#### Single Query Mode

```bash
python -m chatbot.cli --query "Show me AI/ML internships in Bangalore"
```

#### With Resume Parsing

```bash
python -m chatbot.cli --resume path/to/your/resume.pdf
```

#### With AI Enhancement (Gemini)

```bash
# Method 1: Add API key to .env file (recommended)
echo "GEMINI_API_KEY=your_api_key_here" >> .env
python -m chatbot.cli

# Method 2: Set environment variable
export GEMINI_API_KEY=your_api_key_here
python -m chatbot.cli

# Method 3: Pass API key directly
python -m chatbot.cli --ai --api-key your_api_key_here
```

## 💬 Usage Examples

### Natural Language Queries

```
You: Show me internships in Bangalore with stipend
Bot: Found 15 internship(s):
     1. Software Developer Intern
         Organization: TechCorp
         Location: Bangalore, India
         Mode: Onsite
         Stipend: ₹15,000/month
         ...

You: List AI/ML internships that are remote
Bot: Found 8 internship(s):
     1. Machine Learning Intern
         Organization: AI Startup
         Location: Remote
         Mode: Remote
         Skills: Python, TensorFlow, Scikit-learn
         ...
```

### Profile-based Recommendations

```
You: parse resume my_resume.pdf
Bot: ✅ Resume parsed: 12 skills found

You: recommend internships based on my profile
Bot: Found 5 recommended internship(s) based on your profile:
     1. Full Stack Developer Intern
         Relevance Score: 8/10
         Matches: Python, React, JavaScript
         ...
```

### Interactive Clarification

```
You: internships
Bot: Your query seems a bit vague. Could you please clarify:
     • What location are you interested in? (e.g., Bangalore, Mumbai, Remote)
     • What work mode do you prefer? (Remote, Onsite, or Hybrid)
     • What skills or technologies are you interested in? (e.g., Python, React, AI/ML)
     • Are you looking for paid internships? What's your stipend expectation?
```

## 🔧 Configuration

### Adding New Scrapers

1. Create a new scraper class inheriting from `BaseScraper`:

   ```python
   from scrapers.base_scraper import BaseScraper

   class NewSourceScraper(BaseScraper):
       def __init__(self):
           super().__init__("NewSource")

       def scrape(self, max_results=None):
           # Implementation here
           pass
   ```

2. Add to pipeline.py:

   ```python
   from scrapers.new_source_scraper import NewSourceScraper

   scrapers = [
       InternshalaScraper(),
       AICTEScraper(),
       GoogleSTEPScraper(),
       NewSourceScraper()  # Add here
   ]
   ```

### Customizing Filters

Modify the `InternshipBot.filter_internships()` method to add new filtering criteria.

## 📊 Data Schema

Each internship record contains:

| Field                | Type | Description               |
| -------------------- | ---- | ------------------------- |
| title                | str  | Internship title          |
| organization         | str  | Company/organization name |
| country              | str  | Country                   |
| location             | str  | City/state                |
| type                 | str  | Always "Internship"       |
| eligibility_criteria | str  | Requirements              |
| target_audience      | str  | UG/PG/PhD                 |
| start_date           | str  | Start date                |
| duration             | str  | Duration                  |
| application_deadline | str  | Deadline                  |
| application_link     | str  | Apply URL                 |
| mode                 | str  | Remote/Onsite/Hybrid      |
| stipend              | str  | Stipend amount            |
| salary               | str  | Salary information        |
| visa_support         | str  | Visa support info         |
| tags                 | str  | Comma-separated tags      |
| source               | str  | Scraping source           |
| scraped_timestamp    | str  | When scraped              |
| description          | str  | Full description          |
| skills_required      | str  | Required skills           |
| perks                | str  | Perks offered             |
| company_size         | str  | Company size              |
| industry             | str  | Industry                  |

## 🐛 Troubleshooting

### Common Issues

1. **No internships found**:

   - Check if `data/internships.csv` exists
   - Run `python pipeline.py` to scrape data
   - Check internet connection

2. **Scraping errors**:

   - Some sites may block requests
   - Try running with delays between requests
   - Check if site structure has changed

3. **Resume parsing fails**:
   - Ensure PDF is not password-protected
   - Check if PDF contains text (not just images)
   - Try with a different PDF format

### Debug Mode

Run with verbose logging:

```bash
python -m chatbot.cli --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source. Please check the license file for details.

## 🔒 Security Best Practices

- **API Keys**: Stored in `.env` file (not committed to git)
- **Environment Variables**: Production standard for sensitive data
- **Git Ignore**: `.env` file is automatically ignored
- **Template**: Use `env.template` for reference
- **Fallback**: Legacy config file support for migration

## 🔮 Future Enhancements

- [ ] Add more scraping sources (Microsoft, Amazon, etc.)
- [ ] Implement semantic similarity matching
- [ ] Add web interface
- [ ] Email notifications for new internships
- [ ] Advanced filtering options
- [ ] Machine learning-based recommendations
- [ ] Integration with job application tracking

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Look at existing issues
3. Create a new issue with detailed description

---

**Happy job hunting! 🎯**
