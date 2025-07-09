# 🐞 AI Bug Reporter

A Streamlit-based tool for generating detailed bug reports using OpenAI **and Google Gemini** models, with automatic issue creation in Jira.

---

<img alt="img.png" height="500" src="img.png" width="1000"/>

## Features

- **Free-text bug description** with optional screenshot upload (BLIP-based captioning).
- **AI-powered JSON bug formatting**: title, description, steps to reproduce, expected result, and actual result.
- **Multi-provider support**: Choose between OpenAI (`gpt-4o-mini`, `gpt-4.1-nano`, etc.) and **Google Gemini** (`gemini-2.5-flash`, `gemini-2.5-pro`, etc.).
- **Interactive UI**: fully editable bug reports before submission.
- **Jira integration**:
  - Configure via environment variables or sidebar input.
  - Dropdowns for **Environment** and **Fix Versions**.
  - Automatic ADF payload creation and issue submission.
- **Loading spinners** for all long-running operations (image processing, AI generation, Jira API calls).
- **Modular codebase**: easy maintenance and extension (`ai_models.py`, `jira_utils.py`, etc.).
- **Gemini Model Discovery**: Includes a utility script `find_available_models.py` to list all Google Gemini models accessible to your API key.

---

## Prerequisites

- Python 3.10+
- An OpenAI API key (get from [OpenAI](https://platform.openai.com/api-keys))
- A Google Gemini API key (get from [Google AI Studio](https://aistudio.google.com/app/apikey))
- A Jira Cloud instance with:
  - A custom **Environment** single-select field (e.g., QA, Production, Staging, etc.)
  - Configured **Fix Versions** in your project
  - An API token from [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

---


## ⚠️ Jira Custom Fields Mapping

> **Important:** To enable issue creation in Jira, you must update the custom field IDs in `settings.py` (`JIRA_CUSTOMFIELDS`) to match your own Jira project’s configuration.
>
> Example:
>
> ```python
> JIRA_CUSTOMFIELDS = {
>     "steps":    "customfield_10420",
>     "expected": "customfield_10422",
>     "actual":   "customfield_10421",
>     "env":      "customfield_10618"
> }
> ```
>
> - Find the custom field IDs in your Jira instance (Admin → Issues → Custom fields, or by inspecting the API).
> - **If the IDs don’t match, Jira will return field errors or the issue won’t be created as expected.**

___

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/keinar/AI-Bug-Reporter.git
   cd AI-Bug-Reporter
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables (add only what you use):

   ```dotenv
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=your-gemini-api-key
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=you@company.com
   JIRA_API_TOKEN=your_jira_api_token
   JIRA_PROJECT_KEY=ABC
   ```

---

## Running Locally

```bash
streamlit run ai_bug_reporter.py
```

Then open the URL shown in the terminal (e.g., `http://localhost:8501`).

---

## Docker

1. Build the image:

   ```bash
   docker build -t ai-bug-reporter:latest .
   ```

2. Run the container (with your `.env`):

   ```bash
   docker run -p 8501:8501 --env-file .env ai-bug-reporter:latest
   ```

---

## Usage

1. Enter a **bug description** in free text.
2. (Optional) Upload a **screenshot** for additional context.
3. Select **Environment** from the dropdown.
4. Select one or more **Fix Versions**.
5. Select your preferred **AI model** (OpenAI or Gemini).
6. Click **Generate Bug** to let the AI format the report.
7. Edit the generated bug details as needed.
8. Click **Create in JIRA** to submit the issue.
   - You’ll get immediate success/error feedback with a link to the new Jira issue.

---

## Project Structure

```
.
├── ai_bug_reporter.py      # Main Streamlit application (UI)
├── ai_models.py            # OpenAI & Gemini API integration, parsing
├── jira_utils.py           # Jira payload building and API calls
├── image_captioning.py     # BLIP-based screenshot captioning
├── settings.py             # Constants & field mappings
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .env                    # Environment variable definitions (local)
├── README.md               # This file
└── find_available_models.py# List available Gemini models for your key
```

---

## Google Gemini Notes

- Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
- Not all Gemini models may be available to every account.\
  To see which models you can use, run the included script:
  ```bash
  python find_available_models.py
  ```
 
- Use the full model name as shown (e.g., `"models/gemini-2.5-flash"`).

---

## Contributing

Pull requests welcome!\
For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](https://github.com/keinar/AI-Bug-Reporter/blob/main/LICENSE)
