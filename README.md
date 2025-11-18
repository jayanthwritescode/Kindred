# EduBridge AI Tutoring System

EduBridge is a modular, multi-agent educational system that adapts content to student preferences using Google's Gemini API.

## Features
- Student-facing TutorAgent that runs interactive sessions
- ContentAgent that generates lessons using Gemini
- InsightAgent that summarizes student progress for parents/teachers
- CLI interface for running custom sessions
- JSON reports and profiles saved for every session

## Requirements
```bash
pip install google-generativeai python-dotenv
```

## Setup
Create a `.env` file or export:
```bash
export GEMINI_API_KEY=your-gemini-api-key
```

## Run a session
```bash
python main.py --student student001 --name Alex --topic "Introduction to Fractions"
```

Reports will be saved to `reports/` directory.
