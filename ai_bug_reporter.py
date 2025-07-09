import os
import streamlit as st
from dotenv import load_dotenv
from settings import JIRA_CUSTOMFIELDS, ENV_OPTIONS, VERSION_OPTIONS, AI_MODEL_OPTIONS
from ai_models import call_openai_model, call_gemini_model, parse_bug_json
from image_captioning import generate_image_caption
from jira_utils import build_jira_payload, send_jira_issue

load_dotenv()
st.set_page_config(page_title="🐞 AI Bug Reporter", layout="wide")

if 'bug' not in st.session_state:
    st.session_state.bug = None
if 'jira_feedback' not in st.session_state:
    st.session_state.jira_feedback = None

# -- Sidebar -- #
st.sidebar.subheader("🛠 JIRA Configuration (via ENV VARs)")
jira_url = st.sidebar.text_input("JIRA Base URL", value=os.getenv("JIRA_URL", ""),
                                 placeholder="https://your-domain.atlassian.net")
jira_email = st.sidebar.text_input("JIRA Email", value=os.getenv("JIRA_EMAIL", ""))
jira_token = st.sidebar.text_input("JIRA API Token", value=os.getenv("JIRA_API_TOKEN", ""), type="password")
jira_proj = st.sidebar.text_input("Project Key", value=os.getenv("JIRA_PROJECT_KEY", ""), placeholder="e.g. ABC")

st.sidebar.subheader("🤖 AI Model Selection")
selected_model = st.sidebar.selectbox("Model (OpenAI or Gemini)", AI_MODEL_OPTIONS)

st.sidebar.subheader("🔑 API Keys")
default_openai = os.getenv("OPENAI_API_KEY", "")
openai_input = st.sidebar.text_input("OpenAI API Key", value=default_openai, type="password")
openai_key = openai_input.strip() or default_openai

default_gemini = os.getenv("GEMINI_API_KEY", "")
gemini_input = st.sidebar.text_input("Gemini API Key", value=default_gemini, type="password")
gemini_key = gemini_input.strip() or default_gemini

if selected_model.startswith("gpt-") and not openai_key:
    st.sidebar.error("Please enter a valid OpenAI API key.")
    st.stop()
if selected_model.startswith("gemini") and not gemini_key:
    st.sidebar.error("Please enter a valid Gemini API key.")
    st.stop()

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

st.markdown("<div class='title'>🐞 AI Bug Reporter</div>", unsafe_allow_html=True)
st.markdown("Describe your bug and optionally upload one screenshot for context.", unsafe_allow_html=True)

bug_desc = st.text_area("📝 Bug Description", height=150,
                        placeholder="E.g. Clicking ‘Save’ does nothing and dialog remains open...")
bug_image = st.file_uploader("📷 Upload a screenshot (optional)", type=["png", "jpg", "jpeg"])
environment = st.selectbox("🌐 Environment", options=ENV_OPTIONS)
fix_versions = st.multiselect("🏷 Fix Versions", options=VERSION_OPTIONS)

# -- BLIP -- #
image_caption = None
if bug_image:
    with st.spinner("Processing screenshot…"):
        img, image_caption = generate_image_caption(bug_image)
    st.image(img, caption=bug_image.name, width=300)
    st.success("Screenshot processed!")

# -- Generate bug report -- #
gen_btn = st.button("Generate Bug", key="gen")
if gen_btn:
    if not bug_desc.strip():
        st.error("Please describe the bug first.")
    else:
        prompt = (
            "You are a helpful assistant that formats bug reports as JSON.\n"
            "Generate a JSON object with fields: title, description, steps (array), expected, actual.\n"
            f"Bug description:\n{bug_desc}\n"
        )
        if image_caption:
            prompt += f"\nScreenshot context: {image_caption}\n"
        prompt += "\nRespond *only* with the JSON object."

        with st.spinner("Generating bug report…"):
            try:
                if selected_model.startswith("gpt-"):
                    # OpenAI
                    raw = call_openai_model(selected_model, prompt, openai_key)
                elif "gemini" in selected_model:
                    # Gemini (Google)
                    raw = call_gemini_model(selected_model, prompt, gemini_key)
                else:
                    raise ValueError("Unknown model selected")
                bug = parse_bug_json(raw)
                st.session_state.bug = bug
                st.session_state.jira_feedback = None
                st.success("✅ Bug report generated! You can now edit it below before sending to Jira.")
            except Exception as e:
                st.error(f"Failed to generate or parse bug report: {e}")
                st.code(locals().get("raw", ""), language="json")

# -- Edit & Approve -- #
bug = st.session_state.bug
if bug:
    st.markdown("## Edit & Approve Bug Report")
    bug["title"] = st.text_input("Title", bug["title"])
    bug["description"] = st.text_area("Description", bug["description"])
    steps_str = st.text_area("Steps to Reproduce (one per line)", "\n".join(bug["steps"]))
    bug["steps"] = [s.strip() for s in steps_str.splitlines() if s.strip()]
    bug["expected"] = st.text_area("Expected Result", bug["expected"])
    bug["actual"] = st.text_area("Actual Result", bug["actual"])

    create_jira = st.button("Create in JIRA", key="create_jira")
    if create_jira:
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
            payload = build_jira_payload(bug, jira_proj, environment, fix_versions)
            with st.spinner("Creating issue in JIRA…"):
                resp = send_jira_issue(jira_url, jira_email, jira_token, payload)
            if resp.status_code == 201:
                key = resp.json().get("key")
                st.session_state.jira_feedback = ("success", key)
            else:
                st.session_state.jira_feedback = ("error", resp.status_code, resp.text)

    # Show feedback
    fb = st.session_state.jira_feedback
    if fb:
        if fb[0] == "success":
            st.success(f"✅ Issue created: {fb[1]}")
            st.markdown(f"[View in JIRA]({jira_url.rstrip('/')}/browse/{fb[1]})")
        else:
            st.error(f"❌ Jira API Error {fb[1]}:\n{fb[2]}")
