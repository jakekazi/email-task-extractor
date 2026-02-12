# Email Task Extractor

An AI-powered tool that extracts structured tasks from unstructured emails using Large Language Models (LLMs). The system automatically assigns confidence scores and routes low-confidence tasks to human review.

## Features

- 🤖 **AI-Powered Extraction**: Uses Claude to extract tasks, deadlines, assignees, and priorities from email text
- 📊 **Confidence Scoring**: Dual-layer confidence system (LLM + rule-based adjustments)
- 🔀 **Automatic Routing**: Auto-approves high-confidence tasks, flags uncertain ones for review
- 📋 **Structured Output**: Converts messy emails into clean, actionable task lists
- 💡 **Interactive CLI**: Easy-to-use command-line interface
- 🌐 **Web Interface**: Beautiful Streamlit app for non-technical users

## Project Structure

```
email-task-extractor/
├── app.py                    # 🌐 Web application (RECOMMENDED)
├── task_extractor.py         # Core extraction logic and classes
├── main.py                   # Interactive CLI application
├── test_setup.py             # Installation verification
├── requirements.txt          # Python dependencies
├── .env.example              # Template for environment variables
├── sample_email.txt          # Sample email for testing
├── run_web_app.bat           # Quick launcher (Windows)
├── run_web_app.sh            # Quick launcher (Mac/Linux)
├── HACKATHON_GUIDE.md        # Guide for demos and presentations
└── README.md                 # This file
```

## Prerequisites

- Python 3.8 or higher (already installed ✅)
- Anthropic API key (get one at https://console.anthropic.com/)

## Quick Start

### 🌐 Option A: Web Application (RECOMMENDED)

**Best for:** Hackathons, work demos, sharing with non-technical users

#### Setup (2 minutes):

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API key:**
```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

3. **Launch the web app:**
```bash
streamlit run app.py
```

**Or simply double-click:**
- Windows: `run_web_app.bat`
- Mac/Linux: `run_web_app.sh`

The app opens at `http://localhost:8501` with a beautiful interface!

**Web App Features:**
- ✨ Professional, user-friendly interface
- 📊 Real-time AI extraction with visual feedback
- 🎨 Color-coded confidence scores (green/yellow/red)
- 📤 Export to CSV, JSON, and Markdown
- ⚙️ Adjustable confidence thresholds
- 📈 Processing statistics and history

---

### 🖥️ Option B: Command Line Interface

**Best for:** Developers and technical users

1. **Verify installation:**
```bash
python test_setup.py
```

2. **Run interactive mode:**
```bash
python main.py
```

3. **Use as library:**
3. **Use as library:**
```python
from task_extractor import process_email

result = process_email("Your email text here...")
for task in result['processed_tasks']:
    print(f"Task: {task['task_description']}")
```

---

## Screenshots

### Web Application
The web app provides an intuitive interface where users can:
- Paste emails or upload files
- See real-time extraction with confidence scores
- Edit and export tasks
- Track processing history

### Confidence Score System

**LLM Confidence (0.0 - 1.0)**:
- 0.8-1.0: Explicitly stated, very clear
- 0.5-0.7: Clear task but some ambiguity
- 0.0-0.5: Vague or highly uncertain

**Rule-Based Adjustments**:
- Missing deadline: -0.15
- Unspecified assignee: -0.20
- Vague language: -0.10

### 3. Automatic Routing

Based on final confidence scores:

| Confidence | Status | Action |
|------------|--------|--------|
| ≥ 0.7 | ✅ Auto-approved | Ready to add to task system |
| 0.5 - 0.7 | ⚠️ Needs review | Standard review queue |
| < 0.5 | 🔴 Urgent review | High-priority review queue |

## Example Usage

### Sample Email
```
Subject: Q1 Deliverables

Hi team,

Sarah - Please finalize the marketing report by March 20th. 
This is critical.

The engineering team should review the API docs sometime 
before end of quarter.

Thanks!
```

### Extracted Output
```json
{
  "tasks": [
    {
      "task_description": "Finalize the marketing report",
      "assignee": "Sarah",
      "deadline": "2024-03-20",
      "priority": "high",
      "confidence_score": 0.95,
      "review_status": "auto_approved"
    },
    {
      "task_description": "Review API documentation",
      "assignee": "engineering team",
      "deadline": null,
      "priority": "medium",
      "confidence_score": 0.58,
      "review_status": "needs_review"
    }
  ]
}
```

## Customization

### Adjust Confidence Thresholds

Edit `task_extractor.py`:
```python
queue = TaskReviewQueue(
    auto_approve_threshold=0.8,  # Raise for stricter auto-approval
    high_priority_threshold=0.6   # Adjust review urgency threshold
)
```

### Modify Rule-Based Penalties

Edit the `calculate_final_confidence` method in `task_extractor.py`:
```python
if not task.get('deadline'):
    penalties += 0.15  # Adjust this value
```

### Change LLM Model

Edit the model in `task_extractor.py`:
```python
model="claude-sonnet-4-20250514"  # or claude-opus-4-20250514 for more accuracy
```

## Confidence Scoring Guidelines

The system assigns confidence based on:

✅ **High Confidence (0.8-1.0)**
- Explicit task statement
- Clear deadline with specific date
- Named assignee
- Unambiguous language

⚠️ **Medium Confidence (0.5-0.7)**
- Clear task but vague deadline ("next week", "soon")
- Assignee is a team/group not individual
- Some contextual inference needed

🔴 **Low Confidence (0.0-0.5)**
- Vague task description
- No deadline mentioned
- No assignee specified
- Conditional language ("might", "maybe")

## Troubleshooting

### "ANTHROPIC_API_KEY not found" error
- Make sure you created a `.env` file (not `.env.example`)
- Check that your API key is correctly pasted
- Ensure there are no extra spaces or quotes around the key

### Import errors
```bash
pip install -r requirements.txt --upgrade
```

### JSON parsing errors
- The LLM occasionally returns invalid JSON
- The system catches this and returns an error response
- Try running again or adjust the prompt temperature

## Next Steps

To integrate this into a production system:

1. **Email Integration**: Connect to Gmail API, IMAP, or email webhooks
2. **Database**: Store extracted tasks in PostgreSQL/MongoDB
3. **Review Interface**: Build a web UI for human reviewers
4. **Task System Integration**: Push auto-approved tasks to Asana/Jira/etc.
5. **Monitoring**: Track confidence score accuracy and false positive/negative rates
6. **Feedback Loop**: Store human corrections to improve prompts over time

## API Usage Costs

Approximate costs (as of Feb 2025):
- Claude Sonnet 4: ~$0.003 per email (varies by length)
- Processing 1000 emails: ~$3

## License

MIT License - feel free to use and modify for your projects.

## Support

Questions or issues? Check the code comments or modify the prompts in `task_extractor.py` to better suit your use case.
