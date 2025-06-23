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


if "start_time" not in st.session_state:
    st.session_state["start_time"] = datetime.now()
start_time = st.session_state["start_time"]

student_model = "meta/llama-2-7b-chat"
embedding_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

library = pickle.load(open('llama-2-7b-chat-library.pkl', 'rb'))
scenario_embeds = library['scenario_embedding']
guidelines = library['guidelines']

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="LLM Chat Interface", layout="wide")

# === Safe reset trigger ===
if st.session_state.get("reset_now", False):
    def reset_form():
        st.session_state["chat_history_agent_1"] = [
            {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
            {"role": "assistant", "content": "Hello, this is Agent 1, how can I help you?"}
        ]
        st.session_state["chat_history_agent_2"] = [
            {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
            {"role": "assistant", "content": "Hello, this is Agent 2, how can I help you?"}
        ]
        st.session_state["rating_agent_1"] = 1
        st.session_state["rating_agent_2"] = 1
        st.session_state["comments"] = ""
        st.session_state["form_submitted"] = False

    reset_form()
    st.session_state["reset_now"] = False
    st.rerun()

st.title("Live Chat with Two Customer Service Agents")
if "show_thank_you" not in st.session_state:
    st.session_state["show_thank_you"] = False
if st.session_state.get("show_thank_you", False):
    st.success("Your response has been recorded. Thank you for your participation. The completion code is: 06520.")
    st.stop()

# Initial session setup
if "guideline_for_agent_1" not in st.session_state:
    use_guideline_for_agent_1 = random.choice([True, False])
    st.session_state["guideline_for_agent_1"] = use_guideline_for_agent_1
    st.session_state["guideline_for_agent_2"] = not use_guideline_for_agent_1

for key, default in {
    "chat_history_agent_1": [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 1, how can I help you?"}
    ],
    "chat_history_agent_2": [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": "Hello, this is Agent 2, how can I help you?"}
    ],
    "user_input_agent_1": "",
    "user_input_agent_2": "",
    # "clear_input_agent_1": False,
    # "clear_input_agent_2": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def create_connection():
    return psycopg2.connect(
        dbname=st.secrets["database"]["DB_NAME"],
        user=st.secrets["database"]["DB_USER"],
        password=st.secrets["database"]["DB_PASSWORD"],
        host=st.secrets["database"]["DB_HOST"],
        port=st.secrets["database"]["DB_PORT"],
        sslmode="require"
    )

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
        <span style="color: red; font-weight: bold;font-size: 20px;">
            Note: It takes up to 1 minute for the agent to respond. Please wait patiently and DO NOT keep sending messages while waiting for a response.
        </span>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

def get_best_guideline(conv_txt, embedding_client, scenario_embeds, guidelines):
    conv_embed = get_embedding_sync(conv_txt, embedding_client)
    closest_idx, _ = find_k_closest_embedding(conv_embed, scenario_embeds)
    return guidelines[closest_idx]

def send_message(agent, chat_history_key, input_key, use_guideline):
    # Only handle agent response if 'await_agent_response' flag is set
    if st.session_state.get(f"await_agent_response_{agent}", False):
        conversation = [m for m in st.session_state[chat_history_key] if m["role"] != "system"]
        conv_txt = ""
        for m in conversation:
            if m["role"] == "assistant":
                conv_txt += "\n\nAgent: " + m["content"]
            elif m["role"] == "user":
                conv_txt += "\n\nCustomer: " + m["content"]
        conv_txt = conv_txt.strip()
        best_guideline = get_best_guideline(conv_txt, embedding_client, scenario_embeds, guidelines) if use_guideline else None
        llm_response = gen_agent_response(conv_txt, student_model, client=None, guidelines=best_guideline, temperature=0.3)
        st.session_state[chat_history_key].append({"role": "assistant", "content": llm_response})
        st.session_state[f"await_agent_response_{agent}"] = False


col1, _, col2 = st.columns([1, 0.1, 1])

with col1:
    st.write("**Chat with Agent 1**")
    for message in st.session_state["chat_history_agent_1"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 1:** {message['content']}")

    st.text_input("Enter your message to Agent 1", key="user_input_agent_1")

    # --- BUTTON LOGIC ---
    if st.button("Send to Agent 1"):
        user_message = st.session_state["user_input_agent_1"]
        if user_message:
            st.session_state["chat_history_agent_1"].append({"role": "user", "content": user_message})
            st.session_state["await_agent_response_agent_1"] = True
            st.session_state["user_input_agent_1"] = ""
            
            st.rerun()

    # After rerun, if a user message was just appended but no agent response yet, generate it:
    send_message("agent_1", "chat_history_agent_1", "user_input_agent_1", st.session_state["guideline_for_agent_1"])

    st.slider("Rate Agent 1 - 1 means very dissatisfied and 5 means very satisfied", 1, 5, value=1, key="rating_agent_1")


with col2:
    st.write("**Chat with Agent 2**")
    for message in st.session_state["chat_history_agent_2"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 2:** {message['content']}")

    st.text_input("Enter your message to Agent 2", key="user_input_agent_2")

    # --- BUTTON LOGIC ---
    if st.button("Send to Agent 2"):
        user_message = st.session_state["user_input_agent_2"]
        if user_message:
            st.session_state["chat_history_agent_2"].append({"role": "user", "content": user_message})
            st.session_state["user_input_agent_2"] = ""
            st.session_state["await_agent_response_agent_2"] = True
            st.rerun()

    # After rerun, if a user message was just appended but no agent response yet, generate it:
    send_message("agent_2", "chat_history_agent_2", "user_input_agent_2", st.session_state["guideline_for_agent_2"])

    st.slider("Rate Agent 2 - 1 means very dissatisfied and 5 means very satisfied", 1, 5, value=1, key="rating_agent_2")


better_agent = st.radio("Which agent do you think performed better?", ("Agent 1", "Agent 2"))

st.subheader("Briefly explain your ratings and choice above")
st.text_area("Your comments:", key="comments", value=st.session_state.get("comments", ""))



# Count agent responses
agent_1_turns = len([msg for msg in st.session_state["chat_history_agent_1"] if msg["role"] == "assistant"])
agent_2_turns = len([msg for msg in st.session_state["chat_history_agent_2"] if msg["role"] == "assistant"])
num_turns = 4
not_enough_turns = agent_1_turns < num_turns+1 or agent_2_turns < num_turns+1

if not_enough_turns:
    st.warning("Please complete **4 full exchanges with each agent** (i.e., you send a message *and* receive a response, 4 times per agent) before submitting your feedback.")

if st.button("Submit Feedback", disabled=not_enough_turns or st.session_state.get("form_submitted", False)):
    st.session_state["form_submitted"] = True
    connection = create_connection()
    cursor = connection.cursor()
    conversation_agent_1 = json.dumps([msg for msg in st.session_state["chat_history_agent_1"] if msg["role"] != "system"])
    conversation_agent_2 = json.dumps([msg for msg in st.session_state["chat_history_agent_2"] if msg["role"] != "system"])
    elapsed_time = datetime.now() - start_time
    agent_1_model = student_model + ("-guidelines" if st.session_state["guideline_for_agent_1"] else "-base")
    agent_2_model = student_model + ("-guidelines" if st.session_state["guideline_for_agent_2"] else "-base")

    cursor.execute("""
        INSERT INTO two_agents_human_in_the_loop_evals (
            user_id, elapsed_time, agent_1, agent_2,
            conversation_agent_1, conversation_agent_2,
            rating_agent_1, rating_agent_2, better_agent,
            comment, model_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        st.session_state.get("user_id", "anonymous"),
        elapsed_time,
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
    st.session_state["show_thank_you"] = True   # <--- ADD THIS
    # st.success("Your response has been recorded. Thank you for your participation. The completion code is: 06520.")
    # st.session_state["reset_now"] = True
    # st.rerun()

