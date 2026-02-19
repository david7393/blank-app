"""
Primary Math Practice Module
Provides math practice with LLM-generated questions tailored to primary levels.
Users can select difficulty level and practice 10 questions.
"""

import streamlit as st
import os
import json
from datetime import datetime
from llm_helper import get_llm_helper
from snake_game import snake_game

LEVELS = ["P1", "P2", "P3", "P4", "P5", "P6", "PLSE"]
LEVEL_DESCRIPTIONS = {
    "P1": "Primary 1 (Ages 6-7) - Addition, Subtraction, Simple Multiplication",
    "P2": "Primary 2 (Ages 7-8) - Operations within 100, Multiplication & Division",
    "P3": "Primary 3 (Ages 8-9) - Operations within 1000, Fractions",
    "P4": "Primary 4 (Ages 9-10) - Multi-digit, Decimals, Geometry",
    "P5": "Primary 5 (Ages 10-11) - Fractions, Decimals, Percentages, Algebra",
    "P6": "Primary 6 (Ages 11-12) - Advanced Algebra, Geometry, Statistics",
    "PLSE": "Pre-Lower Secondary Exam - Comprehensive Exam Preparation",
}

HISTORY_FILE = "history.json"


# ------------------- Helpers -------------------


def get_llm_helper_instance():
    """Get or create LLM Helper instance."""
    if 'llm_helper' not in st.session_state:
        try:
            import streamlit as st_inner
            api_key = (
                st_inner.secrets.get("OPENROUTER_API_KEY", None) if hasattr(st_inner, "secrets") else None
            ) or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
            st.session_state.llm_helper = get_llm_helper(api_key)
        except Exception as e:
            st.error(f"Failed to initialize LLM Helper: {e}")
            return None
    return st.session_state.llm_helper


