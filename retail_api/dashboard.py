import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Retail Dashboard",
    layout="wide"
)

st.title("🏪 Apex Retail Live Dashboard")

placeholder = st.empty()

while True:

    try:

        metrics = requests.get(
            "http://127.0.0.1:8000/stores/STORE_BLR_002/metrics"
        ).json()

        with placeholder.container():

            st.metric(
                "Unique Visitors",
                metrics["unique_visitors"]
            )

            st.metric(
                "Average Dwell (ms)",
                metrics["avg_dwell_ms"]
            )

            st.metric(
                "Queue Depth",
                metrics["queue_depth"]
            )

    except Exception as e:

        st.error(str(e))

    time.sleep(2)