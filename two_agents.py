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

student_model = "meta/llama-2-7b-chat"  # or whatever model string you want
embedding_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

library = pickle.load(open('llama-2-7b-chat-library.pkl','rb'))
scenario_embeds = library['scenario_embedding']
guidelines = library['guidelines']

if "clear_input_agent_1" not in st.session_state:
    st.session_state["clear_input_agent_1"] = False


def create_connection():
    return psycopg2.connect(
        dbname=st.secrets["database"]["DB_NAME"],
        user=st.secrets["database"]["DB_USER"],
        password=st.secrets["database"]["DB_PASSWORD"],
        host=st.secrets["database"]["DB_HOST"],
        port=st.secrets["database"]["DB_PORT"],
        sslmode="require"
    )



# Randomly assign at session start
if "guideline_for_agent_1" not in st.session_state:
    use_guideline_for_agent_1 = random.choice([True, False])
    st.session_state["guideline_for_agent_1"] = use_guideline_for_agent_1
    st.session_state["guideline_for_agent_2"] = not use_guideline_for_agent_1

# Chat histories and input initialization
if "chat_history_agent_1" not in st.session_state:
    st.session_state["chat_history_agent_1"] = [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 1, how can I help you?"}
    ]
if "chat_history_agent_2" not in st.session_state:
    st.session_state["chat_history_agent_2"] = [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 2, how can I help you?"}
    ]
if "user_input_agent_1" not in st.session_state:
    st.session_state["user_input_agent_1"] = ""
if "user_input_agent_2" not in st.session_state:
    st.session_state["user_input_agent_2"] = ""

# Add clear input flags
if "clear_input_agent_1" not in st.session_state:
    st.session_state["clear_input_agent_1"] = False
if "clear_input_agent_2" not in st.session_state:
    st.session_state["clear_input_agent_2"] = False

