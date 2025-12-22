import streamlit as st

st.title("Lucas Page")
st.write("Welcome to Lucase's page — a simple placeholder.")

msg = st.text_input("Message to Lucase")
if st.button("Send"):
    if msg:
        st.success(f"Lucase received: {msg}")
    else:
        st.info("Type a message first")
