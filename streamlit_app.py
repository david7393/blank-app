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
pages = ["Math Practice"]
if st.session_state.get("reward_unlocked", False):
    pages.append("Reward Game")

page = st.sidebar.radio("📚 Pages", pages)

# ------------------- Math Practice -------------------
if page == "Math Practice":
    st.title("🧮 Primary 1 Math Practice")

    # Sidebar calendar
    st.sidebar.header("📅 Progress Tracker")
    selected_date = st.sidebar.date_input("Pick a date to view history:")
    if str(selected_date) in history:
        st.sidebar.success("✅ Completed")
    else:
        st.sidebar.warning("❌ Not completed")

    # Show historical record
    if str(selected_date) in history:
        st.header(f"Results on {selected_date}")
        for i, record in enumerate(history[str(selected_date)], 1):
            symbol = "✅" if record["ans"] == record["correct"] else "❌"
            st.write(f"Q{i}: {record['q']} → Your answer: {record['ans']} {symbol}")
        st.stop()

    st.subheader("Solve these 10 questions:")

    for i, (q, ans) in enumerate(st.session_state.questions):
        if not st.session_state.completed:
            st.session_state.answers[i] = st.text_input(f"Q{i+1}: {q} =", st.session_state.answers[i])

    if st.button("✅ Submit answers") and not st.session_state.completed:
        results = []
        score = 0
        st.subheader("✅ Results:")
        for i, ((q, correct), user_ans) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
            try:
                ua = int(user_ans)
            except:
                ua = None
            is_correct = (ua == correct)
            symbol = "✅" if is_correct else f"❌ (Correct: {correct})"
            st.write(f"Q{i+1}: {q} → {ua} {symbol}")
            if is_correct:
                score += 1
            results.append({"q": q, "ans": ua, "correct": correct})

        st.success(f"🎉 You got {score}/10 correct!")

        # Save history
        today = str(datetime.date.today())
        history[today] = results
        save_history(history)
        st.session_state.completed = True

        # Unlock reward if perfect score
        if score == 10:
            st.session_state.reward_unlocked = True
            st.success("🎁 Perfect score! Reward game unlocked!")
            st.stop()  # Force rerun to show Reward Game page

# ------------------- Reward Game -------------------
elif page == "Reward Game":
    snake_game()
