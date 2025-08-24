import streamlit as st
import random
import datetime
import json
import os

HISTORY_FILE = "history.json"

# ---- Helpers ----
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def generate_question():
    q_type = random.choice(["add_sub", "mul"])
    if q_type == "add_sub":
        # create chain like 12+58-32
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

# Sidebar calendar
history = load_history()
dates_done = list(history.keys())
selected_date = st.sidebar.date_input("📅 Pick a date to view history:")

if str(selected_date) in history:
    st.sidebar.write("✅ Completed")
else:
    st.sidebar.write("❌ Not completed")

# Show historical record if viewing past date
if str(selected_date) in history:
    st.header(f"Results on {selected_date}")
    for i, record in enumerate(history[str(selected_date)], 1):
        st.write(f"Q{i}: {record['q']} → Your answer: {record['ans']} | Correct: {record['correct']}")
    st.stop()


# Generate 10 questions
if "questions" not in st.session_state:
    st.session_state.questions = [generate_question() for _ in range(10)]
    st.session_state.answers = [""] * 10
    st.session_state.completed = False

questions = st.session_state.questions

st.subheader("Solve these 10 questions:")

for i, (q, ans) in enumerate(questions):
    st.session_state.answers[i] = st.text_input(f"Q{i+1}: {q} =", st.session_state.answers[i])

if st.button("Submit answers"):
    results = []
    score = 0
    for (q, correct), user_ans in zip(questions, st.session_state.answers):
        try:
            ua = int(user_ans)
        except:
            ua = None
        is_correct = (ua == correct)
        if is_correct: score += 1
        results.append({"q": q, "ans": ua, "correct": correct})

    st.success(f"🎉 You got {score}/10 correct!")

    # Save into history under today
    today = str(datetime.date.today())
    history[today] = results
    save_history(history)

    # Reset for new session
    st.session_state.completed = True