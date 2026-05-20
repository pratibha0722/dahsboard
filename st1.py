import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Conference Feedback Dashboard",
    page_icon="🎤",
    layout="wide"
)

# =========================================================
# READ EXCEL DIRECTLY
# =========================================================

EXCEL_FILE = "FeedBack Result_All_day1_3dayEidt.xlsx"

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    # Read excel file
    df = pd.read_excel(EXCEL_FILE)

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Handle duplicate Question column
    if "Question.1" in df.columns:
        df.rename(columns={"Question.1": "Category"}, inplace=True)

    # If category missing
    if "Category" not in df.columns:
        df["Category"] = "General"

    # Convert Answer column to numeric
    df["Answer"] = pd.to_numeric(df["Answer"], errors="coerce")

    # Fill missing values
    fill_cols = [
        "ConferenceName",
        "ProgramName",
        "SessionName",
        "NameOfSpeaker",
        "Topic",
        "FullName",
        "Question",
        "Category"
    ]

    for col in fill_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df


df = load_data()

# =========================================================
# TITLE
# =========================================================
st.title("🎤 Conference Feedback Analytics Dashboard")
st.markdown("Interactive PowerBI-style conference feedback dashboard")

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🔍 Dashboard Filters")

conference_filter = st.sidebar.multiselect(
    "Conference",
    options=sorted(df["ConferenceName"].unique()),
    default=sorted(df["ConferenceName"].unique())
)

program_filter = st.sidebar.multiselect(
    "Program / Day",
    options=sorted(df["ProgramName"].unique()),
    default=sorted(df["ProgramName"].unique())
)

session_filter = st.sidebar.multiselect(
    "Session",
    options=sorted(df["SessionName"].unique()),
    default=sorted(df["SessionName"].unique())
)

speaker_filter = st.sidebar.multiselect(
    "Speaker",
    options=sorted(df["NameOfSpeaker"].unique()),
    default=sorted(df["NameOfSpeaker"].unique())
)

