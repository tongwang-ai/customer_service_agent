import streamlit as st
import pandas as pd
import psycopg2
import time
from datetime import datetime

########################################
# 1) Database Connection
########################################
def save_to_db(user_responses, start_time, elapsed_seconds):
    try:
        conn = psycopg2.connect(
            dbname=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            sslmode="require"
        )
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rater_evaluations_llama_2_13b_chat_gpt_4_0613 (
                    id SERIAL PRIMARY KEY,
                    conversation_index INTEGER,
                    reliability INTEGER,
                    assurance INTEGER,
                    empathy INTEGER,
                    responsiveness INTEGER,
                    start_time TIMESTAMP,
                    submission_time TIMESTAMP,
                    seconds_spent INTEGER
                );
            """)
            
            insert_query = """
                INSERT INTO rater_evaluations_llama_2_13b_chat_gpt_4_0613 
                (conversation_index, reliability, assurance, empathy, responsiveness, start_time, submission_time, seconds_spent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            submission_time = datetime.now()
            for resp in user_responses:
                cur.execute(insert_query, (
                    int(resp["conversation_index"]), 
                    resp["reliability"],
                    resp["assurance"],
                    resp["empathy"],
                    resp["responsiveness"],
                    start_time, 
                    submission_time,
                    int(elapsed_seconds)
                ))
            
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

########################################
# 2) Main Streamlit App
########################################
def main():
    st.set_page_config(page_title="Customer Service Agent Evaluation", layout="wide")
    
    # --- CUSTOM CSS FOR HIGH CONTRAST ---
    st.markdown("""
        <style>
        .transcript-box {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #d1d1d1;
            height: 600px;
            overflow-y: scroll;
            font-family: 'Source Sans Pro', sans-serif;
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Service Quality Assessment")
    
    with st.expander("📝 View Instructions & Evaluation Criteria", expanded=True):
        st.markdown("""
        ### Welcome to the Agent Performance Survey
        You are a customer who has just finished an interaction with a service agent. You are not a professional evaluator; you are a person with a specific problem who wants to feel heard and helped. 

        ### YOUR EVALUATION MINDSET
        When reading the transcript, imagine yourself as the customer. Do not look for "technical checkboxes." Instead, ask yourself: 
        - "Did I get what I needed?" (Reliability)
        - "Did I feel like I was in good hands?" (Assurance)
        - "Did I feel like a human being or just a number?" (Empathy)
        - "Did I feel like the agent actually wanted to help me?" (Responsiveness)
    
        ### RATER DIMENSIONS (Customer Interpretation)
        Rate the following from 1 to 5 (**1 = Very Dissatisfied, 5 = Very Satisfied**):
    
        1. **Reliability** (Ability to perform the promised service dependably and accurately): Did the agent actually solve my problem correctly and do what they said they would do? (Key Indicators: Correct solution, factual accuracy, following through on promises.)
        2. **Assurance** (Knowledge and courtesy of employees and their ability to convey trust): Did the agent sound like they knew what they were doing? Did I trust the information they gave me? (Key Indicators: Expertise, professional language, customer confidence.)
        3. **Empathy** (Provision of caring, individualized attention to customers): Did the agent seem to care about my situation? Did they listen to my specific concerns? (Key Indicators: Using name, acknowledging feelings, personalization.)
        4. **Responsiveness** (Willingness to help customers and provide prompt service): How was the agent's "energy"? Did they respond quickly and show an eagerness to resolve my issue? (Key Indicators: Eagerness to assist, proactivity, ownership.)

        """)

    st.markdown("---")

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.now()
        st.session_state["start_unix"] = time.time()
    
    if "viewed_indices" not in st.session_state:
        st.session_state["viewed_indices"] = set()

    # Load Local CSV
    if "df_local" not in st.session_state:
        try:
            st.session_state["df_local"] = pd.read_csv("llama-2-13b-chat-gpt-4-0613-conversations.csv")
        except FileNotFoundError:
            st.error("CSV file not found.")
            return

    df_sampled = st.session_state.get("df_sampled")
    if df_sampled is None:
        st.session_state["df_sampled"] = st.session_state["df_local"].sample(n=4).reset_index()
        df_sampled = st.session_state["df_sampled"]

    # Sidebar
    st.sidebar.header("Navigation")
    selection = st.sidebar.radio("Select Conversation:", options=[0, 1, 2, 3], format_func=lambda x: f"Conversation {x+1}")
    st.session_state["viewed_indices"].add(selection)
    
    progress = len(st.session_state["viewed_indices"])
    st.sidebar.progress(progress / 4)
    st.sidebar.write(f"Progress: {progress} / 4 Reviewed")
    
    # Display Content
    row = df_sampled.iloc[selection]
    orig_idx = row['index']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Agent - Customer Conversation")
        # --- IMPROVED READABILITY BOX ---
        # Using a Div instead of a text_area to avoid the "disabled gray" look
        transcript_html = f'<div class="transcript-box">{row["conversation"]}</div>'
        st.markdown(transcript_html, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Performance Ratings")
        
        st.markdown("**Reliability**: Ability to perform the promised service dependably and accurately.")
        st.caption("*Key Indicators: Correct solution, factual accuracy, following through on promises.*")
        rel = st.select_slider("Rate Reliability", options=[1, 2, 3, 4, 5], key=f"rel_{selection}", value=5)
        
        st.write("---")
        st.markdown("**Assurance**: Knowledge and courtesy of employees and their ability to convey trust.")
        st.caption("*Key Indicators: Expertise, professional language, customer confidence.*")
        assur = st.select_slider("Rate Assurance", options=[1, 2, 3, 4, 5], key=f"assur_{selection}", value=5)

        st.write("---")
        st.markdown("**Empathy**: Provision of caring, individualized attention to customers.")
        st.caption("*Key Indicators: Using name, acknowledging feelings, personalization.*")
        emp = st.select_slider("Rate Empathy", options=[1, 2, 3, 4, 5], key=f"emp_{selection}", value=5)

        st.write("---")
        st.markdown("**Responsiveness**: Willingness to help customers and provide prompt service.")
        st.caption("*Key Indicators: Eagerness to assist, proactivity, ownership.*")
        resp = st.select_slider("Rate Responsiveness", options=[1, 2, 3, 4, 5], key=f"resp_{selection}", value=5)

    # Submission Logic
    if progress >= 4:
        current_time = time.time()
        elapsed_seconds = current_time - st.session_state["start_unix"]
        
        if st.button("Submit All Evaluations", type="primary", use_container_width=True):
            if elapsed_seconds < 180:
                st.error(f"⚠️ **Too Fast!** Please take another {int(180 - elapsed_seconds)} seconds to review carefully.")
            else:
                # Gather data
                all_data = []
                for i in range(4):
                    all_data.append({
                        "conversation_index": df_sampled.iloc[i]['index'],
                        "reliability": st.session_state.get(f"rel_{i}", 5),
                        "assurance": st.session_state.get(f"assur_{i}", 5),
                        "empathy": st.session_state.get(f"emp_{i}", 5),
                        "responsiveness": st.session_state.get(f"resp_{i}", 5)
                    })
                if save_to_db(all_data, st.session_state["start_time"], elapsed_seconds):
                    st.success("Evaluations successfully submitted!")
                    st.balloons()
    else:
        st.button(f"Submit Disabled (Review {4-progress} more)", type="secondary", use_container_width=True, disabled=True)

if __name__ == "__main__":
    main()
