import streamlit as st
import random
import datetime
import json
import os

HISTORY_FILE = "history.json"

# ---- Helpers ----
def load_history():
    """Load history from JSON, reset if empty/corrupted."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_history(history):
    """Save history into JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def generate_question():
    """Generate either add/sub or simple multiplication question."""
    q_type = random.choice(["add_sub", "mul"])
    if q_type == "add_sub":
        a, b, c = random.randint(1, 60), random.randint(1, 60), random.randint(1, 60)
        expr = f"{a} + {b} - {c}"
        answer = a + b - c
    else:  # multiplication
        a, b = random.randint(2, 9), random.randint(2, 9)
        expr = f"{a} × {b}"
        answer = a * b
    return expr, answer


# ---- UI ----
st.title("🧮 Primary 1 Math Practice")

# Load history
history = load_history()

# Sidebar calendar
st.sidebar.header("📅 Progress Tracker")
selected_date = st.sidebar.date_input("Pick a date to view history:")

if str(selected_date) in history:
    st.sidebar.success("✅ Completed")
else:
    st.sidebar.warning("❌ Not completed")

# Show historical record if viewing past date
if str(selected_date) in history:
    st.header(f"Results on {selected_date}")
    for i, record in enumerate(history[str(selected_date)], 1):
        st.write(
            f"Q{i}: {record['q']} → Your answer: {record['ans']} | Correct: {record['correct']}"
        )
    st.stop()


# ---- Practice Session ----
if "questions" not in st.session_state or st.button("🔄 New Set"):
    st.session_state.questions = [generate_question() for _ in range(10)]
    st.session_state.answers = [""] * 10
    st.session_state.completed = False

questions = st.session_state.questions

st.subheader("Solve these 10 questions:")

for i, (q, ans) in enumerate(questions):
    st.session_state.answers[i] = st.text_input(
        f"Q{i+1}: {q} =", st.session_state.answers[i]
    )

if st.button("✅ Submit answers"):
    results = []
    score = 0
    for (q, correct), user_ans in zip(questions, st.session_state.answers):
        try:
            ua = int(user_ans)
        except:
            ua = None
        is_correct = (ua == correct)
        if is_correct:
            score += 1
        results.append({"q": q, "ans": ua, "correct": correct})

    st.success(f"🎉 You got {score}/10 correct!")

    # Save into history under today
    today = str(datetime.date.today())
    history[today] = results
    save_history(history)

    st.session_state.completed = True