import os
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ServiceUnavailable

# 1. API Configuration
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# Active working model
model = genai.GenerativeModel("gemini-flash-latest")

# 2. UI Layout
st.set_page_config(page_title="AI Flashcard Generator", page_icon="🎴", layout="centered")
st.title("🎴 AI Flashcard Generator")
st.caption("Generate study cards instantly from your notes using Gemini.")

notes = st.text_area("Paste your study notes:", height=200, placeholder="Paste lecture notes or concepts here...")
num_cards = st.slider("Number of flashcards", min_value=1, max_value=10, value=5)

if st.button("Generate Flashcards", type="primary"):
    if not notes.strip():
        st.warning("Please enter some study notes first.")
    else:
        prompt = f"""
        Extract key concepts from these notes and generate exactly {num_cards} study flashcards.
        Format each card strictly as:
        Q: [Concise question]
        A: [Clear, accurate answer]
        ---
        Notes:
        {notes}
        """
        with st.spinner("Generating flashcards..."):
            try:
                response = model.generate_content(prompt)
                raw_cards = response.text.split("---")
                
                valid_cards = [c.strip() for c in raw_cards if c.strip() and "Q:" in c]
                
                if valid_cards:
                    st.success(f"Generated {len(valid_cards)} flashcards!")
                    for idx, card in enumerate(valid_cards, 1):
                        with st.expander(f"Card {idx}", expanded=True):
                            lines = card.split("\n")
                            q = next((l.replace("Q:", "").strip() for l in lines if l.startswith("Q:")), "")
                            a = next((l.replace("A:", "").strip() for l in lines if l.startswith("A:")), "")
                            st.markdown(f"**Question:** {q}")
                            st.markdown(f"**Answer:** {a}")
                else:
                    st.write(response.text)
                    
            except ServiceUnavailable:
                st.error("Google AI service is momentarily busy. Please try again in 10 seconds.")
            except Exception as e:
                st.error(f"Error: {e}")
