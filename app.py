import streamlit as st
import openai

# Configure your OpenAI API key or another LLM backend
openai.api_key = my_key # Replace with your OpenAI key or connect to another LLM provider

# Configure Streamlit app layout
st.set_page_config(page_title="LLM Chat Interface", layout="centered")

st.title("LLM Chat Interface")
st.write("Chat with an agent in a continuous conversation.")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [{"role": "system", "content": "You are a helpful assistant."}]

# Function to get a response from the LLM using the latest OpenAI syntax
def get_llm_response(messages, model="gpt-4o-mini", temperature=0.3, max_tokens=150):
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

        # Get LLM response based on conversation history
        llm_response = get_llm_response(st.session_state["chat_history"])

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
st.text_input("Start a conversation with a customer support agent", key="user_input", on_change=send_message)

# Clear chat history button
if st.button("Clear Chat"):
    # Reset chat history to initial system message
    st.session_state["chat_history"] = [{"role": "system", "content": "You are a helpful assistant."}]
