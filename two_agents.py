import streamlit as st
import openai
import my_prompts
from my_utils import *
import psycopg2
import json
import random
from openai import OpenAI
from datetime import datetime
import pickle
import os

student_model = "meta/llama-2-7b-chat"
embedding_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

library = pickle.load(open('llama-2-7b-chat-library.pkl','rb'))
scenario_embeds = library['scenario_embedding']
guidelines = library['guidelines']

def create_connection():
    return psycopg2.connect(
        dbname=st.secrets["database"]["DB_NAME"],
        user=st.secrets["database"]["DB_USER"],
        password=st.secrets["database"]["DB_PASSWORD"],
        host=st.secrets["database"]["DB_HOST"],
        port=st.secrets["database"]["DB_PORT"],
        sslmode="require"
    )

# --- Clear and reset all state after form submission
def reset_form():
    st.session_state.clear()
    st.experimental_rerun()

# --- Initialize session state
def init_session():
    if "guideline_for_agent_1" not in st.session_state:
        use_guideline_for_agent_1 = random.choice([True, False])
        st.session_state["guideline_for_agent_1"] = use_guideline_for_agent_1
        st.session_state["guideline_for_agent_2"] = not use_guideline_for_agent_1

    st.session_state.setdefault("chat_history_agent_1", [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 1, how can I help you?"}
    ])
    st.session_state.setdefault("chat_history_agent_2", [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 2, how can I help you?"}
    ])
    st.session_state.setdefault("user_input_agent_1", "")
    st.session_state.setdefault("user_input_agent_2", "")
    st.session_state.setdefault("rating_agent_1", 1)
    st.session_state.setdefault("rating_agent_2", 1)
    st.session_state.setdefault("comments", "")
    st.session_state.setdefault("form_submitted", False)

init_session()

openai.api_key = st.secrets["OPENAI_API_KEY"]
st.set_page_config(page_title="LLM Chat Interface", layout="wide")
st.title("Live Chat with Two Customer Service Agents")

# --- UI layout ---
col1, _, col2 = st.columns([1, 0.1, 1])

def render_chat(agent, chat_key, input_key, clear_key):
    with col1 if agent == 1 else col2:
        st.write(f"**Chat with Agent {agent}**")
        for msg in st.session_state[chat_key]:
            role = "You" if msg["role"] == "user" else f"Agent {agent}"
            st.markdown(f"**{role}:** {msg['content']}")

        st.text_input(f"Enter your message to Agent {agent}", key=input_key)
        if st.button(f"Send to Agent {agent}"):
            send_message(
                f"agent_{agent}",
                chat_key,
                input_key,
                st.session_state[f"guideline_for_agent_{agent}"]
            )
            st.rerun()

        st.slider(
            f"Rate Agent {agent} - 1 means very dissatisfied and 5 means very satisfied",
            min_value=1,
            max_value=5,
            key=f"rating_agent_{agent}"
        )

def send_message(agent, chat_key, input_key, use_guideline):
    user_message = st.session_state[input_key]
    if user_message:
        st.session_state[chat_key].append({"role": "user", "content": user_message})
        conversation = [m for m in st.session_state[chat_key] if m["role"] != "system"]
        conv_txt = "\n\n".join([
            f"Customer: {m['content']}" if m["role"] == "user" else f"Agent: {m['content']}"
            for m in conversation
        ])
        best_guideline = get_best_guideline(conv_txt, embedding_client, scenario_embeds, guidelines) if use_guideline else None
        llm_response = gen_agent_response(conv_txt, student_model, client=None, guidelines=best_guideline, temperature=0.3)
        st.session_state[chat_key].append({"role": "assistant", "content": llm_response})

render_chat(1, "chat_history_agent_1", "user_input_agent_1", "clear_input_agent_1")
render_chat(2, "chat_history_agent_2", "user_input_agent_2", "clear_input_agent_2")

st.subheader("Comments about the Agents")
st.text_area("Your comments:", key="comments")
better_agent = st.radio("Which agent do you think performed better?", ("Agent 1", "Agent 2"))

# --- Turn check ---
a1_turns = len([m for m in st.session_state["chat_history_agent_1"] if m["role"] != "user"])
a2_turns = len([m for m in st.session_state["chat_history_agent_2"] if m["role"] != "user"])
min_turns_required = 1
not_enough_turns = a1_turns < min_turns_required or a2_turns < min_turns_required
if not_enough_turns:
    st.warning("Please continue the conversation with both agents until each has at least 4 turns before submitting feedback.")

if st.button("Submit Feedback", disabled=not_enough_turns or st.session_state.get("form_submitted", False)):
    st.session_state["form_submitted"] = True
    conn = create_connection()
    cursor = conn.cursor()
    conv1 = json.dumps([m for m in st.session_state["chat_history_agent_1"] if m["role"] != "system"])
    conv2 = json.dumps([m for m in st.session_state["chat_history_agent_2"] if m["role"] != "system"])
    survey_time = datetime.now()
    agent_1_model = student_model + ("-guidelines" if st.session_state["guideline_for_agent_1"] else "-base")
    agent_2_model = student_model + ("-guidelines" if st.session_state["guideline_for_agent_2"] else "-base")
    cursor.execute("""
        INSERT INTO two_agents_human_in_the_loop_evals (
            user_id, survey_time, agent_1, agent_2,
            conversation_agent_1, conversation_agent_2,
            rating_agent_1, rating_agent_2, better_agent,
            comment, model_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        st.session_state.get("user_id", "anonymous"),
        survey_time,
        agent_1_model,
        agent_2_model,
        conv1,
        conv2,
        st.session_state["rating_agent_1"],
        st.session_state["rating_agent_2"],
        better_agent,
        st.session_state["comments"],
        student_model
    ))
    conn.commit()
    cursor.close()
    conn.close()
    st.success("Thank you for your feedback!")
    reset_form()
