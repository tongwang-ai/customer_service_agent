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

student_model = "gpt-3.5-turbo-0125"
embedding_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

library_augmented = pickle.load(open('gpt-3.5-turbo-0125-library_augmented.pkl', 'rb'))
scenario_embeds_augmented = library_augmented['scenario_embedding']
guidelines_augmented = library_augmented['guidelines']

library_simulated = pickle.load(open('gpt-3.5-turbo-0125-library_simulated.pkl', 'rb'))
scenario_embeds_simulated = library_simulated['scenario_embedding']
guidelines_simulated = library_simulated['guidelines']


st.set_page_config(page_title="LLM Chat Interface", layout="wide")
input_placeholder = st.empty()  # create a container

if st.session_state.get("reset_now", False):
    def reset_form():
        st.session_state["chat_history_agent"] = [
            {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
            {"role": "assistant", "content": "Hello, this is Agent 06520, how can I help you?"}
        ]
        st.session_state["rating_agent"] = 1
        st.session_state["comments"] = ""
        st.session_state["form_submitted"] = False

    reset_form()
    st.session_state["reset_now"] = False
    st.rerun()

st.title("Live Chat with a Customer Service Agent")
if "show_thank_you" not in st.session_state:
    st.session_state["show_thank_you"] = False
if st.session_state.get("show_thank_you", False):
    st.success("Your response has been recorded. Thank you for your participation. The completion code is: 06520.")
    st.stop()

# ---- Randomize guideline type ONCE per session ----
if "guideline_for_agent" not in st.session_state:
    st.session_state["guideline_for_agent"] = random.choice([True, False])  # True=augmented, False=simulated

agent_label = "Agent"

# ---- Session state for single agent ----
if "chat_history_agent" not in st.session_state:
    st.session_state["chat_history_agent"] = [
        {"role": "system", "content": my_prompts.AGENT_PROMPT_TICKET},
        {"role": "assistant", "content": f"Hello, this is the Agent 06520, how can I help you?"}
    ]
if "user_input_agent" not in st.session_state:
    st.session_state["user_input_agent"] = ""

st.markdown(
    """
    <div style="border: 2px solid #B0B0B0; background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="font-size: 16px; color: #333;">
        <b>Your task is to interact with the agent to request a full refund for a restricted ticket with booking reference YAL165.</b><br><br>
        <b>Objective:</b> Negotiate for a refund as you would in a real-life situation.<br><br>
        <b>Guidelines:</b><br>
        - Use persuasive and realistic arguments to achieve your goal - which is to get a full refund.<br>
        - Try to engage in multiple rounds of back-and-forth dialogue.<br>
        - If the conversation requires details not included in the instructions, use your best judgment to provide reasonable and realistic information.<br><br>
        <span style="color: red; font-weight: bold;font-size: 20px;">
            Note: Once you send a message, it may take a few seconds for the agent to respond. DO NOT keep sending messages or refresh while waiting for a response.
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

def send_message(chat_history_key, input_key, use_human):
    if st.session_state.get("await_agent_response", False):
        conversation = [m for m in st.session_state[chat_history_key] if m["role"] != "system"]
        conv_txt = ""
        for m in conversation:
            if m["role"] == "assistant":
                conv_txt += "\n\nAgent: " + m["content"]
            elif m["role"] == "user":
                conv_txt += "\n\nCustomer: " + m["content"]
        conv_txt = conv_txt.strip()
        if use_human:
            best_guideline = get_best_guideline(conv_txt, embedding_client, scenario_embeds_augmented, guidelines_augmented)
        else:
            best_guideline = get_best_guideline(conv_txt, embedding_client, scenario_embeds_simulated, guidelines_simulated)
        llm_response = gen_agent_response(conv_txt, student_model, client=client, guidelines=best_guideline, temperature=0.3)
        st.session_state[chat_history_key].append({"role": "assistant", "content": llm_response})
        st.session_state["await_agent_response"] = False

# --- Chat UI for single agent ---
st.write(f"**Chat with a customer service agent**")
for msg in st.session_state["chat_history_agent"]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**{agent_label}:** {msg['content']}")

st.session_state.setdefault("await_agent_response", False)
st.session_state.setdefault("clear_input_agent", False)

input_placeholder = st.empty()
if st.session_state["clear_input_agent"]:
    user_message = input_placeholder.text_input(
        f"Enter your message to the agent",
        value="",
        key="temp_input_agent"
    )
    st.session_state["clear_input_agent"] = False
else:
    user_message = input_placeholder.text_input(
        f"Enter your message to the agent",
        key="user_input_agent"
    )

if st.button(f"Send to agent", key="send_btn_agent", disabled=st.session_state.get("await_agent_response", False)):
    if user_message:
        st.session_state["chat_history_agent"].append({"role": "user", "content": user_message})
        st.session_state["await_agent_response"] = True
        st.session_state["clear_input_agent"] = True
        st.rerun()

if st.session_state["await_agent_response"]:
    send_message("chat_history_agent", "user_input_agent", st.session_state["guideline_for_agent"])
    st.session_state["await_agent_response"] = False
    st.rerun()

# Rating slider
st.radio(
    "How satisfied are you with the agent's service?",
    [
        "1: Extremely unsatisfied",
        "2: Unsatisfied",
        "3: Neutral",
        "4: Satisfied",
        "5: Extremely satisfied"
    ],
    key="rating_agent"
)

# Count agent responses
agent_turns = len([msg for msg in st.session_state["chat_history_agent"] if msg["role"] == "assistant"])
num_turns = 4
not_enough_turns = agent_turns < num_turns + 1



st.subheader("Briefly explain your rating")
st.text_area("Your comments:", key="comments", value=st.session_state.get("comments", ""))

def create_connection():
    return psycopg2.connect(
        dbname=st.secrets["database"]["DB_NAME"],
        user=st.secrets["database"]["DB_USER"],
        password=st.secrets["database"]["DB_PASSWORD"],
        host=st.secrets["database"]["DB_HOST"],
        port=st.secrets["database"]["DB_PORT"],
        sslmode="require"
    )

col1, col2, col3 = st.columns([1,1,1])
with col2:
    if not_enough_turns:
        st.warning("If your conversation is too short, you won't be able to submit.")
    if st.button("Submit survey", disabled=not_enough_turns or st.session_state.get("form_submitted", False)):
        st.session_state["form_submitted"] = True
        connection = create_connection()
        cursor = connection.cursor()
        conversation_agent = json.dumps([msg for msg in st.session_state["chat_history_agent"] if msg["role"] != "system"])
        elapsed_time = datetime.now() - start_time
        agent_model = student_model + ("-augmented" if st.session_state["guideline_for_agent"] else "-simulated")
    
        cursor.execute("""
            INSERT INTO one_agent_human_in_the_loop_evals (
                user_id, elapsed_time, agent,
                conversation,
                rating, comments, model_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            st.session_state.get("user_id", "anonymous"),
            elapsed_time,
            agent_model,
            conversation_agent,
            st.session_state["rating_agent"],
            st.session_state["comments"],
            student_model
        ))
    
        connection.commit()
        cursor.close()
        connection.close()
        st.session_state["show_thank_you"] = True   
        st.rerun()
