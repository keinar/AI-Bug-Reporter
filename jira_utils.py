import requests
from requests.auth import HTTPBasicAuth
from settings import JIRA_CUSTOMFIELDS


def build_jira_description_adf(bug):
    lines = [bug["description"], "Steps to Reproduce:"] \
            + [f"{i + 1}. {s}" for i, s in enumerate(bug["steps"])] \
            + ["Expected Result:", bug["expected"], "Actual Result:", bug["actual"]]
    adf_content = [
        {"type": "paragraph", "content": [{"type": "text", "text": line}]}
        for line in lines
    ]
    return {"type": "doc", "version": 1, "content": adf_content}


def build_jira_payload(bug, jira_proj, environment, fix_versions):
    return {
        "fields": {
            "project": {"key": jira_proj},
            "summary": bug["title"],
            "description": build_jira_description_adf(bug),
            "issuetype": {"name": "Bug"},
            JIRA_CUSTOMFIELDS["env"]: {"value": environment},
            "fixVersions": [{"name": v} for v in fix_versions],
            JIRA_CUSTOMFIELDS["steps"]: {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": s}]}
                for s in bug["steps"]
            ]},
            JIRA_CUSTOMFIELDS["expected"]: {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": bug["expected"]}]}
            ]},
            JIRA_CUSTOMFIELDS["actual"]: {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": bug["actual"]}]}
            ]},
        }
    }


def send_jira_issue(jira_url, jira_email, jira_token, payload):
    url = jira_url.rstrip("/") + "/rest/api/3/issue"
    auth = HTTPBasicAuth(jira_email, jira_token)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, auth=auth, headers=headers, json=payload)
    return resp
