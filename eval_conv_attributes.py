import streamlit as st
import pandas as pd
import psycopg2
import time
from datetime import datetime

########################################
# 1) Database Connection
########################################
def save_to_db(user_responses, start_time):
    try:
        conn = psycopg2.connect(
            dbname=st.secrets["database"]["DB_NAME"],
            user=st.secrets["database"]["DB_USER"],
            password=st.secrets["database"]["DB_PASSWORD"],
            host=st.secrets["database"]["DB_HOST"],
            port=st.secrets["database"]["DB_PORT"],
            sslmode="require"
        )
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rater_evaluations_gpt_3_5_turbo_0125_gpt_4 (
                    id SERIAL PRIMARY KEY,
                    conversation_index INTEGER,
                    reliability INTEGER,
                    assurance INTEGER,
                    empathy INTEGER,
                    responsiveness INTEGER,
                    start_time TIMESTAMP,
                    submission_time TIMESTAMP
                );
            """)
            
            insert_query = """
                INSERT INTO rater_evaluations_gpt_3_5_turbo_0125_gpt_4 
                (conversation_index, reliability, assurance, empathy, responsiveness, start_time, submission_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                    submission_time
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
    
    st.title("Service Quality Assessment: The RATER Framework")
    st.markdown("---")

    # Initialize Session States
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.now()
        # Also store as unix timestamp for easy math
        st.session_state["start_unix"] = time.time()
    
    if "viewed_indices" not in st.session_state:
        st.session_state["viewed_indices"] = set()

    # Load Local CSV
    if "df_local" not in st.session_state:
        try:
            st.session_state["df_local"] = pd.read_csv("gpt-3.5-turbo-0125-gpt-4-conversations.csv")
        except FileNotFoundError:
            st.error("CSV file not found. Ensure the filename matches exactly.")
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
        st.text_area("", value=row['conv'], height=600, disabled=True, key=f"text_display_{selection}")
    
    with col2:
        st.subheader("Performance Ratings")
        
        st.markdown("**Reliability**: Ability to perform the promised service dependably and accurately.")
        st.caption("*Key Indicators: Did the agent provide the correct solution? Was the information factually accurate? Did they follow through on promises?*")
        rel = st.select_slider("Rate Reliability", options=[1, 2, 3, 4, 5], key=f"rel_{selection}", value=5)
        
        st.write("---")

        st.markdown("**Assurance**: Knowledge and courtesy of employees and their ability to convey trust.")
        st.caption("*Key Indicators: Did the agent sound like an expert? Did they use professional language? Did the customer feel confident in the advice?*")
        assur = st.select_slider("Rate Assurance", options=[1, 2, 3, 4, 5], key=f"assur_{selection}", value=5)

        st.write("---")

        st.markdown("**Empathy**: Provision of caring, individualized attention to customers.")
        st.caption("*Key Indicators: Did the agent use the customer's name? Did they acknowledge feelings/frustration? Was the service personalized?*")
        emp = st.select_slider("Rate Empathy", options=[1, 2, 3, 4, 5], key=f"emp_{selection}", value=5)

        st.write("---")

        st.markdown("**Responsiveness**: Willingness to help customers and provide prompt service.")
        st.caption("*Key Indicators: Did the agent seem eager to assist? Was the response proactive? Did the agent take immediate ownership?*")
        resp = st.select_slider("Rate Responsiveness", options=[1, 2, 3, 4, 5], key=f"resp_{selection}", value=5)

    # Gather data
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
            # Calculate elapsed time
            current_time = time.time()
            elapsed_seconds = current_time - st.session_state["start_unix"]
            
            if elapsed_seconds < 180:
                # Warning for fast submission (less than 1 min)
                st.error("⚠️ **Submission Error: Review Time Too Short**")
                st.warning(f"""
                Please read the conversations carefully before you rate them. 
                Our research parameters require a thorough review of the transcripts. 
                
                **Note:** Careless or automated submissions will not be counted. 
                Please take another {int(60 - elapsed_seconds)} seconds to verify your ratings.
                """)
            else:
                success = save_to_db(all_data_to_submit, st.session_state["start_time"])
                if success:
                    st.success("Evaluations successfully submitted to the database!")
                    st.balloons()
    else:
        st.button(f"Submit Disabled (Review {4-progress} more)", type="secondary", use_container_width=True, disabled=True)

if __name__ == "__main__":
    main()