category_filter = st.sidebar.multiselect(
    "Feedback Category",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

# =========================================================
# FILTER DATA
# =========================================================
filtered_df = df[
    (df["ConferenceName"].isin(conference_filter)) &
    (df["ProgramName"].isin(program_filter)) &
    (df["SessionName"].isin(session_filter)) &
    (df["NameOfSpeaker"].isin(speaker_filter)) &
    (df["Category"].isin(category_filter))
]

# =========================================================
# KPI SECTION
# =========================================================
st.subheader("📌 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

avg_rating = round(filtered_df["Answer"].mean(), 2)
total_feedback = len(filtered_df)
total_speakers = filtered_df["NameOfSpeaker"].nunique()
total_sessions = filtered_df["SessionName"].nunique()
total_attendees = filtered_df["FullName"].nunique()

col1.metric("⭐ Avg Rating", avg_rating)
col2.metric("📝 Feedback", total_feedback)
col3.metric("🎤 Speakers", total_speakers)
col4.metric("📚 Sessions", total_sessions)
col5.metric("👥 Attendees", total_attendees)

st.divider()

# =========================================================
# ROW 1
# =========================================================
col1, col2 = st.columns(2)

with col1:

    st.subheader("⭐ Average Rating by Speaker")

    speaker_rating = (
        filtered_df
        .groupby("NameOfSpeaker")["Answer"]
        .mean()
        .reset_index()
        .sort_values(by="Answer", ascending=False)
    )

    fig1 = px.bar(
        speaker_rating,
        x="Answer",
        y="NameOfSpeaker",
        orientation="h",
        text_auto=".2f",
        color="Answer",
        color_continuous_scale="Blues"
    )

    fig1.update_layout(height=600)

    st.plotly_chart(fig1, use_container_width=True)

with col2:

    st.subheader("📈 Rating Distribution")

    fig2 = px.histogram(
        filtered_df,
        x="Answer",
        color="Category",
        barmode="group",
        nbins=5
    )

    fig2.update_layout(height=600)

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# ROW 2
# =========================================================
col3, col4 = st.columns(2)

with col3:

    st.subheader("📚 Session Performance")

    session_rating = (
        filtered_df
        .groupby("SessionName")["Answer"]
        .mean()
        .reset_index()
        .sort_values(by="Answer", ascending=False)
    )

    fig3 = px.bar(
        session_rating,
        x="SessionName",
        y="Answer",
        text_auto=".2f",
        color="Answer",
        color_continuous_scale="Viridis"
    )

    fig3.update_layout(
        xaxis_tickangle=-45,
        height=650
    )

    st.plotly_chart(fig3, use_container_width=True)

with col4:

    st.subheader("📅 Program / Day Analysis")

    day_rating = (
        filtered_df
        .groupby("ProgramName")["Answer"]
        .mean()
        .reset_index()
    )

    fig4 = px.line(
        day_rating,
        x="ProgramName",
        y="Answer",
        markers=True
    )

    fig4.update_layout(height=650)

    st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# HEATMAP
# =========================================================
st.subheader("🔥 Speaker vs Category Heatmap")

heatmap_data = (
    filtered_df
    .pivot_table(
        index="NameOfSpeaker",
        columns="Category",
        values="Answer",
        aggfunc="mean"
    )
)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdYlGn"
)

fig_heatmap.update_layout(height=700)

st.plotly_chart(fig_heatmap, use_container_width=True)

# =========================================================
# TOPIC ANALYTICS
# =========================================================
st.subheader("📖 Topic Analytics")

col5, col6 = st.columns(2)

with col5:

    topic_rating = (
        filtered_df
        .groupby("Topic")["Answer"]
        .mean()
        .reset_index()
        .sort_values(by="Answer", ascending=False)
    )

    fig5 = px.treemap(
        topic_rating,
        path=["Topic"],
        values="Answer",
        color="Answer",
        color_continuous_scale="Teal"
    )

    fig5.update_layout(height=700)

    st.plotly_chart(fig5, use_container_width=True)

with col6:

    fig6 = px.sunburst(
        filtered_df,
        path=["ProgramName", "SessionName", "NameOfSpeaker"],
        values="Answer",
        color="Answer",
        color_continuous_scale="Plasma"
    )

    fig6.update_layout(height=700)

    st.plotly_chart(fig6, use_container_width=True)

# =========================================================
# SPEAKER DRILLDOWN
# =========================================================
st.subheader("🎤 Speaker Drilldown")

selected_speaker = st.selectbox(
    "Select Speaker",
    sorted(filtered_df["NameOfSpeaker"].unique())
)

speaker_df = filtered_df[
    filtered_df["NameOfSpeaker"] == selected_speaker
]

col7, col8 = st.columns([1, 2])

with col7:

    st.metric(
        "Average Rating",
        round(speaker_df["Answer"].mean(), 2)
    )

    st.metric(
        "Total Reviews",
        len(speaker_df)
    )

    category_avg = (
        speaker_df
        .groupby("Category")["Answer"]
        .mean()
        .reset_index()
    )

    fig7 = px.pie(
        category_avg,
        names="Category",
        values="Answer"
    )

    st.plotly_chart(fig7, use_container_width=True)

with col8:

    topic_speaker = (
        speaker_df
        .groupby("Topic")["Answer"]
        .mean()
        .reset_index()
    )

    fig8 = px.bar(
        topic_speaker,
        x="Topic",
        y="Answer",
        text_auto=".2f",
        color="Answer",
        color_continuous_scale="Sunset"
    )

    fig8.update_layout(
        xaxis_tickangle=-30,
        height=550
    )

    st.plotly_chart(fig8, use_container_width=True)

# =========================================================
# TOP SPEAKERS
# =========================================================
st.subheader("🏆 Top Performing Speakers")

top_speakers = (
    filtered_df
    .groupby("NameOfSpeaker")
    .agg(
        Average_Rating=("Answer", "mean"),
        Feedback_Count=("Answer", "count")
    )
    .reset_index()
)

top_speakers = top_speakers.sort_values(
    by="Average_Rating",
    ascending=False
)

fig9 = px.scatter(
    top_speakers,
    x="Feedback_Count",
    y="Average_Rating",
    size="Feedback_Count",
    color="Average_Rating",
    hover_name="NameOfSpeaker",
    text="NameOfSpeaker"
)

fig9.update_traces(textposition="top center")

fig9.update_layout(height=700)

st.plotly_chart(fig9, use_container_width=True)

# =========================================================
# TREND ANALYSIS
# =========================================================
st.subheader("📊 Session Trend Analysis")

trend_data = (
    filtered_df
    .groupby(["SessionName", "Category"])["Answer"]
    .mean()
    .reset_index()
)

fig10 = px.line(
    trend_data,
    x="SessionName",
    y="Answer",
    color="Category",
    markers=True
)

fig10.update_layout(
    xaxis_tickangle=-45,
    height=650
)

st.plotly_chart(fig10, use_container_width=True)

# =========================================================
# RAW DATA
# =========================================================
st.subheader("📄 Raw Feedback Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)

# =========================================================
# DOWNLOAD CSV
# =========================================================
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_feedback.csv",
    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================
st.divider()

st.success("✅ Dashboard Loaded Successfully")