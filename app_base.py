import streamlit as st
import openai
import my_prompts
from my_utils import *
import psycopg2
import json
import random
from datetime import datetime
import argparse

# Access the model argument
student_model = "meta/llama-2-7b-chat"

# Initialize session state for chat histories of both agents
agent_1_sys_txt = my_prompts.AGENT_PROMPT_TICKET + my_prompts.AIRLINE_POLICY_TICKET
agent_2_sys_txt = my_prompts.AGENT_PROMPT_TICKET + my_prompts.AIRLINE_POLICY_TICKET
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

if "rating_agent_1" not in st.session_state:
    st.session_state["rating_agent_1"] = 0
if "rating_agent_2" not in st.session_state:
    st.session_state["rating_agent_2"] = 0
if "comments_agent1" not in st.session_state:
    st.session_state["comments_agent1"] = ""
if "comments_agent2" not in st.session_state:
    st.session_state["comments_agent2"] = ""
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
if "user_input_agent_1" not in st.session_state:
    st.session_state["user_input_agent_1"] = ""
if "user_input_agent_2" not in st.session_state:
    st.session_state["user_input_agent_2"] = ""

# Reset function to clear session states
def reset_form():
    # Reset session state keys not tied to widgets
    st.session_state["chat_history_agent_1"] = [
        {"role": "system", "content": agent_1_sys_txt},
        {"role": "assistant", "content": "Hello, this is Agent 1. How can I help you today?"}
    ]
    st.session_state["chat_history_agent_2"] = [
        {"role": "system", "content": agent_2_sys_txt},
        {"role": "assistant", "content": "Hello, this is Agent 2. How can I assist you?"}
    ]





# Configure OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]



# Randomly assign each function to Agent 1 and Agent 2 at the start of the session and store the mapping
if "agent_1_response_func" not in st.session_state:
    funcs = random.sample([get_teacher_response, get_student_response], 2)
    st.session_state["agent_1_response_func"] = funcs[0]
    st.session_state["agent_2_response_func"] = funcs[1]
    # st.session_state["agent_1_func_name"] = "get_teacher_response" if funcs[0] == get_teacher_response else "get_student_response"
    # st.session_state["agent_2_func_name"] = "get_teacher_response" if funcs[1] == get_teacher_response else "get_student_response"
    st.session_state['agent_1'] = "gpt-4" if funcs[0] == get_teacher_response else student_model
    st.session_state['agent_2'] = "gpt-4" if funcs[1] == get_teacher_response else student_model
# Configure Streamlit app layout
st.set_page_config(page_title="LLM Chat Interface", layout="wide")