def reset_form():
    st.session_state["chat_history_agent_1"] = [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 1, how can I help you?"}
    ]
    st.session_state["chat_history_agent_2"] = [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 2, how can I help you?"}
    ]
    st.session_state["user_input_agent_1"] = ""
    st.session_state["user_input_agent_2"] = ""
    st.session_state["clear_input_agent_1"] = False
    st.session_state["clear_input_agent_2"] = False
    st.session_state["rating_agent_1"] = 0
    st.session_state["rating_agent_2"] = 0
    st.session_state["comments"] = ""
    st.session_state["form_submitted"] = False

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="LLM Chat Interface", layout="wide")
st.title("Live Chat with Two Customer Service Agents")
st.markdown(
    """
    <div style="border: 2px solid #B0B0B0; background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="font-size: 16px; color: #333;">
        <b>Your task is to interact with Agent 1 and Agent 2 to request a full refund for a restricted ticket with confirmation number YAL165.</b><br><br>
        <b>Objective:</b> Negotiate for a refund as you would in a real-life situation.<br><br>
        <b>Guidelines:</b><br>
        - Use persuasive and realistic arguments to achieve your goal.<br>
        - Try to have at least 4 rounds of back-and-forth dialogue with each agent.<br>
        - If the conversation requires details not included in the instructions, use your best judgment to provide reasonable and realistic information.<br><br>
        <span style="color: red; font-weight: bold;">
            Note: It takes up to 1 minute for the agent to respond. Please be patient and do not refresh the page while waiting for a response.
        </span>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- ASYNC guideline retrieval wrapper
def get_best_guideline(conv_txt, embedding_client, scenario_embeds, guidelines):
    conv_embed = get_embedding_sync(conv_txt, embedding_client)
    closest_idx, _ = find_k_closest_embedding(conv_embed, scenario_embeds)
    return guidelines[closest_idx]

# --- Send message handler for each agent
def send_message(agent, chat_history_key, input_key, use_guideline):
    user_message = st.session_state[input_key]
    if user_message:
        # Append the new user message!
        
        st.session_state[chat_history_key].append({"role": "user", "content": user_message})

        # Get the entire conversation so far (excluding system)
        conversation = [
            m for m in st.session_state[chat_history_key] if m["role"] != "system"
        ]
        conv_txt = ""
        for m in conversation:
            if m["role"] == "assistant":
                conv_txt += "\n\nAgent: " + m["content"]
            elif m["role"] == "user":
                conv_txt += "\n\nCustomer: " + m["content"]
        conv_txt = conv_txt.strip()

        if use_guideline:    
            best_guideline = get_best_guideline(conv_txt, embedding_client, scenario_embeds, guidelines)
        else:
            best_guideline = None

        # Pass all turns to the LLM
        llm_response = gen_agent_response(
            conv_txt,    # <<<< ALL turns, not just the most recent
            student_model,
            client=None,
            guidelines=best_guideline,
            temperature=0.3
        )

        # Append the agent's response
        st.session_state[chat_history_key].append({"role": "assistant", "content": llm_response})


# --- UI layout ---
col1, _, col2 = st.columns([1, 0.1, 1])

with col1:
    st.write("**Chat with Agent 1**")
    for message in st.session_state["chat_history_agent_1"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 1:** {message['content']}")

    # ---- Clear input BEFORE widget is instantiated
    if st.session_state["clear_input_agent_1"]:
        st.session_state["user_input_agent_1"] = ""
        st.session_state["clear_input_agent_1"] = False

    st.text_input("Enter your message to Agent 1", key="user_input_agent_1")
    if st.button("Send to Agent 1"):
        send_message(
            "agent_1",
            "chat_history_agent_1",
            "user_input_agent_1",
            st.session_state["guideline_for_agent_1"]
        )
        st.session_state["clear_input_agent_1"] = True
        st.rerun()
        

    
    st.slider(
        "Rate Agent 1 - 1 means very dissatisfied and 5 means very satisfied",
        min_value=1,
        max_value=5,
        value = 1,
        key="rating_agent_1"
    )

with col2:
    st.write("**Chat with Agent 2**")
    for message in st.session_state["chat_history_agent_2"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 2:** {message['content']}")

    # ---- Clear input BEFORE widget is instantiated
    if st.session_state["clear_input_agent_2"]:
        st.session_state["user_input_agent_2"] = ""
        st.session_state["clear_input_agent_2"] = False

    st.text_input("Enter your message to Agent 2", key="user_input_agent_2")
    if st.button("Send to Agent 2"):
        send_message(
            "agent_2",
            "chat_history_agent_2",
            "user_input_agent_2",
            st.session_state["guideline_for_agent_2"]
        )
        st.session_state["clear_input_agent_2"] = True
        st.rerun()

        
    st.slider(
        "Rate Agent 2 - 1 means very dissatisfied and 5 means very satisfied",
        min_value=1,
        max_value=5,
        value = 1,
        key="rating_agent_2"
    )

# --- Comments and feedback ---
st.subheader("Comments about the Agents")
st.text_area("Your comments:", key="comments", value=st.session_state.get("comments", ""))

better_agent = st.radio("Which agent do you think performed better?", ("Agent 1", "Agent 2"))

# --- Turn count logic START ---
# Exclude 'system' messages when counting turns
agent_1_turns = len([msg for msg in st.session_state["chat_history_agent_1"] if msg["role"] != "user"])
agent_2_turns = len([msg for msg in st.session_state["chat_history_agent_2"] if msg["role"] != "user"])
min_turns_required = 1
not_enough_turns = agent_1_turns < min_turns_required or agent_2_turns < min_turns_required

if not_enough_turns:
    st.warning("Please continue the conversation with both agents until each has at least 4 turns before submitting feedback.")
# --- Turn count logic END ---

if st.button("Submit Feedback", disabled=not_enough_turns or st.session_state.get("form_submitted", False)):
    st.session_state["form_submitted"] = True
    connection = create_connection()
    cursor = connection.cursor()
    filtered_conversation_agent_1 = [
        msg for msg in st.session_state["chat_history_agent_1"] if msg["role"] != "system"
    ]
    filtered_conversation_agent_2 = [
        msg for msg in st.session_state["chat_history_agent_2"] if msg["role"] != "system"
    ]
    conversation_agent_1 = json.dumps(filtered_conversation_agent_1)
    conversation_agent_2 = json.dumps(filtered_conversation_agent_2)
    survey_time = datetime.now()
    # Assign the model names based on guideline usage (as discussed before)
    agent_1_model = student_model + ("-guidelines" if st.session_state["guideline_for_agent_1"] else "-base")
    agent_2_model = student_model + ("-guidelines" if st.session_state["guideline_for_agent_2"] else "-base")
    cursor.execute("""
        INSERT INTO two_agents_human_in_the_loop_evals (
            user_id, survey_time, agent_1, agent_2,
            conversation_agent_1, conversation_agent_2,
            rating_agent_1, rating_agent_2, better_agent,
            comments, model_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        st.session_state.get("user_id", "anonymous"),
        survey_time,
        agent_1_model,
        agent_2_model,
        conversation_agent_1,
        conversation_agent_2,
        st.session_state["rating_agent_1"],
        st.session_state["rating_agent_2"],
        better_agent,
        st.session_state["comments"],
        student_model
    ))

    connection.commit()
    cursor.close()
    connection.close()
    st.success("Thank you for your feedback!")
    reset_form()
