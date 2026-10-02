import os
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ServiceUnavailable

# 1. API Configuration
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Please configure your GEMINI_API_KEY in secrets or environment.")
    st.stop()

genai.configure(api_key=API_KEY)
# Using gemini-1.5-flash prevents 503 traffic overloads
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("AI Flashcard Generator")
notes = st.text_area("Paste your study notes:", height=180)
num_cards = st.slider("Number of flashcards", min_value=1, max_value=10, value=5)

if st.button("Generate Flashcards"):
    if not notes.strip():
        st.warning("Please enter some notes first.")
    else:
        prompt = f"""
        Create exactly {num_cards} flashcards from the following notes.
        Format strictly as:
        Q: [Question]
        A: [Answer]
        ---
        Notes:
        {notes}
        """
        with st.spinner("Generating flashcards..."):
            try:
                response = model.generate_content(prompt)
                cards = response.text.split("---")
                for card in cards:
                    if card.strip():
                        st.info(card.strip())
            except ServiceUnavailable:
                st.error("Server is temporarily busy. Please wait 10 seconds and click Generate again.")
            except Exception as e:
                st.error(f"Error: {e}")
