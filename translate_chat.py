import streamlit as st

st.title("Translate Chat")
st.write("Authorized access — simple translate/chat placeholder.")

txt = st.text_area("Enter text to translate")
if st.button("Translate"):
    if txt:
        # placeholder translation: reverse the text
        st.success("Translated result:")
        st.write(txt[::-1])
    else:
        st.info("Enter some text first")
