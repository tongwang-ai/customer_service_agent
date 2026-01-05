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
        # Standard Streamlit secrets access: st.secrets["DB_NAME"] 
        # or st.secrets["database"]["DB_NAME"] depending on your secrets.toml
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
                CREATE TABLE IF NOT EXISTS rater_evaluations_gpt_3_5_turbo_0125_gpt_4_0613 (
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
                INSERT INTO rater_evaluations_gpt_3_5_turbo_0125_gpt_4_0613 
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
    st.set_page_config(page_title="RATER Evaluation Tool", layout="wide")
    
    # --- Instructions Section (Moved to very top) ---
    st.title("Service Quality Assessment: The RATER Framework")
    
    with st.expander("📝 View Instructions & Evaluation Criteria", expanded=True):
        st.markdown("""
        ### Welcome to the Agent Performance Survey
        In this study, you will evaluate **4 unique conversations** between a customer service agent and a client. 
        Your goal is to assess the agent's performance using the **RATER Framework**, a validated academic model for measuring service quality.

        **Guidelines:**
        1. **Read Carefully:** Please read the full transcript for each conversation before providing ratings.
        2. **Standard of Excellence:** The default rating is set to **5 (Excellent)**. Please adjust the sliders if the agent's performance falls below this standard.
        3. **Quality Control:** To ensure data integrity, the system requires a minimum of **3 minutes** to review the material before submission is allowed.
        4. **Dimensions:** You will rate each agent on *Reliability, Assurance, Empathy,* and *Responsiveness*.
        """)

    st.markdown("---")

    # Initialize Session States
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.now()
        st.session_state["start_unix"] = time.time()
    
    if "viewed_indices" not in st.session_state:
        st.session_state["viewed_indices"] = set()

    # Load Local CSV
    if "df_local" not in st.session_state:
        try:
            # Check filename: verify it matches exactly on your computer
            st.session_state["df_local"] = pd.read_csv("gpt-3.5-turbo-0125-gpt-4-0613-conversations.csv")
        except FileNotFoundError:
            st.error("CSV file not found. Ensure 'gpt-3.5-turbo-0125-gpt-4-0613-conversations.csv' is in the app folder.")
            return

    # Sample 4
    if "df_sampled" not in st.session_state:
        st.session_state["df_sampled"] = st.session_state["df_local"].sample(n=4).reset_index()

    df_sampled = st.session_state["df_sampled"]

    # --- Sidebar Navigation ---
    st.sidebar.header("Navigation")
    selection = st.sidebar.radio(
        "Select Conversation to Rate:",
        options=[0, 1, 2, 3],
        format_func=lambda x: f"Conversation {x+1}"
    )
    
    st.session_state["viewed_indices"].add(selection)
    progress = len(st.session_state["viewed_indices"])

    st.sidebar.markdown("---")
    st.sidebar.write(f"**Progress: {progress} / 4 Reviewed**")
    st.sidebar.progress(progress / 4)
    
    # --- Display Selected Conversation ---
    row = df_sampled.iloc[selection]
    orig_idx = row['index']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"Agent - Customer Conversation (Sample {selection + 1})")
        # Ensure 'conv' is the correct column name in your CSV
        st.text_area("", value=row['conv'], height=600, disabled=True, key=f"text_display_{selection}")
    
    with col2:
        st.subheader("Performance Ratings")
        
        # 1. Reliability
        st.markdown("**Reliability**: Ability to perform the promised service dependably and accurately.")
        st.caption("*Key Indicators: Correct solution, factual accuracy, following through on promises.*")
        rel = st.select_slider("Rate Reliability", options=[1, 2, 3, 4, 5], key=f"rel_{selection}", value=5)
        
        st.write("---")

        # 2. Assurance
        st.markdown("**Assurance**: Knowledge and courtesy of employees and their ability to convey trust.")
        st.caption("*Key Indicators: Expertise, professional language, customer confidence.*")
        assur = st.select_slider("Rate Assurance", options=[1, 2, 3, 4, 5], key=f"assur_{selection}", value=5)

        st.write("---")

        # 3. Empathy
        st.markdown("**Empathy**: Provision of caring, individualized attention to customers.")
        st.caption("*Key Indicators: Using name, acknowledging feelings, personalization.*")
        emp = st.select_slider("Rate Empathy", options=[1, 2, 3, 4, 5], key=f"emp_{selection}", value=5)

        st.write("---")

        # 4. Responsiveness
        st.markdown("**Responsiveness**: Willingness to help customers and provide prompt service.")
        st.caption("*Key Indicators: Eagerness to assist, proactivity, ownership.*")
        resp = st.select_slider("Rate Responsiveness", options=[1, 2, 3, 4, 5], key=f"resp_{selection}", value=5)

    # Gather data from all sessions
    all_data_to_submit = []
    for i in range(4):
        all_data_to_submit.append({
            "conversation_index": df_sampled.iloc[i]['index'],
            "reliability": st.session_state.get(f"rel_{i}", 5),
            "assurance": st.session_state.get(f"assur_{i}", 5),
            "empathy": st.session_state.get(f"emp_{i}", 5),
            "responsiveness": st.session_state.get(f"resp_{i}", 5)
        })

    st.markdown("---")
    
    # --- Quality Control & Submission Logic ---
    if progress >= 4:
        if st.button("Submit All Evaluations", type="primary", use_container_width=True):
            current_time = time.time()
            elapsed_seconds = current_time - st.session_state["start_unix"]
            
            if elapsed_seconds < 180:
                st.error("⚠️ **Submission Error: Review Time Too Short**")
                st.warning(f"Careless submissions will not be counted. Please take another {int(180 - elapsed_seconds)} seconds to review.")
            else:
                success = save_to_db(all_data_to_submit, st.session_state["start_time"], elapsed_seconds)
                if success:
                    st.success("Evaluations successfully submitted to the database!")
                    st.balloons()
    else:
        st.button(f"Submit Disabled (Review {4-progress} more)", type="secondary", use_container_width=True, disabled=True)

if __name__ == "__main__":
    main()
