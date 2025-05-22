import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Proposal & Collaboration Maps", layout="wide")

st.title("Proposal/Collaboration Mapping Dashboard")

# --- DATA LOAD ---
file_path = "MAPS_EXCELSIOR_cleaned.xlsx"  # Place this Excel file in the same folder as this script
df = pd.read_excel(file_path)

# --- EMMENA REGION ---
emmena_countries = [
    'Cyprus', 'Greece', 'Turkey', 'Syria', 'Lebanon', 'Israel', 'Palestine', 'Jordan',
    'Egypt', 'Saudi Arabia', 'United Arab Emirates', 'Oman', 'Qatar', 'Bahrain', 'Kuwait', 'Yemen', 'Iraq', 'Iran',
    'Algeria', 'Morocco', 'Tunisia', 'Libya', 'Sudan'
]

# --- FILTERS ---
st.sidebar.header("Filters")
region = st.sidebar.selectbox(
    "Region",
    ["All Countries", "EMMENA Only"]
)
funding_options = ["All", "Funded Only", "Not Funded Only"]
funded_filter = st.sidebar.selectbox(
    "Show Only...",
    funding_options
)
chart_type = st.sidebar.selectbox(
    "Chart Type",
    [
        "Choropleth Map",
        "Bubble Map",
        "Bar Chart",
        "Lollipop Chart",
        "Small Multiples (Funded vs Not Funded)"
    ]
)

# --- DATA FILTERING ---
data = df.copy()
if region == "EMMENA Only":
    data = data[data["Country"].isin(emmena_countries)]

if funded_filter == "Funded Only":
    data = data[data["Funded"].str.lower().isin(["yes", "funded"])]
elif funded_filter == "Not Funded Only":
    data = data[data["Funded"].str.lower() == "no"]

# --- AGGREGATION ---
counts = data.groupby("Country").size().reset_index(name="num_proposals")

# --- CHOROPLETH MAP ---
if chart_type == "Choropleth Map":
    fig = px.choropleth(
        counts,
        locations="Country",
        locationmode="country names",
        color="num_proposals",
        hover_name="Country",
        color_continuous_scale="YlGnBu",
        title="Number of Proposals by Country"
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True), margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- BUBBLE MAP ---
elif chart_type == "Bubble Map":
    fig = px.scatter_geo(
        counts,
        locations="Country",
        locationmode="country names",
        size="num_proposals",
        projection="natural earth",
        hover_name="Country",
        title="Bubble Map of Proposals by Country"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- BAR CHART ---
elif chart_type == "Bar Chart":
    top = counts.sort_values("num_proposals", ascending=True)
    fig = px.bar(
        top,
        x="num_proposals",
        y="Country",
        orientation="h",
        title="Number of Proposals by Country"
    )
    fig.update_layout(margin=dict(l=100, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# --- LOLLIPOP CHART ---
elif chart_type == "Lollipop Chart":
    top = counts.sort_values("num_proposals", ascending=True)
    fig = go.Figure()
    for _, row in top.iterrows():
        fig.add_shape(
            type="line",
            x0=0, x1=row.num_proposals,
            y0=row.Country, y1=row.Country,
            line=dict(width=2, color="gray")
        )
    fig.add_trace(go.Scatter(
        x=top.num_proposals,
        y=top.Country,
        mode="markers",
        marker=dict(size=10, color="crimson"),
        hovertemplate="%{y}: %{x}<extra></extra>"
    ))
    fig.update_layout(
        title="Lollipop Chart of Proposals",
        xaxis_title="Proposals",
        yaxis=dict(tickmode="linear"),
        margin=dict(l=100, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- SMALL MULTIPLES ---
elif chart_type == "Small Multiples (Funded vs Not Funded)":
    counts2 = (
        data.groupby(["Funded", "Country"])
        .size()
        .reset_index(name="count")
    )
    fig = px.choropleth(
        counts2,
        locations="Country",
        locationmode="country names",
        color="count",
        facet_col="Funded",
        color_continuous_scale="YlGnBu",
        title="Proposals by Country: Funded Status"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- DATA DOWNLOAD ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Download Filtered Data")
st.sidebar.download_button(
    "Download as CSV",
    counts.to_csv(index=False).encode(),
    file_name="filtered_counts.csv",
    mime="text/csv"
)
