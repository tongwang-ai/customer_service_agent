import streamlit as st
import openai
import my_prompts
from my_utils import *
import psycopg2
import json
import random
from datetime import datetime

# Database connection setup
def create_connection():
    return psycopg2.connect(
        dbname=st.secrets["database"]["DB_NAME"],
        user=st.secrets["database"]["DB_USER"],
        password=st.secrets["database"]["DB_PASSWORD"],
        host=st.secrets["database"]["DB_HOST"],
        port=st.secrets["database"]["DB_PORT"],
        sslmode="require"
    )

# Configure OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]



# Randomly assign each function to Agent 1 and Agent 2 at the start of the session and store the mapping
if "agent_1_response_func" not in st.session_state:
    funcs = random.sample([get_teacher_response, get_student_response], 2)
    st.session_state["agent_1_response_func"] = funcs[0]
    st.session_state["agent_2_response_func"] = funcs[1]
    st.session_state["agent_1_func_name"] = "get_teacher_response" if funcs[0] == get_teacher_response else "get_student_response"
    st.session_state["agent_2_func_name"] = "get_teacher_response" if funcs[1] == get_teacher_response else "get_student_response"

# Configure Streamlit app layout
st.set_page_config(page_title="LLM Chat Interface", layout="wide")

st.title("Live Chat with Two Customer Service Agents")
st.write("Interact with Agent 1 and Agent 2 to request a full refund for a restricted ticket.")

# Initialize session state for chat histories of both agents
agent_sys_txt = my_prompts.AGENT_PROMPT_TICKET + my_prompts.AIRLINE_POLICY_TICKET
agent_2_sys_txt = my_prompts.AGENT_PROMPT_TICKET + my_prompts.AIRLINE_POLICY_TICKET

if "chat_history_agent_1" not in st.session_state:
    st.session_state["chat_history_agent_1"] = [
        {"role": "system", "content": agent_1_sys_txt},
        {"role": "assistant", "content": "Hello, this is Agent 1. How can I help you today?"}
    ]

if "chat_history_agent_2" not in st.session_state:
    st.session_state["chat_history_agent_2"] = [
        {"role": "system", "content": agent_2_sys_txt},
        {"role": "assistant", "content": "Hello, this is Agent 2. How can I assist you?"}
    ]

if "rating_agent_1" not in st.session_state:
    st.session_state["rating_agent_1"] = 0

if "rating_agent_2" not in st.session_state:
    st.session_state["rating_agent_2"] = 0

if "comments" not in st.session_state:
    st.session_state["comments"] = ""

# Function to handle sending messages for each agent
def send_message(agent):
    user_message = st.session_state[f"user_input_{agent}"]
    if user_message:
        if agent == "agent_1":
            st.session_state["chat_history_agent_1"].append({"role": "user", "content": user_message})
            llm_response = st.session_state["agent_1_response_func"](st.session_state["chat_history_agent_1"])
            st.session_state["chat_history_agent_1"].append({"role": "assistant", "content": llm_response})
        else:
            st.session_state["chat_history_agent_2"].append({"role": "user", "content": user_message})
            llm_response = st.session_state["agent_2_response_func"](st.session_state["chat_history_agent_2"])
            st.session_state["chat_history_agent_2"].append({"role": "assistant", "content": llm_response})

        # Clear the input field for the specific agent
        st.session_state[f"user_input_{agent}"] = ""

# Set up two columns for side-by-side interaction with both agents
col1, col2 = st.columns(2)

# Column for Agent 1
with col1:
    st.write("**Chat with Agent 1**")
    for message in st.session_state["chat_history_agent_1"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 1:** {message['content']}")
    
    # Input field for Agent 1
    st.text_input("Enter your message to Agent 1", key="user_input_agent_1", on_change=lambda: send_message("agent_1"))
    
    # Rating for Agent 1
    st.slider(
        "Rate Agent 1",
        min_value=1,
        max_value=5,
        key="rating_agent_1"
    )

# Column for Agent 2
with col2:
    st.write("**Chat with Agent 2**")
    for message in st.session_state["chat_history_agent_2"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 2:** {message['content']}")
    
    # Input field for Agent 2
    st.text_input("Enter your message to Agent 2", key="user_input_agent_2", on_change=lambda: send_message("agent_2"))
    
    # Rating for Agent 2
    st.slider(
        "Rate Agent 2",
        min_value=1,
        max_value=5,
        key="rating_agent_2"
    )

# Comments section for both agents
st.subheader("Comments about the Agents")
st.text_area("Your comments:", key="comments", value="")

# Select the better agent
better_agent = st.radio("Which agent do you think performed better?", ("Agent 1", "Agent 2"))

# Button to submit feedback and choice of better agent
if st.button("Submit Feedback"):
    connection = create_connection()
    cursor = connection.cursor()
    
    # Filter chat histories to exclude system messages
    filtered_conversation_agent_1 = [
        message for message in st.session_state["chat_history_agent_1"] if message["role"] != "system"
    ]
    filtered_conversation_agent_2 = [
        message for message in st.session_state["chat_history_agent_2"] if message["role"] != "system"
    ]
    
    # Serialize conversations
    conversation_agent_1 = json.dumps(filtered_conversation_agent_1)
    conversation_agent_2 = json.dumps(filtered_conversation_agent_2)
    
    # Get current timestamp
    feedback_time = datetime.now()
    
    # Insert feedback with function mapping info, agent selection, and ratings into the database
    cursor.execute("""
        INSERT INTO human_evals (
            user_id, conversation_agent_1, conversation_agent_2,
            rating_agent_1, rating_agent_2, comments,
            feedback_time, better_agent,
            agent_1_func_name, agent_2_func_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        st.session_state.get("user_id", "anonymous"),
        conversation_agent_1,
        conversation_agent_2,
        st.session_state["rating_agent_1"],
        st.session_state["rating_agent_2"],
        st.session_state["comments"],
        feedback_time,
        better_agent,
        st.session_state["agent_1_func_name"],
        st.session_state["agent_2_func_name"]
    ))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    st.success("Thank you for your feedback!")

    # # Reset chat histories after submission
    # st.session_state["chat_history_agent_1"] = [
    #     {"role": "system", "content": agent
