import streamlit as st
import json
import os

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

# ------------------- Page Selection -------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Build available pages. Home is the front page with buttons.
pages = ["Home", "Ella", "Meimei", "Lucas", "Translate Chat"]

# Preserve the last selected page 
current_page = st.session_state.get("page", "Home")
try:
    default_index = pages.index(current_page)
    is_valid_page = True
except ValueError:
    # Current page not in radio options
    default_index = 0
    is_valid_page = False

selected = st.sidebar.radio("📚 Pages", pages, index=default_index)

# Only update page from radio if we were on a valid page
if is_valid_page:
    st.session_state.page = selected

page = st.session_state.page

# ------------------- Home / Front Page -------------------
if page == "Home":
    st.title("Welcome")
    st.write("Choose a profile to continue:")

    # passwords for protected profiles; required value is '1314'
    SECRET_PW = "1314"

    # First row: Ella, Meimei, Lucas
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👧 Ella"):
            st.session_state.page = "Ella"
            st.rerun()
    with c2:
        if st.button("🧒 Meimei"):
            st.session_state.page = "Meimei"
            st.rerun()
    with c3:
        if st.button("🧑‍🎓 Lucas"):
            st.session_state.page = "Lucas"
            st.rerun()

    # Second row: David, Mika, Wai Wai (all use Translate Chat)
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🕵️ David"):
            st.session_state.page = "Translate Chat"
            st.rerun()
    with c5:
        if st.button("🎧 Mika"):
            st.session_state.page = "Translate Chat"
            st.rerun()
    with c6:
        if st.button("🎨 Wai Wai"):
            st.session_state.page = "Translate Chat"
            st.rerun()

# ------------------- Practice Pages -------------------

# Ella page
if page == "Ella":
    try:
        import primary_math
        primary_math.show(user="ella")
    except Exception as e:
        st.error(f"Failed to load Ella page: {e}")
    st.stop()

# Meimei page
if page == "Meimei":
    try:
        import primary_math
        primary_math.show(user="meimei")
    except Exception as e:
        st.error(f"Failed to load Meimei page: {e}")
    st.stop()

# Lucas page
if page == "Lucas":
    try:
        import primary_math
        primary_math.show(user="lucas")
    except Exception as e:
        st.error(f"Failed to load Lucas page: {e}")
    st.stop()

# ------------------- Translate Chat page (load module) -------------------
if page == "Translate Chat":
    try:
        import translate_chat
        # translate_chat is import-safe and exposes a `main()` function
        # that must be called to render the page (it does not render on import).
        translate_chat.main()
    except Exception as e:
        st.error(f"Failed to load Translate Chat page: {e}")
        st.exception(e)
    st.stop()


