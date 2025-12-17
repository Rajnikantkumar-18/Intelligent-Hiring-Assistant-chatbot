import streamlit as st
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
import os

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Streamlit Configuration
# -----------------------------
st.set_page_config(page_title="TalentScout Hiring Assistant", layout="centered")

# -----------------------------
# Session State Initialization
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict] = []

if "stage" not in st.session_state:
    st.session_state.stage = "greeting"

if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "name": None,
        "email": None,
        "phone": None,
        "experience": None,
        "position": None,
        "location": None,
        "tech_stack": None,
    }

EXIT_KEYWORDS = {"exit", "quit", "bye", "stop"}

# -----------------------------
# Helper Functions
# -----------------------------

def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})


def render_chat():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


def end_conversation():
    add_message(
        "assistant",
        "Thank you for your time! 🙏 Our recruitment team will review your profile and contact you regarding next steps. Have a great day!",
    )
    render_chat()
    st.stop()


def generate_technical_questions(tech_stack: str) -> str:
    system_prompt = """
You are TalentScout, an AI hiring assistant.
Generate 3–5 technical interview questions per technology listed.
Questions should test fundamentals, real-world usage, and problem-solving skills.
Do not provide answers.
Stay strictly within recruitment and technical evaluation context.
"""

    user_prompt = f"""
Candidate Tech Stack:
{tech_stack}

Generate technical interview questions.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content

# -----------------------------
# UI Layout
# -----------------------------
st.title("🤖 TalentScout Hiring Assistant")
render_chat()

user_input = st.chat_input("Type your response here...")

if user_input:
    if user_input.lower().strip() in EXIT_KEYWORDS:
        end_conversation()

    add_message("user", user_input)

    # -----------------------------
    # Conversation Flow Control
    # -----------------------------
    if st.session_state.stage == "greeting":
        add_message(
            "assistant",
            "Hello! Welcome to **TalentScout** 👋\n\nI will guide you through a short initial screening process.",
        )
        add_message("assistant", "Let’s start with your **full name**.")
        st.session_state.stage = "name"

    elif st.session_state.stage == "name":
        st.session_state.candidate["name"] = user_input
        add_message("assistant", "Thanks! Please enter your **email address**.")
        st.session_state.stage = "email"

    elif st.session_state.stage == "email":
        st.session_state.candidate["email"] = user_input
        add_message("assistant", "Great. What is your **phone number**?")
        st.session_state.stage = "phone"

    elif st.session_state.stage == "phone":
        st.session_state.candidate["phone"] = user_input
        add_message("assistant", "How many **years of professional experience** do you have?")
        st.session_state.stage = "experience"

    elif st.session_state.stage == "experience":
        st.session_state.candidate["experience"] = user_input
        add_message("assistant", "What **position(s)** are you applying for?")
        st.session_state.stage = "position"

    elif st.session_state.stage == "position":
        st.session_state.candidate["position"] = user_input
        add_message("assistant", "What is your **current location**?")
        st.session_state.stage = "location"

    elif st.session_state.stage == "location":
        st.session_state.candidate["location"] = user_input
        add_message(
            "assistant",
            "Please list your **tech stack** (comma-separated).\nExample: Python, Django, PostgreSQL, Docker",
        )
        st.session_state.stage = "tech_stack"

    elif st.session_state.stage == "tech_stack":
        st.session_state.candidate["tech_stack"] = user_input
        add_message(
            "assistant",
            "Thanks! Based on your tech stack, here are some technical questions for you:",
        )
        questions = generate_technical_questions(user_input)
        add_message("assistant", questions)
        end_conversation()

    render_chat()
