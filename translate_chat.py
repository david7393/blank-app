import requests
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# NOTE: Do not import `streamlit` or access `st.secrets` at module import time.
# This file is now import-safe: Streamlit is imported inside `main()`.

import json
import json
# ============================================
# CONFIGURATION - MODIFY THESE VALUES!
# NOTE: Secrets are resolved at runtime inside `main()` so this module
# can be safely imported by non-Streamlit tools (tests, linters, etc.).
# ============================================

# Values will be populated at runtime; keep safe defaults here.
DEEPSEEK_API_KEY: Optional[str] = None
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
# DEEPSEEK TRANSLATOR
# ============================================

class DeepSeekTranslator:
    """DeepSeek API translator"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.last_status: Optional[int] = None
        self.last_response_text: Optional[str] = None
    
    def translate_to_english(self, text: str) -> str:
        """Translate text to English"""
        return self._call_api(text, "Translate this to English:")
    
    def translate_to_myanmar(self, text: str) -> str:
        """Translate text to Myanmar (Burmese)"""
        return self._call_api(text, "Translate this to Myanmar (Burmese) language:")
    
    def _call_api(self, text: str, instruction: str) -> str:
        """Call DeepSeek API"""
        try:
            prompt = f"{instruction}\n\n{text}\n\nOnly provide the translation, no explanations."
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=data,
                timeout=30
            )

            # Save status/body for debugging
            self.last_status = response.status_code
            try:
                self.last_response_text = response.text
            except Exception:
                self.last_response_text = None

            if response.status_code != 200:
                body = self.last_response_text or ""
                snippet = body[:400].replace('\n', ' ')
                return f"Translation error: HTTP {response.status_code} - {snippet}"

            try:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                return translated_text
            except Exception as e:
                # JSON parse / unexpected structure
                return f"Translation error: invalid response format ({e})"

        except Exception as e:
            return f"Translation error: {e}"

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

    # Simple interface
    st.title("Translate Chat")
    st.write("Authorized access — multilingual translation with chat history.")

    # Resolve secrets from Streamlit config or environment variables.
    # Use item access on `st.secrets` first (works on Streamlit Cloud),
    # then fall back to environment variables.
    try:
        try:
            deepseek_key = st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            deepseek_key = os.environ.get("DEEPSEEK_API_KEY")

        try:
            github_token = st.secrets["GITHUB_TOKEN"]
        except Exception:
            github_token = os.environ.get("GITHUB_TOKEN")

        try:
            gist_id = st.secrets["GITHUB_GIST_ID"]
        except Exception:
            gist_id = os.environ.get("GITHUB_GIST_ID")

        # Basic validation to ensure keys were configured
        # Show a minimal, non-sensitive debug banner indicating presence of secrets
        secrets_status = {
            "DEEPSEEK_API_KEY": bool(deepseek_key),
            "GITHUB_TOKEN": bool(github_token),
            "GITHUB_GIST_ID": bool(gist_id),
        }

        st.write("**Secrets status (presence only):**")
        cols = st.columns(len(secrets_status))
        for col, (name, present) in zip(cols, secrets_status.items()):
            col.write(f"{ '✅' if present else '❌' } {name}")

        missing = [name for name, val in secrets_status.items() if not val]

        if missing:
            st.warning(f"⚠️ Missing secrets: {', '.join(missing)}. Configure via Streamlit secrets or environment variables.")
            st.stop()

        # Initialize components (store instances in session state)
        if 'storage' not in st.session_state:
            st.session_state.storage = GitHubGistStorage(gist_id, github_token)
            st.session_state.chat_history = st.session_state.storage.load()

        if 'translator' not in st.session_state:
            st.session_state.translator = DeepSeekTranslator(deepseek_key)

        # Indicate app initialized (non-sensitive)
        st.write("App initialized — ready")

    except Exception as _e:
        st.error("An error occurred during app initialization — check details below.")
        st.exception(_e)
        return

    # Initialize components (store instances in session state)
    if 'storage' not in st.session_state:
        st.session_state.storage = GitHubGistStorage(gist_id, github_token)
        st.session_state.chat_history = st.session_state.storage.load()

    if 'translator' not in st.session_state:
        st.session_state.translator = DeepSeekTranslator(deepseek_key)

    # Main input area
    txt = st.text_area("Enter text to translate")

    if st.button("Translate"):
        if txt:
            with st.spinner("Translating..."):
                # Get translations
                english_text = st.session_state.translator.translate_to_english(txt)
                myanmar_text = st.session_state.translator.translate_to_myanmar(txt)

                # Create chat history entry
                new_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "original": txt,
                    "english": english_text,
                    "myanmar": myanmar_text
                }

                # Add to history and save
                st.session_state.chat_history.append(new_entry)
                st.session_state.storage.save(st.session_state.chat_history)

                # Display results
                st.success("Translated result:")

                # Show both translations
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**English:**")
                    st.write(english_text)
                with col2:
                    st.write("**Myanmar:**")
                    st.write(myanmar_text)
                # If there was an error, show debug info from the translator
                if isinstance(st.session_state.translator, DeepSeekTranslator):
                    if (isinstance(english_text, str) and english_text.startswith("Translation error")) or (
                        isinstance(myanmar_text, str) and myanmar_text.startswith("Translation error")):
                        with st.expander("Debug: DeepSeek HTTP response (no secrets)"):
                            st.write(f"HTTP status: {st.session_state.translator.last_status}")
                            st.text(st.session_state.translator.last_response_text or "<no response body>")
        else:
            st.info("Enter some text first")

    # Chat history display
    st.divider()
    st.write("### Chat History")

    if st.session_state.chat_history:
        # Show last 100 items
        for entry in reversed(st.session_state.chat_history[-100:]):
            with st.expander(f"{entry['timestamp']} - {entry['original'][:50]}..."):
                st.write(f"**Original:** {entry['original']}")
                st.write(f"**English:** {entry['english']}")
                st.write(f"**Myanmar:** {entry['myanmar']}")
    else:
        st.write("No chat history yet. Start translating!")

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    main()