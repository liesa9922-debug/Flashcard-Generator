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

# 2. Dynamic Model Selection (Finds whatever model works with your key/SDK)
@st.cache_resource
def get_working_model():
    try:
        available_models = [
            m.name for m in genai.list_models() 
            if "generateContent" in m.supported_generation_methods
        ]
        # Prefer flash, fallback to pro or first available
        for preferred in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]:
            for m in available_models:
                if preferred in m:
                    return genai.GenerativeModel(m)
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"Failed to fetch models: {e}")
    return genai.GenerativeModel("gemini-1.5-flash")

model = get_working_model()

# 3. Streamlit UI
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
                st.error("Server is busy right now. Please wait 10 seconds and try again.")
            except Exception as e:
                st.error(f"Generation error: {e}")
