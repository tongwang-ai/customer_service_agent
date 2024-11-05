import streamlit as st
import openai
import my_prompts

# Configure your OpenAI API key or another LLM backend
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configure Streamlit app layout
st.set_page_config(page_title="LLM Chat Interface", layout="centered")

st.title("Live Chat with a Customer Service Agent")
# st.write("Chat with an agent")

# Initialize session state for chat history
agent_sys_txt = my_prompts.AGENT_PROMPT_TICKET + my_prompts.AIRLINE_POLICY_TICKET

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "system", "content": agent_sys_txt},
        {"role": "assistant", "content": "Hello, how can I help you?"}  # Initial greeting from the agent
    ]

# Function to get a response from the LLM using the latest OpenAI syntax
def get_llm_response(messages, model="gpt-3.5-turbo", temperature=0.3, max_tokens=150):
    try:
        # Use OpenAI's chat completion with correct parameters
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # Access the content of the LLM response correctly
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to handle sending messages
def send_message():
    user_message = st.session_state.user_input
    if user_message:
        # Add user's message to chat history
        st.session_state["chat_history"].append({"role": "user", "content": user_message})

        # Show typing indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown("**Agent typing...**")

        # Get LLM response based on conversation history
        llm_response = get_llm_response(st.session_state["chat_history"])

        # Clear typing indicator
        typing_placeholder.empty()

        # Add LLM response to chat history
        st.session_state["chat_history"].append({"role": "assistant", "content": llm_response})

        # Clear user input field after sending
        st.session_state["user_input"] = ""

# Display chat history in a conversation-like format
for message in st.session_state["chat_history"]:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**Agent:** {message['content']}")

# Text input field with `on_change` to send message on "Enter"
st.text_input("", key="user_input", on_change=send_message)

# Clear chat history button
if st.button("Clear Chat"):
    # Reset chat history to initial system message and greeting
    st.session_state["chat_history"] = [
        {"role": "system", "content": agent_sys_txt},
        {"role": "assistant", "content": "Hello, how can I help you?"}  # Initial greeting after clearing
    ]
