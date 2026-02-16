import streamlit as st
import requests
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from llm_helper import get_llm_helper

# NOTE: Do not import `streamlit` or access `st.secrets` at module import time.
# This file is now import-safe: Streamlit is imported inside `main()`.

# ============================================
# CONFIGURATION - MODIFY THESE VALUES!
# NOTE: Secrets are resolved at runtime inside `main()` so this module
# can be safely imported by non-Streamlit tools (tests, linters, etc.).
# ============================================

# Values will be populated at runtime; keep safe defaults here.
OPENROUTER_API_KEY: Optional[str] = None  # Changed from DEEPSEEK_API_KEY
GITHUB_TOKEN: Optional[str] = None
GITHUB_GIST_ID: Optional[str] = None

# App configuration
MAX_HISTORY = 100
GIST_FILENAME = "chat_history.json"

# ============================================
# GITHUB GIST STORAGE MANAGER
# ============================================

class GitHubGistStorage:
    """Storage manager exclusively for GitHub Gist (no local backup)"""
    
    def __init__(self, gist_id: str, github_token: str):
        self.gist_id = gist_id
        self.github_token = github_token
        self.gist_api_url = f"https://api.github.com/gists/{gist_id}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        self.history = []
        
    def load(self) -> List[Dict]:
        """Load chat history from GitHub Gist"""
        try:
            response = requests.get(self.gist_api_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                gist_data = response.json()
                files = gist_data.get('files', {})
                
                # Find JSON file
                for filename, file_info in files.items():
                    if filename == GIST_FILENAME or filename.endswith('.json'):
                        content = file_info.get('content', '[]')
                        self.history = json.loads(content)
                        return self.history[-MAX_HISTORY:]
                # Create initial file if not found
                self._create_initial_gist_file()
                return []
                
            elif response.status_code == 404:
                return []
            elif response.status_code == 401:
                return []
            else:
                return []
                
        except:
            return []
    
    def save(self, history: List[Dict]) -> bool:
        """Save to GitHub Gist"""
        if not history:
            return False
            
        history_to_save = history[-MAX_HISTORY:]
        
        try:
            # Get current Gist information
            response = requests.get(self.gist_api_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return False
                
            gist_data = response.json()
            current_files = gist_data.get('files', {})
            
            # Prepare update data
            history_json = json.dumps(history_to_save, ensure_ascii=False, indent=2)
            
            update_data = {
                "description": f"Chat History - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "files": {
                    GIST_FILENAME: {
                        "content": history_json
                    }
                }
            }
            
            # Preserve other files (if any)
            for filename, file_info in current_files.items():
                if filename != GIST_FILENAME:
                    update_data["files"][filename] = file_info
            
            # Update Gist
            update_response = requests.patch(
                self.gist_api_url,
                headers=self.headers,
                json=update_data,
                timeout=15
            )
            
            if update_response.status_code == 200:
                self.history = history_to_save
                return True
            else:
                return False
                
        except:
            return False
    
    def _create_initial_gist_file(self) -> bool:
        """Create initial file in Gist"""
        try:
            initial_data = {
                "description": "Chat History Storage",
                "files": {
                    GIST_FILENAME: {
                        "content": "[]"
                    }
                }
            }
            
            response = requests.patch(
                self.gist_api_url,
                headers=self.headers,
                json=initial_data,
                timeout=15
            )
            
            return response.status_code == 200
        except:
            return False

# ============================================
# OPENROUTER TRANSLATOR (REPLACES DEEPSEEK TRANSLATOR)
# ============================================

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    # Import Streamlit at runtime so module imports remain safe.
    try:
        import streamlit as st
    except Exception:
        print("Streamlit is not available. `main()` requires Streamlit.")
        return

    try:
        # Resolve secrets from Streamlit config or environment variables.
        # Use a safe accessor for `st.secrets` because Streamlit raises when no secrets file exists.
        def _safe_secret_get(key: str) -> Optional[str]:
            try:
                if hasattr(st, "secrets"):
                    return st.secrets.get(key)
            except Exception:
                # Streamlit may raise StreamlitSecretNotFoundError if no secrets file or dir is present.
                return None
            return None

        # Accept either OPENROUTER_API_KEY (new name) or DEEPSEEK_API_KEY (legacy name)
        openrouter_key = (
            _safe_secret_get("OPENROUTER_API_KEY")
            or _safe_secret_get("DEEPSEEK_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
        )
        github_token = _safe_secret_get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
        gist_id = _safe_secret_get("GITHUB_GIST_ID") or os.environ.get("GITHUB_GIST_ID")

        # Basic validation to ensure keys were configured
        missing = [name for name, val in [("OPENROUTER_API_KEY", openrouter_key), ("GITHUB_TOKEN", github_token), ("GITHUB_GIST_ID", gist_id)] if not val]

        if missing:
            st.error(f"Missing secrets: {', '.join(missing)}. Configure via Streamlit secrets or environment variables.")

            # Show non-sensitive presence checks to help debugging
            with st.expander("Debug: Secret presence (no values shown)"):
                def _presence(key: str):
                    in_secrets = bool(_safe_secret_get(key))
                    in_env = bool(os.environ.get(key))
                    st.write(f"- `{key}` — in Streamlit secrets: {'✅' if in_secrets else '❌'}, in environment: {'✅' if in_env else '❌'}")

                _presence("OPENROUTER_API_KEY")
                _presence("GITHUB_TOKEN")
                _presence("GITHUB_GIST_ID")

                st.write("Tip: After updating Streamlit secrets, rebuild/restart the app to apply changes.")

            st.stop()

        # Initialize components (store instances in session state)
        if 'storage' not in st.session_state:
            st.session_state.storage = GitHubGistStorage(gist_id, github_token)
            st.session_state.chat_history = st.session_state.storage.load()

        if 'llm_helper' not in st.session_state:
            st.session_state.llm_helper = get_llm_helper(openrouter_key)
    except Exception as _e:
        st.error("An error occurred during app initialization — check details below.")
        st.exception(_e)
        return
    
    # User selection
    if 'current_user' not in st.session_state:
        st.session_state.current_user = "Unknown"
    
    st.write("##### Chat Room")
    st.divider()
    
    # Chat history display
    if st.session_state.chat_history:
        # Show last 100 items
        for entry in st.session_state.chat_history[-100:]:
            sender = entry.get('sender', 'Unknown')
            is_current_user = sender == st.session_state.current_user
            
            # Determine alignment
            if is_current_user:
                # Left aligned for current user
                col1, col2 = st.columns([0.3, 0.7])
                with col1:
                    st.markdown(f"<small style='color: gray;'>{sender} • {entry['timestamp']}</small>", unsafe_allow_html=True)
                    st.markdown(f"<small>{entry['english']}</small>", unsafe_allow_html=True)
                    st.markdown(f"<small>{entry['myanmar']}</small>", unsafe_allow_html=True)
            else:
                # Right aligned for others
                col1, col2 = st.columns([0.7, 0.3])
                with col2:
                    st.markdown(f"<small style='color: gray; text-align: right;'>{sender} • {entry['timestamp']}</small>", unsafe_allow_html=True)
                    st.markdown(f"<small style='text-align: right;'>{entry['english']}</small>", unsafe_allow_html=True)
                    st.markdown(f"<small style='text-align: right;'>{entry['myanmar']}</small>", unsafe_allow_html=True)
            
            st.write("")  # Minimal spacing
    else:
        st.write("No chat history yet. Start translating!")
    
    # Show current response if it exists in session state
    if 'current_response' in st.session_state:
        current_entry = st.session_state.current_response
        sender = current_entry.get('sender', 'Unknown')
        is_current_user = sender == st.session_state.current_user
        
        # st.markdown("---")
        st.markdown("##### Current Response")
        
        # Determine alignment - same format as chat history
        if is_current_user:
            # Left aligned for current user
            col1, col2 = st.columns([0.3, 0.7])
            with col1:
                st.markdown(f"<small style='color: gray;'>{sender} • {current_entry['timestamp']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small>{current_entry['english']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small>{current_entry['myanmar']}</small>", unsafe_allow_html=True)
        else:
            # Right aligned for others
            col1, col2 = st.columns([0.7, 0.3])
            with col2:
                st.markdown(f"<small style='color: gray; text-align: right;'>{sender} • {current_entry['timestamp']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small style='text-align: right;'>{current_entry['english']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small style='text-align: right;'>{current_entry['myanmar']}</small>", unsafe_allow_html=True)
    
    st.divider()
    # Main input area
    txt = st.text_area(f"{st.session_state.current_user}: Enter text to send")

    if st.button("Send"):
        if txt:
            with st.spinner("Translating..."):
                # Get translations
                english_text = st.session_state.llm_helper.translate_to_english(txt)
                myanmar_text = st.session_state.llm_helper.translate_to_myanmar(txt)

                # Create chat history entry
                new_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sender": st.session_state.current_user,
                    "original": txt,
                    "english": english_text,
                    "myanmar": myanmar_text
                }

                # Store current response in session state before adding to history
                st.session_state.current_response = new_entry

                # Add to history and save
                st.session_state.chat_history.append(new_entry)
                st.session_state.storage.save(st.session_state.chat_history)

                # Force a rerun to show the current response
                st.rerun()
                    
                # If there was an error, show debug info
                if (isinstance(english_text, str) and english_text.startswith("Translation error")) or (
                    isinstance(myanmar_text, str) and myanmar_text.startswith("Translation error")):
                    with st.expander("Debug: Error Details"):
                        if st.session_state.llm_helper.last_error:
                            st.write(f"Error: {st.session_state.llm_helper.last_error}")
        else:
            st.info("Enter some text first")

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    main()