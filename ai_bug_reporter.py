import os
import re
import json
import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import requests

# ─── Load env vars ─────────────────────────────────────────────────────────────
load_dotenv()

# ─── Streamlit page config ───────────────────────────────────────────────────
st.set_page_config(page_title="🐞 AI Bug Reporter", layout="wide")

# ─── Session state defaults ───────────────────────────────────────────────────
if 'bug' not in st.session_state:
    st.session_state.bug = None
if 'jira_feedback' not in st.session_state:
    st.session_state.jira_feedback = None

# ─── JIRA Configuration from ENV ─────────────────────────────────────────────
st.sidebar.subheader("🛠 JIRA Configuration (via ENV VARs)")
jira_url = st.sidebar.text_input(
    "JIRA Base URL",
    value=os.getenv("JIRA_URL", ""),
    placeholder="https://your-domain.atlassian.net",
    help="The base URL of your Jira instance, e.g. https://your-domain.atlassian.net"
)
jira_email = st.sidebar.text_input(
    "JIRA Email",
    value=os.getenv("JIRA_EMAIL", ""),
    help="Your Atlassian account email"
)
jira_token = st.sidebar.text_input(
    "JIRA API Token",
    value=os.getenv("JIRA_API_TOKEN", ""),
    type="password",
    help="Create one at https://id.atlassian.com/manage-profile/security/api-tokens"
)
jira_proj = st.sidebar.text_input(
    "Project Key",
    value=os.getenv("JIRA_PROJECT_KEY", ""),
    placeholder="e.g. ABC",
    help="The key of the Jira project where bugs will be filed"
)

# ─── OpenAI Configuration ────────────────────────────────────────────────────
st.sidebar.subheader("🔑 OpenAI Configuration")
default_openai = os.getenv("OPENAI_API_KEY", "")
openai_input = st.sidebar.text_input(
    "Your OpenAI API Key",
    value=default_openai,
    type="password",
    help="Enter your key (sk-...), or set OPENAI_API_KEY as an env var"
)
openai_key = openai_input.strip() or default_openai
if not openai_key:
    st.sidebar.error("Please enter a valid OpenAI API key.")
    st.stop()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stButton>button { background-color: #0052CC; color: white; border-radius: 8px;
                     padding: 8px 20px; font-weight: bold; }
  .stExpander { background: #FFF; border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 16px;
                margin-bottom: 16px; }
  .title { font-size: 2.5rem; color: #0052CC; font-weight: 600;
            margin-bottom: 24px; }
  section.stSidebar { width: 400px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Main UI ─────────────────────────────────────────────────────────────────
st.markdown("<div class='title'>🐞 AI Bug Reporter</div>", unsafe_allow_html=True)
st.markdown("Describe your bug and optionally upload one screenshot for context.", unsafe_allow_html=True)

bug_desc = st.text_area(
    "📝 Bug Description",
    height=150,
    placeholder="E.g. Clicking ‘Save’ does nothing and dialog remains open..."
)

bug_image = st.file_uploader(
    "📷 Upload a screenshot (optional)",
    type=["png","jpg","jpeg"]
)

# ─── New: dropdowns for Environment & Fix Versions ───────────────────────────
ENV_OPTIONS = ["QA", "Production", "IT", "On-Prem", "All Environments", "QA + Production", "Staging"]
environment = st.selectbox(
    "🌐 Environment",
    options=ENV_OPTIONS,
    help="Select the environment where the bug occurred"
)

VERSION_OPTIONS = ["Kal Sense Version 1.4", "Kal Sense Version 1.3"]
fix_versions = st.multiselect(
    "🏷 Fix Versions",
    options=VERSION_OPTIONS,
    help="Select one or more fix versions"
)

# ─── If image provided, process under a spinner ──────────────────────────────
image_caption = None
if bug_image:
    with st.spinner("Processing screenshot…"):
        img = Image.open(bug_image)
        processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base", use_fast=False
        )
        cap_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        inputs = processor(images=img, return_tensors="pt")
        inputs = {k: v.to("cpu") for k, v in inputs.items()}
        cap_model = cap_model.to("cpu")
        out_ids = cap_model.generate(**inputs)
        image_caption = processor.decode(out_ids[0], skip_special_tokens=True)
    st.image(img, caption=bug_image.name, width=300)
    st.success("Screenshot processed!")

# ─── Action button: Generate Bug ─────────────────────────────────────────────
gen_btn = st.button("Generate Bug", key="gen")

