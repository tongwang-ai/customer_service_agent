import streamlit as st
import openai
import my_prompts
import psycopg2
import json
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

# Configure your OpenAI API key or another LLM backend
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configure Streamlit app layout
st.set_page_config(page_title="LLM Chat Interface", layout="centered")

st.title("Live Chat with a Customer Service Agent")
st.write("Chat with an agent to request a full refund of a restricted ticket you purchased")

# Initialize session state for chat history
agent_sys_txt = my_prompts.AGENT_PROMPT_TICKET + my_prompts.AIRLINE_POLICY_TICKET

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "system", "content": agent_sys_txt},
        {"role": "assistant", "content": "Hello, how can I help you?"}  # Initial greeting from the agent
    ]

if "overall_rating" not in st.session_state:
    st.session_state["overall_rating"] = 0

if "comments" not in st.session_state:
    st.session_state["comments"] = ""

# Function to get a response from the LLM using the latest OpenAI syntax
def get_llm_response(messages, model="gpt-4o-mini", temperature=0.3, max_tokens=500):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to handle sending messages
def send_message():
    user_message = st.session_state.user_input
    if user_message:
        st.session_state["chat_history"].append({"role": "user", "content": user_message})

        typing_placeholder = st.empty()
        typing_placeholder.markdown("**Agent typing...**")

        llm_response = get_llm_response(st.session_state["chat_history"])

        typing_placeholder.empty()

        st.session_state["chat_history"].append({"role": "assistant", "content": llm_response})

        st.session_state["user_input"] = ""

# Display chat history in a conversation-like format
for message in st.session_state["chat_history"]:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**Agent:** {message['content']}")

st.text_input("", key="user_input", on_change=send_message)

# if st.button("Clear Chat"):
#     # Reset chat history without a function
#     st.session_state["chat_history"] = [
#         {"role": "system", "content": agent_sys_txt},
#         {"role": "assistant", "content": "Hello, how can I help you?"}  # Initial greeting after clearing
#     ]

# Overall rating section
st.subheader("Rate the Agent")
st.slider(
    "How satisfied are you with this agent? 1 means very dissatisfied and 5 means very satisfied:",
    min_value=1,
    max_value=5,
    key="overall_rating",
    value=1  # Default rating value
)

# Comments section
st.subheader("Comments about the Agent")
st.text_area("Your comments:", key="comments", value="")  # Default empty text

# Button to submit rating and comments
if st.button("Submit Feedback"):
    connection = create_connection()
    cursor = connection.cursor()
    
    # Filter chat history to exclude the system message
    filtered_conversation = [
        message for message in st.session_state["chat_history"] if message["role"] != "system"
    ]
    conversation = json.dumps(filtered_conversation)
    
    # Get current timestamp
    feedback_time = datetime.now()
    
    # Insert feedback with timestamp into the database
    cursor.execute("""
        INSERT INTO user_feedback (user_id, conversation, rating, comments, feedback_time)
        VALUES (%s, %s, %s, %s, %s)
    """, (st.session_state.get("user_id", "anonymous"), conversation, st.session_state["overall_rating"], st.session_state["comments"], feedback_time))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    st.success("Thank you for your feedback!")

