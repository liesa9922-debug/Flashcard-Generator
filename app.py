
import streamlit as st
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from google import genai

# Load API keys
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🧠",
    layout="centered"
)

# Header
st.title("🧠 AI Flashcard Generator")
st.subheader("Learn Smarter with Artificial Intelligence")

st.write(
    "Transform your study notes into interactive flashcards "
    "using OpenAI or Google Gemini."
)

st.divider()

# AI Provider
provider = st.selectbox(
    "Choose your AI Model",
    ["OpenAI", "Google Gemini"]
)

# User inputs
topic = st.text_input(
    "Enter your study topic",
    placeholder="Example: Cyber Security"
)

notes = st.text_area(
    "Paste your study notes",
    placeholder="Enter your notes here...",
    height=200
)

number = st.slider(
    "Number of flashcards",
    min_value=3,
    max_value=15,
    value=5
)


# AI Generation Function
def generate_flashcards(provider, topic, notes, number):

    prompt = f"""
    You are an educational flashcard generator.

    Create exactly {number} useful flashcards about {topic}.

    Use these study notes:
    {notes}

    Return ONLY a valid JSON array.
    Do not include markdown or explanations.

    Format:
    [
        {{
            "question": "Question here",
            "answer": "Answer here"
        }}
    ]
    """

    if provider == "OpenAI":

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OpenAI API key is missing in .env")

        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        result = response.output_text

    else:

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Gemini API key is missing in .env")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )

        result = response.text

    # Clean response
    result = result.strip()

    if result.startswith("```"):
        result = result.split("\n", 1)[1]
        result = result.rsplit("```", 1)[0]

    cards = json.loads(result)

    if not isinstance(cards, list) or not cards:
        raise ValueError("The AI returned an invalid flashcard list.")

    for card in cards:
        if not isinstance(card, dict):
            raise ValueError("Invalid flashcard format.")

        if not card.get("question") or not card.get("answer"):
            raise ValueError("A flashcard is missing its question or answer.")

    return cards


# Generate Button
if st.button("✨ Generate Flashcards", use_container_width=True):

    if not topic.strip() or not notes.strip():

        st.warning("Please enter your topic and study notes.")

    else:

        try:

            with st.spinner("AI is preparing your flashcards..."):

                cards = generate_flashcards(
                    provider,
                    topic,
                    notes,
                    number
                )

            st.session_state["cards"] = cards
            st.session_state["index"] = 0
            st.session_state["revealed"] = False

            st.success("Flashcards generated successfully!")

        except Exception as e:

            st.error(f"Generation failed: {e}")


# Display Flashcards
if "cards" in st.session_state:

    cards = st.session_state["cards"]
    index = st.session_state["index"]

    st.divider()

    st.header("📚 Your Flashcards")

    st.progress((index + 1) / len(cards))

    st.caption(
        f"Card {index + 1} of {len(cards)}"
    )

    current_card = cards[index]

    # Question card
    with st.container(border=True):

        st.subheader(f"❓ {current_card['question']}")

        if st.button(
            "👁️ Show Answer",
            use_container_width=True
        ):
            st.session_state["revealed"] = not st.session_state.get(
                "revealed", False
            )

        if st.session_state.get("revealed", False):

            st.success("Answer")

            st.write(current_card["answer"])

    # Navigation
    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⬅ Previous",
            disabled=(index == 0),
            use_container_width=True
        ):

            st.session_state["index"] -= 1
            st.session_state["revealed"] = False
            st.rerun()

    with col2:

        if st.button(
            "Next ➡",
            disabled=(index == len(cards) - 1),
            use_container_width=True
        ):

            st.session_state["index"] += 1
            st.session_state["revealed"] = False
            st.rerun()

    # Download
    st.divider()

    st.download_button(
        "📥 Download All Flashcards",
        data=json.dumps(cards, indent=4, ensure_ascii=False),
        file_name="my_flashcards.json",
        mime="application/json",
        use_container_width=True
    )

    st.success("Happy Learning! 🎓")