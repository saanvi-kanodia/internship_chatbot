# Quick Start Guide

Get up and running with the Internship Scraping and Recommendation System in 5 minutes!

## 🚀 One-Command Setup

```bash
python setup.py
```

This will:

- Check Python version compatibility
- Install all dependencies
- Create necessary directories
- Run system tests
- Show you a demo



## 📋 Manual Setup (if needed)

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Create data directory**:

   ```bash
   mkdir -p data
   ```

3. **Test the system**:
   ```bash
   python test_system.py
   ```

## 🎯 Quick Usage

### 1. Scrape Internships

```bash
python pipeline.py
```

This scrapes internships from Internshala, AICTE, and Google STEP.

### 2. Start the Chatbot

```bash
python -m chatbot.cli
```

### 3. Try These Queries

- "Show me AI/ML internships in Bangalore"
- "Find remote internships with Python"
- "List internships for undergraduates"
- "Recommend internships based on my profile"

## 🔧 Advanced Usage

### Parse Your Resume

```bash
python -m chatbot.cli --resume path/to/your/resume.pdf
```

### Single Query Mode

```bash
python -m chatbot.cli --query "Show me Google internships"
```

### Run Demo

```bash
python demo.py
```

## 🐛 Troubleshooting

### No internships found?

- Run `python pipeline.py` first to scrape data
- Check if `data/internships.csv` exists

### Import errors?

- Make sure you're in the project directory
- Check if all dependencies are installed: `pip install -r requirements.txt`

### Scraping errors?

- Some sites may block requests
- Check your internet connection
- Try running with delays between requests

## 📚 What's Next?

1. **Add more scrapers**: Check `scrapers/` directory
2. **Customize filters**: Modify `chatbot/internship_bot.py`
3. **Add new features**: Extend the base classes
4. **Deploy**: Add a web interface or API

## 🆘 Need Help?

- Check the full README.md for detailed documentation
- Look at the demo.py for usage examples
- Run `python -m chatbot.cli --help` for command options

---

**Happy job hunting! 🎯**
