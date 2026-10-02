import os
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted

# 1. API Configuration
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 2. Dynamic Model Discovery (Eliminates 404 errors)
@st.cache_data(ttl=600)
def get_supported_models():
    try:
        models = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        return models
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []

available_models = get_supported_models()

if not available_models:
    st.error("No text generation models found for this API key. Verify key permissions in Google AI Studio.")
    st.stop()

# Auto-select the first Flash model (Flash has free tier quota)
default_idx = 0
for idx, name in enumerate(available_models):
    if "flash" in name.lower():
        default_idx = idx
        break

# 3. User Interface
st.title("AI Flashcard Generator")

selected_model = st.selectbox(
    "Active Model (automatically detected from your key):",
    available_models,
    index=default_idx
)
model = genai.GenerativeModel(selected_model)

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
        with st.spinner(f"Generating flashcards using {selected_model}..."):
            try:
                response = model.generate_content(prompt)
                cards = response.text.split("---")
                for card in cards:
                    if card.strip():
                        st.info(card.strip())
            except ResourceExhausted:
                st.error("Free quota limit reached for this specific model. Pick another Flash model from the dropdown above.")
            except ServiceUnavailable:
                st.error("Google's servers are temporarily busy. Please retry in a few seconds.")
            except Exception as e:
                st.error(f"Error: {e}")
