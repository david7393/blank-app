import streamlit as st
import random
import datetime
import json
import os

from snake_game import snake_game

HISTORY_FILE = "history.json"

# ------------------- Helpers -------------------
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def generate_question():
    """Generate a Primary 1 question with non-negative result."""
    q_type = random.choice(["add_sub", "mul"])
    if q_type == "add_sub":
        while True:
            a, b, c = random.randint(1, 60), random.randint(1, 60), random.randint(1, 60)
            result = a + b - c
            if result >= 0:
                break
        expr = f"{a} + {b} - {c}"
        answer = result
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
        expr = f"{a} × {b}"
        answer = a * b
    return expr, answer

# ------------------- Session State -------------------
if "questions" not in st.session_state:
    st.session_state.questions = [generate_question() for _ in range(10)]
    st.session_state.answers = [""] * 10
    st.session_state.completed = False
    st.session_state.reward_unlocked = False

history = load_history()

# ------------------- Page Selection -------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Build available pages. Home is the front page with buttons.
pages = ["Home", "Practice Page", "Lucas", "Translate Chat", "Ella", "Meimei"]
if st.session_state.get("reward_unlocked", False):
    pages.append("Reward Game")

# Preserve the last selected page 
try:
    default_index = pages.index(st.session_state.get("page", "Home"))
except ValueError:
    default_index = 0

page = st.sidebar.radio("📚 Pages", pages, index=default_index)
st.session_state.page = page

# ------------------- Home / Front Page -------------------
if page == "Home":
    st.title("Welcome")
    st.write("Choose a profile to continue:")

    # passwords for protected profiles; required value is '1314'
    SECRET_PW = "1314"

    # First row: Ella, Meimei, Lucase
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👧 Ella"):
            st.session_state.page = "Ella"
    with c2:
        if st.button("🧒 Meimei"):
            st.session_state.page = "Meimei"
    with c3:
        if st.button("🧑‍🎓 Lucas"):
            st.session_state.page = "Lucas"

    # Second row: David, Mika, Wai Wai
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🕵️ David"):
            st.session_state.pw_prompt = "David"
    with c5:
        if st.button("🎧 Mika"):
            st.session_state.pw_prompt = "Mika"
    with c6:
        if st.button("🎨 Wai Wai"):
            st.session_state.pw_prompt = "Wai Wai"

    # Inline password prompt (replacement for modal)
    pw_prompt = st.session_state.get("pw_prompt")
    if pw_prompt:
        st.markdown(f"**Enter password for {pw_prompt}:**")
        pw_val = st.text_input("Password", type="password", key="pw_input")
        if st.button("Submit Password", key="submit_pw"):
            if pw_val == SECRET_PW:
                st.session_state.page = "Translate Chat"
                # clear prompt
                del st.session_state["pw_prompt"]
            else:
                st.error("Incorrect password")

    # Stop further rendering when on Home
    st.stop()

# ------------------- Practice Page (placeholder) -------------------
if page == "Practice Page":
    st.title("Practice Page")
    st.write("This is an empty practice page placeholder.")
    st.stop()

# ------------------- Lucase page (load module) -------------------
if page == "Lucas":
    try:
        import lucas
    except Exception:
        st.error("Failed to load Lucase page")
    st.stop()

# ------------------- Translate Chat page (load module) -------------------
if page == "Translate Chat":
    try:
        import translate_chat
        # translate_chat is import-safe and exposes a `main()` function
        # that must be called to render the page (it does not render on import).
        translate_chat.main()
    except Exception as e:
        st.error("Failed to load Translate Chat page")
        st.exception(e)
    st.stop()

# ------------------- Ella / Meimei pages (load module) -------------------
if page == "Ella" or page == "Meimei":
    try:
        import ella_math
        # call the page's renderer function
        ella_math.show()
    except Exception:
        st.error("Failed to load Ella/Meimei page")
    st.stop()


