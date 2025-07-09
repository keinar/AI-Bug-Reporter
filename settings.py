JIRA_CUSTOMFIELDS = {
    "steps": "customfield_10420",
    "expected": "customfield_10422",
    "actual": "customfield_10421",
    "env": "customfield_10618"
}

ENV_OPTIONS = ["QA", "Production", "IT", "On-Prem", "All Environments", "QA + Production", "Staging"]
VERSION_OPTIONS = ["Kal Sense Version 1.5", "Kal Sense Version 1.4", "Kal Sense Version 1.3"]

AI_MODEL_OPTIONS = [
    "gpt-4o-mini", "gpt-4.1-nano",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro"
]

REQUIRED_KEYS = {"title", "description", "steps", "expected", "actual"}
