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

    # --- CUSTOM CSS ---
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
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Service Quality Assessment")

    st.markdown("---")

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.now()
        st.session_state["start_unix"] = time.time()

    if "viewed_indices" not in st.session_state:
        st.session_state["viewed_indices"] = set()

    if "df_local" not in st.session_state:
        try:
            st.session_state["df_local"] = pd.read_csv("gpt-3.5-turbo-0125-gpt-4-0613-conversations.csv")
        except FileNotFoundError:
            st.error("CSV file not found.")
            return

    df_sampled = st.session_state.get("df_sampled")
    if df_sampled is None:
        st.session_state["df_sampled"] = st.session_state["df_local"].sample(n=4).reset_index()
        df_sampled = st.session_state["df_sampled"]

    st.sidebar.header("Navigation")
    selection = st.sidebar.radio(
        "Select Conversation:",
        options=[0, 1, 2, 3],
        format_func=lambda x: f"Conversation {x+1}"
    )
    st.session_state["viewed_indices"].add(selection)

    progress = len(st.session_state["viewed_indices"])
    st.sidebar.progress(progress / 4)
    st.sidebar.write(f"Progress: {progress} / 4 Reviewed")

    row = df_sampled.iloc[selection]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Agent – Customer Conversation")
        st.markdown(f'<div class="transcript-box">{row["conversation"]}</div>', unsafe_allow_html=True)

    rating_labels = {
        1: "1 – Very dissatisfied",
        2: "2 – Dissatisfied",
        3: "3 – Neutral",
        4: "4 – Satisfied",
        5: "5 – Very satisfied",
    }

    with col2:
        st.subheader("Performance Ratings")

        st.markdown("**Reliability**")
        rel = st.radio(
            "Rate Reliability",
            options=[1, 2, 3, 4, 5],
            index=None,
            key=f"rel_{selection}",
            horizontal=True,
            format_func=lambda x: rating_labels[x]
        )

        st.write("---")
        st.markdown("**Assurance**")
        assur = st.radio(
            "Rate Assurance",
            options=[1, 2, 3, 4, 5],
            index=None,
            key=f"assur_{selection}",
            horizontal=True,
            format_func=lambda x: rating_labels[x]
        )

        st.write("---")
        st.markdown("**Empathy**")
        emp = st.radio(
            "Rate Empathy",
            options=[1, 2, 3, 4, 5],
            index=None,
            key=f"emp_{selection}",
            horizontal=True,
            format_func=lambda x: rating_labels[x]
        )

        st.write("---")
        st.markdown("**Responsiveness**")
        resp = st.radio(
            "Rate Responsiveness",
            options=[1, 2, 3, 4, 5],
            index=None,
            key=f"resp_{selection}",
            horizontal=True,
            format_func=lambda x: rating_labels[x]
        )

    if progress >= 4:
        elapsed_seconds = time.time() - st.session_state["start_unix"]

        if st.button("Submit All Evaluations", type="primary", use_container_width=True):
            if elapsed_seconds < 180:
                st.error("⚠️ Please spend more time reviewing before submitting.")
            else:
                for i in range(4):
                    for dim in ["rel", "assur", "emp", "resp"]:
                        if st.session_state.get(f"{dim}_{i}") is None:
                            st.error("⚠️ Please rate all dimensions for all conversations.")
                            st.stop()

                all_data = []
                for i in range(4):
                    all_data.append({
                        "conversation_index": df_sampled.iloc[i]["index"],
                        "reliability": st.session_state[f"rel_{i}"],
                        "assurance": st.session_state[f"assur_{i}"],
                        "empathy": st.session_state[f"emp_{i}"],
                        "responsiveness": st.session_state[f"resp_{i}"],
                    })

                if save_to_db(all_data, st.session_state["start_time"], elapsed_seconds):
                    st.success("Evaluations successfully submitted!")
                    st.balloons()
    else:
        st.button(
            f"Submit Disabled (Review {4-progress} more)",
            disabled=True,
            use_container_width=True
        )

if __name__ == "__main__":
    main()