# ─── Initialize OpenAI client ────────────────────────────────────────────────
client = OpenAI(api_key=openai_key)

# ─── Generate Bug Report under spinner ────────────────────────────────────────
if gen_btn:
    if not bug_desc.strip():
        st.error("Please describe the bug first.")
    else:
        prompt = (
            "You are a helpful assistant that formats bug reports as JSON.\n"
            "Generate a JSON object with fields: title, description, steps (array), expected.\n"
            f"Bug description:\n{bug_desc}\n"
        )
        if image_caption:
            prompt += f"\nScreenshot context: {image_caption}\n"
        prompt += "\nRespond *only* with the JSON object."

        with st.spinner("Generating bug report…"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You format bug reports as JSON."},
                    {"role":"user","content":prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )

        raw = res.choices[0].message.content
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        js = m.group(0) if m else raw

        try:
            st.session_state.bug = json.loads(js)
            st.session_state.jira_feedback = None
            st.success("✅ Bug report generated!")
        except Exception as e:
            st.error(f"Failed to parse JSON: {e}")
            st.code(raw, language="json")

# ─── Display & Create in JIRA ────────────────────────────────────────────────
bug = st.session_state.bug
if bug:
    st.markdown("## Generated Bug Report")

    st.markdown("**Title**")
    st.code(bug["title"], language="")

    st.markdown("**Description**")
    st.code(bug["description"], language="")

    st.markdown("**Steps to Reproduce**")
    steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(bug["steps"]))
    st.code(steps_text, language="")

    st.markdown("**Expected Result**")
    st.code(bug["expected"], language="")

    # ─── Create in JIRA ──────────────────────────────────────────────────────
    create_jira = st.button("Create in JIRA", key="create_jira")
    if create_jira:
        # required fields check
        required = [
            ("URL", jira_url),
            ("Email", jira_email),
            ("Token", jira_token),
            ("Project Key", jira_proj),
            ("Environment", environment),
            ("Fix Versions", fix_versions),
        ]
        missing = [name for name, val in required if not val]
        if missing:
            st.error(f"Please fill out required fields: {', '.join(missing)}")
        else:
            # build ADF for description
            lines = [bug["description"], "Steps to Reproduce:"] \
                  + [f"{i+1}. {s}" for i, s in enumerate(bug["steps"])] \
                  + ["Expected Result:", bug["expected"]]
            adf_content = [
                {"type":"paragraph", "content":[{"type":"text","text":line}]}
                for line in lines
            ]
            description_adf = {"type":"doc","version":1,"content":adf_content}

            # payload
            payload = {
                "fields": {
                    "project":         {"key": jira_proj},
                    "summary":         bug["title"],
                    "description":     description_adf,
                    "issuetype":       {"name":"Bug"},
                    "customfield_10618": { "value": environment },
                    "fixVersions":       [{"name": v} for v in fix_versions],
                    "customfield_10420": {"type":"doc","version":1,"content":[
                        {"type":"paragraph","content":[{"type":"text","text":s}]}
                        for s in bug["steps"]
                    ]},
                    "customfield_10421": {"type":"doc","version":1,"content":[
                        {"type":"paragraph","content":[{"type":"text","text":bug["description"]}]}
                    ]},
                    "customfield_10422": {"type":"doc","version":1,"content":[
                        {"type":"paragraph","content":[{"type":"text","text":bug["expected"]}]}
                    ]},
                }
            }
            url  = jira_url.rstrip("/") + "/rest/api/3/issue"
            auth = HTTPBasicAuth(jira_email, jira_token)
            headers = {"Content-Type":"application/json"}

            with st.spinner("Creating issue in JIRA…"):
                resp = requests.post(url, auth=auth, headers=headers, json=payload)

            if resp.status_code == 201:
                key = resp.json().get("key")
                st.session_state.jira_feedback = ("success", key)
            else:
                st.session_state.jira_feedback = ("error",
                                                  resp.status_code,
                                                  resp.text)

    # ─── Show feedback ────────────────────────────────────────────────────────
    fb = st.session_state.jira_feedback
    if fb:
        if fb[0] == "success":
            st.success(f"✅ Issue created: {fb[1]}")
            st.markdown(f"[View in JIRA]({jira_url.rstrip('/')}/browse/{fb[1]})")
        else:
            st.error(f"❌ Jira API Error {fb[1]}:\n{fb[2]}")