st.title("Live Chat with Two Customer Service Agents")
# st.write("Interact with Agent 1 and Agent 2 to request a full refund for a restricted ticket.")
st.markdown(
    """
    <div style="
        border: 2px solid #B0B0B0; 
        background-color: #f9f9f9; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 20px;">
        <p style="font-size: 16px; color: #333;">
        <b>In this study, you will role-play as an airline customer separately contacting two independent customer service agents. Each agent has no knowledge of your interaction or any information exchanged with the other. You recently purchased a non-refundable, non-changeable flight ticket (confirmation number: YAL165) one day ago. Your goal is to request the cancellation of this restricted ticket and attempt to obtain a full refund. After each interaction, please rate the agent’s performance and provide specific suggestions on how they can enhance their customer service skills.</b><br><br>
        <b>Objective:</b> Negotiate as you would in a real-life situation.<br><br>
        <b>Guidelines:</b><br>
        - Use persuasive and realistic arguments to achieve your goal.<br>
        - If the conversation requires details not included in the instruction, use your best judgment to provide reasonable and realistic information.<br>
        - Rate each agent at the end of the conversation.<br><br>
        <b>Note:</b> It takes a few seconds for the agent to respond. Do not refresh the page while waiting for a response.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)





# Function to handle sending messages for each agent
def send_message(agent):
    user_message = st.session_state[f"user_input_{agent}"]
    if user_message:
        if agent == "agent_1":
            st.session_state["chat_history_agent_1"].append({"role": "user", "content": user_message})
            llm_response = st.session_state["agent_1_response_func"](st.session_state["chat_history_agent_1"],st.session_state['agent_1'])
            st.session_state["chat_history_agent_1"].append({"role": "assistant", "content": llm_response})
        else:
            st.session_state["chat_history_agent_2"].append({"role": "user", "content": user_message})
            llm_response = st.session_state["agent_2_response_func"](st.session_state["chat_history_agent_2"],st.session_state['agent_2'])
            st.session_state["chat_history_agent_2"].append({"role": "assistant", "content": llm_response})

        # Clear the input field for the specific agent
        st.session_state[f"user_input_{agent}"] = ""

# Set up two columns for side-by-side interaction with both agents
col1, spacer, col2 = st.columns([1, 0.1, 1]) 

# Column for Agent 1
with col1:
    st.write("**Chat with Agent 1**")
    for message in st.session_state["chat_history_agent_1"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 1:** {message['content']}")
    
    # Input field for Agent 1
    st.text_input("Enter your message to Agent 1", key="user_input_agent_1", value="", on_change=lambda: send_message("agent_1"))
    
    # Rating for Agent 1
    st.slider(
        "Rate Agent 1 - 1 means very disatisfied and 5 means very satisfied",
        min_value=1,
        max_value=5,
        key="rating_agent_1"
    )
with spacer:
    st.write("")
# Column for Agent 2
with col2:
    st.write("**Chat with Agent 2**")
    for message in st.session_state["chat_history_agent_2"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Agent 2:** {message['content']}")
    
    # Input field for Agent 2
    st.text_input("Enter your message to Agent 2", key="user_input_agent_2", value="", on_change=lambda: send_message("agent_2"))
    
    # Rating for Agent 2
    st.slider(
        "Rate Agent 2 - 1 means very disatisfied and 5 means very satisfied",
        min_value=1,
        max_value=5,
        key="rating_agent_2"
    )

# Comments section for both agents
st.subheader("Suggestions for Agent 1")
st.text_area("Please provide feedback on how Agent 1 can improve:", key="comments_agent1", value="")

st.subheader("Suggestions for Agent 2")
st.text_area("Please provide feedback on how Agent 2 can improve:", key="comments_agent2", value="")

# Select the better agent
better_agent = st.radio("Which agent do you think performed better?", ("Agent 1", "Agent 2"))

# Button to submit feedback and choice of better agent
# if st.button("Submit Feedback"):
    # connection = create_connection()
    # cursor = connection.cursor()
    
    # # Filter chat histories to exclude system messages
    # filtered_conversation_agent_1 = [
    #     message for message in st.session_state["chat_history_agent_1"] if message["role"] != "system"
    # ]
    # filtered_conversation_agent_2 = [
    #     message for message in st.session_state["chat_history_agent_2"] if message["role"] != "system"
    # ]
    
    # # Serialize conversations
    # conversation_agent_1 = json.dumps(filtered_conversation_agent_1)
    # conversation_agent_2 = json.dumps(filtered_conversation_agent_2)
    
    # # Get current timestamp
    # survey_time = datetime.now()
    
    # # Insert feedback with function mapping info, agent selection, and ratings into the database
    # cursor.execute("""
    #     INSERT INTO hum_2LLMagents_conv (
    #         user_id, survey_time, agent_1, agent_2,
    #         conversation_agent_1, conversation_agent_2,
    #         rating_agent_1, rating_agent_2, better_agent,
    #         comments, model_type
    #     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    # """, (
    #     st.session_state.get("user_id", "anonymous"),
    #     survey_time,
    #     st.session_state["agent_1"],
    #     st.session_state["agent_2"],
    #     conversation_agent_1,
    #     conversation_agent_2,
    #     st.session_state["rating_agent_1"],
    #     st.session_state["rating_agent_2"],
    #     better_agent,
    #     st.session_state["comments"],
    #     "base_student_model"
    # ))
    
    # connection.commit()
    # cursor.close()
    # connection.close()
    

if st.button("Submit Feedback", disabled=st.session_state.get("form_submitted", False)):
    st.session_state["form_submitted"] = True  # Disable button after click
    # Your existing feedback submission code here

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
    survey_time = datetime.now()
    
    # Insert feedback with function mapping info, agent selection, and ratings into the database
    cursor.execute("""
        INSERT INTO hum_2LLMagents_conv (
            user_id, survey_time, agent_1, agent_2,
            conversation_agent_1, conversation_agent_2,
            rating_agent_1, rating_agent_2, better_agent,
            comments_agent1, comments_agent2, model_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        st.session_state.get("user_id", "anonymous"),
        survey_time,
        st.session_state["agent_1"],
        st.session_state["agent_2"],
        conversation_agent_1,
        conversation_agent_2,
        st.session_state["rating_agent_1"],
        st.session_state["rating_agent_2"],
        better_agent,
        st.session_state["comments_agent1"],
        st.session_state["comments_agent2"],
        "base_student_model"
    ))
    
    connection.commit()
    cursor.close()
    connection.close()




    st.success("Thank you for your feedback!")

    # Call the reset function after successful submission
    reset_form()

