"""
Primary Math Practice Module
Provides math practice with LLM-generated questions tailored to primary levels.
Users can select difficulty level and practice 10 questions.
"""

import streamlit as st
import os
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





def show(user: str = "ella"):
    """
    Main function to display the math practice page.
    
    Args:
        user: The user name/profile (e.g., "ella", "lucas", "meimei")
    """
    # ------------------- Session State -------------------
    if "primary_math_level" not in st.session_state:
        st.session_state.primary_math_level = "P2"
    if "primary_math_questions" not in st.session_state:
        st.session_state.primary_math_questions = []
    if "primary_math_answers" not in st.session_state:
        st.session_state.primary_math_answers = []
    if "primary_math_completed" not in st.session_state:
        st.session_state.primary_math_completed = False
    if "primary_math_reward_unlocked" not in st.session_state:
        st.session_state.primary_math_reward_unlocked = False

    user_upper = user.upper()

    # ------------------- Sidebar Navigation -------------------
    st.sidebar.header(f"👤 {user_upper}'s Math Practice")

    # Level selection
    selected_level = st.sidebar.selectbox(
        "📚 Select Level:",
        LEVELS,
        index=LEVELS.index(st.session_state.primary_math_level),
        format_func=lambda x: LEVEL_DESCRIPTIONS.get(x, x)
    )

    if selected_level != st.session_state.primary_math_level:
        st.session_state.primary_math_level = selected_level
        st.session_state.primary_math_questions = []
        st.session_state.primary_math_answers = []
        st.session_state.primary_math_completed = False
        st.rerun()



    # ------------------- Main Content -------------------
    st.title(f"🧮 {user_upper}'s {st.session_state.primary_math_level} Math Practice")
    st.caption(LEVEL_DESCRIPTIONS.get(st.session_state.primary_math_level, ""))

    # Generate questions if not already done
    if not st.session_state.primary_math_questions:
        with st.spinner(f"Generating {st.session_state.primary_math_level} level questions..."):
            llm = get_llm_helper_instance()
            if llm:
                try:
                    questions = llm.generate_math_questions(st.session_state.primary_math_level, count=10)
                    st.session_state.primary_math_questions = questions
                    st.session_state.primary_math_answers = [""] * len(questions)
                except Exception as e:
                    st.error(f"Error generating questions: {e}")
                    return
            else:
                st.error("LLM Helper not available")
                return

    # Display questions
    st.subheader("Solve these 10 questions:")
    for i, (q, correct_ans) in enumerate(st.session_state.primary_math_questions):
        if not st.session_state.primary_math_completed:
            st.session_state.primary_math_answers[i] = st.text_input(
                f"Q{i+1}: {q}",
                value=st.session_state.primary_math_answers[i],
                key=f"ans_{i}"
            )

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
            st.write(f"Q{i+1}: {q} → {ua} {symbol}")
            
            if is_correct:
                score += 1
            
            results.append({"q": q, "ans": ua, "correct": correct})

        st.success(f"🎉 You got {score}/10 correct!")
        st.session_state.primary_math_completed = True

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