def load_user_history(user: str):
    """Load history for a specific user."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                all_history = json.load(f)
                # Convert old format to new format if needed
                if isinstance(all_history, dict) and not any(k.startswith(user) for k in all_history.keys()):
                    # Old format without user prefix, assume it's for current user
                    return {k: v for k, v in all_history.items() if len(v) > 0} if all_history else {}
                # New format with user prefix
                return {k: v for k, v in all_history.items() if k.startswith(f"{user}_")} if all_history else {}
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def save_practice_result(user: str, level: str, results: list, score: int):
    """Save practice results to history."""
    try:
        with open(HISTORY_FILE, "r") as f:
            all_history = json.load(f)
    except:
        all_history = {}
    
    # Create key with user and date
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{user}_{level}_{today}"
    
    all_history[key] = {
        "user": user,
        "level": level,
        "score": score,
        "total": len(results),
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_history, f, indent=2)


def get_calendar_stats(user: str) -> dict:
    """Get practice stats for calendar display."""
    history = load_user_history(user)
    stats = {}
    
    for key, value in history.items():
        if isinstance(value, dict) and "timestamp" in value:
            date = value.get("timestamp", "").split("T")[0]
            if date not in stats:
                stats[date] = {"count": 0, "total_score": 0, "total_questions": 0}
            stats[date]["count"] += 1
            stats[date]["total_score"] += value.get("score", 0)
            stats[date]["total_questions"] += value.get("total", 10)
    
    return stats





def show(user: str = "ella"):
    """
    Main function to display the math practice page.
    
    Args:
        user: The user name/profile (e.g., "ella", "lucas", "meimei")
    """
    # ------------------- Session State -------------------
    if "primary_math_level" not in st.session_state:
        st.session_state.primary_math_level = None  # No default, user must select
    if "primary_math_questions" not in st.session_state:
        st.session_state.primary_math_questions = []
    if "primary_math_answers" not in st.session_state:
        st.session_state.primary_math_answers = []
    if "primary_math_completed" not in st.session_state:
        st.session_state.primary_math_completed = False
    if "primary_math_reward_unlocked" not in st.session_state:
        st.session_state.primary_math_reward_unlocked = False
    if "primary_math_current_user" not in st.session_state:
        st.session_state.primary_math_current_user = user

    user_upper = user.upper()

    # ------------------- Sidebar Navigation -------------------
    st.sidebar.header(f"👤 {user_upper}'s Math Practice")

    # Calendar/History section
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Practice History")
    calendar_stats = get_calendar_stats(user)
    if calendar_stats:
        for date in sorted(calendar_stats.keys(), reverse=True)[:7]:  # Last 7 days
            stats = calendar_stats[date]
            score_pct = (stats["total_score"] / stats["total_questions"] * 100) if stats["total_questions"] > 0 else 0
            st.sidebar.write(f"**{date}**: {stats['total_score']}/{stats['total_questions']} ✓ ({score_pct:.0f}%)")
    else:
        st.sidebar.write("No practice history yet")

    # ------------------- Main Content -------------------
    # Level selection moved to main page
    st.title(f"🧮 {user_upper}'s Math Practice")

    if st.session_state.primary_math_level is None:
        st.info("📚 Please select a level below to start practice")
    # Present selectbox on main page
    selected_level = st.selectbox(
        "📚 Select Level:",
        LEVELS,
        index=(LEVELS.index(st.session_state.primary_math_level) if st.session_state.primary_math_level in LEVELS else 0),
        format_func=lambda x: LEVEL_DESCRIPTIONS.get(x, x),
        key="level_select_main"
    )

    if selected_level != st.session_state.primary_math_level:
        st.session_state.primary_math_level = selected_level
        st.session_state.primary_math_questions = []
        st.session_state.primary_math_answers = []
        st.session_state.primary_math_completed = False
        st.experimental_rerun()

    st.title(f"🧮 {user_upper}'s {st.session_state.primary_math_level} Math Practice")
    st.caption(LEVEL_DESCRIPTIONS.get(st.session_state.primary_math_level, ""))

    # Question style selection and explicit generation button moved to main page
    st.markdown("---")
    st.subheader("🧭 Question Options")
    question_style = st.radio(
        "Question style:",
        ["Balanced (Mixed)", "Mostly Word Problems", "Mostly Calculations", "More Puzzles"],
        index=0,
        help="Choose the kind of questions to generate for this practice session."
    )

    count = st.number_input("Number of questions:", min_value=1, max_value=20, value=10)

    if not st.session_state.primary_math_questions:
        if st.button("🧩 Generate questions"):
            with st.spinner(f"Generating {st.session_state.primary_math_level} level questions..."):
                llm = get_llm_helper_instance()
                if llm:
                    try:
                        # Use faster generation settings when possible
                        questions = llm.generate_math_questions(
                            st.session_state.primary_math_level,
                            count=int(count),
                            style=question_style,
                            fast=True,
                        )
                        st.session_state.primary_math_questions = questions
                        st.session_state.primary_math_answers = [""] * len(questions)
                    except Exception as e:
                        st.error(f"Error generating questions: {e}")
                        return
                else:
                    st.error("LLM Helper not available")
                    return
        else:
            st.info("Click 'Generate questions' to request questions from the LLM.")
            return

    # Display questions with better layout
    st.subheader("📝 Solve these 10 questions:")
    st.write("Enter your answers below:")
    
    for i, (q, correct_ans) in enumerate(st.session_state.primary_math_questions):
        if not st.session_state.primary_math_completed:
            # Better layout for questions with larger text
            st.write(f"### Q{i+1}: {q}")
            st.session_state.primary_math_answers[i] = st.text_input(
                "Answer:",
                value=st.session_state.primary_math_answers[i],
                key=f"ans_{i}",
                label_visibility="collapsed"
            )
            st.write("")  # Add spacing between questions
        else:
            st.write(f"**Q{i+1}: {q}**")

    # Submit button
    if st.button("✅ Submit answers", disabled=st.session_state.primary_math_completed):
        results = []
        score = 0
        
        st.subheader("✅ Results:")
        for i, ((q, correct), user_ans) in enumerate(
            zip(st.session_state.primary_math_questions, st.session_state.primary_math_answers)
        ):
            try:
                ua = float(user_ans) if user_ans else None
            except (ValueError, TypeError):
                ua = None
            
            is_correct = (ua == correct)
            symbol = "✅" if is_correct else f"❌ (Correct: {correct})"
            st.write(f"**Q{i+1}**: {q} → {ua} {symbol}")
            
            if is_correct:
                score += 1
            
            results.append({"q": q, "ans": ua, "correct": correct})

        st.success(f"🎉 You got {score}/10 correct!")
        st.session_state.primary_math_completed = True
        
        # Save results to history
        save_practice_result(user, st.session_state.primary_math_level, results, score)

        # Unlock reward if perfect score
        if score == 10:
            st.session_state.primary_math_reward_unlocked = True
            st.success("🎁 Perfect score! Reward game unlocked! Play snake game below:")
            # Show snake game directly
            st.markdown("---")
            snake_game()

    # Show reward game if already unlocked
    if st.session_state.primary_math_reward_unlocked and st.session_state.primary_math_completed:
        if st.button("🎮 Play Reward Game"):
            st.markdown("---")
            snake_game()


if __name__ == "__main__":
    show()
