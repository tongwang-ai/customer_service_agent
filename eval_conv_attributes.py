import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

########################################
# 1) Database Connection
########################################
def save_to_db(user_responses, start_time):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="tongwang",
            password="TWluckygirlno01!",
            host="streamlit-app.ch8aw0oiyxfa.us-east-2.rds.amazonaws.com",
            port="5432",
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
    
    # Track which conversations have been viewed
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
    
    # Update progress tracking
    st.session_state["viewed_indices"].add(selection)
    progress = len(st.session_state["viewed_indices"])

    st.sidebar.markdown("---")
    st.sidebar.write(f"**Progress: {progress} / 4 Reviewed**")
    st.sidebar.progress(progress / 4)
    st.sidebar.info("The 'Submit' button will activate once all 4 conversations have been reviewed.")

    # --- Display Selected Conversation ---
    row = df_sampled.iloc[selection]
    orig_idx = row['index']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"Agent - Customer Conversation (Sample {selection + 1})")
        st.text_area("", value=row['conv'], height=600, disabled=True, key=f"text_display_{selection}")
    
    with col2:
        st.subheader("Performance Ratings")
        
        # 1. Reliability
        st.markdown("**Reliability**: Ability to perform the promised service dependably and accurately.")
        st.caption("*Key Indicators: Did the agent provide the correct solution? Was the information factually accurate? Did they follow through on promises?*")
        rel = st.select_slider("Rate Reliability", options=[1, 2, 3, 4, 5], key=f"rel_{selection}", value=5)
        
        st.write("---")

        # 2. Assurance
        st.markdown("**Assurance**: Knowledge and courtesy of employees and their ability to convey trust.")
        st.caption("*Key Indicators: Did the agent sound like an expert? Did they use professional language? Did the customer feel confident in the advice?*")
        assur = st.select_slider("Rate Assurance", options=[1, 2, 3, 4, 5], key=f"assur_{selection}", value=5)

        st.write("---")

        # 3. Empathy
        st.markdown("**Empathy**: Provision of caring, individualized attention to customers.")
        st.caption("*Key Indicators: Did the agent use the customer's name? Did they acknowledge feelings/frustration? Was the service personalized?*")
        emp = st.select_slider("Rate Empathy", options=[1, 2, 3, 4, 5], key=f"emp_{selection}", value=5)

        st.write("---")

        # 4. Responsiveness
        st.markdown("**Responsiveness**: Willingness to help customers and provide prompt service.")
        st.caption("*Key Indicators: Did the agent seem eager to assist? Was the response proactive? Did the agent take immediate ownership?*")
        resp = st.select_slider("Rate Responsiveness", options=[1, 2, 3, 4, 5], key=f"resp_{selection}", value=5)

    # Gather data from session state for all 4 samples
    all_data_to_submit = []
    for i in range(4):
        # We fetch current slider values from session state, defaulting to 5 if not touched
        all_data_to_submit.append({
            "conversation_index": df_sampled.iloc[i]['index'],
            "reliability": st.session_state.get(f"rel_{i}", 5),
            "assurance": st.session_state.get(f"assur_{i}", 5),
            "empathy": st.session_state.get(f"emp_{i}", 5),
            "responsiveness": st.session_state.get(f"resp_{i}", 5)
        })

    st.markdown("---")
    
    # --- Final Submission Logic ---
    if progress >= 4:
        if st.button("Submit All Evaluations", type="primary", use_container_width=True):
            success = save_to_db(all_data_to_submit, st.session_state["start_time"])
            if success:
                st.success("Evaluations successfully submitted to the database!")
                st.balloons()
    else:
        st.button(f"Submit Disabled (Review {4-progress} more)", type="secondary", use_container_width=True, disabled=True)

if __name__ == "__main__":
    main()