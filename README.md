# 🐞 AI Bug Reporter

A Streamlit-based tool for generating detailed bug reports using OpenAI models and automatically creating issues in Jira.

## Features

- **Free-text bug description** with optional screenshot upload (BLIP-based captioning).
- **AI-powered JSON bug formatting**: title, description, steps to reproduce, and expected result.
- **Interactive UI**: copy buttons for each section.
- **Jira integration**:
  - Configure via environment variables (`JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`).
  - Dropdowns for **Environment** and **Fix Versions** matching your Jira instance.
  - Automatic ADF payload creation and issue submission.
- **Loading spinners** for all long-running operations (image processing, AI generation, Jira API calls).

## Prerequisites

- Python 3.10+
- An OpenAI API key
- A Jira Cloud instance with:
  - A custom **Environment** single-select field (e.g. QA, Production, Staging, etc.)
  - Configured **Fix Versions** in your project
  - An API token generated from [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-org/ai-bug-reporter.git
   cd ai-bug-reporter
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```dotenv
   OPENAI_API_KEY=sk-...
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=you@company.com
   JIRA_API_TOKEN=your_jira_api_token
   JIRA_PROJECT_KEY=ABC
   ```

## Running Locally

```bash
streamlit run ai_bug_reporter.py
```

Then open the URL shown in the terminal (e.g., `http://localhost:8501`).

## Docker

1. Build the image:
   ```bash
   docker build -t ai-bug-reporter:latest .
   ```

2. Run the container (with your `.env`):
   ```bash
   docker run -p 8501:8501 --env-file .env ai-bug-reporter:latest
   ```

## Usage

1. Enter a **bug description** in free text.
2. (Optional) Upload a **screenshot** for additional context.
3. Select **Environment** from the dropdown.
4. Select one or more **Fix Versions**.
5. Click **Generate Bug** to let the AI format the report.
6. Review the generated sections and use the **copy buttons** as needed.
7. Click **Create in JIRA** to submit the issue.  
   - You’ll get immediate success/error feedback with a link to the new Jira issue.

## Project Structure

```
.
├── ai_bug_reporter.py    # Main Streamlit application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition
├── .env                  # Environment variable definitions (local)
└── README.md             # This file
```
