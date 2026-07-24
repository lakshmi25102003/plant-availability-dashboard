import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Plant Availability Drilldown Dashboard",
    page_icon="🏭",
    layout="wide"
)

# -----------------------------
# Professional Light Theme CSS
# -----------------------------
st.markdown("""
<style>

/* Background */
.stApp{
    background:#f4f7fb;
}

/* Page */
.block-container{
    padding-top:1.5rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* Header */
h1{
    text-align:center;
    color:white !important;
    font-size:42px !important;
    font-weight:700;
}

h2,h3{
    color:#1f4e79;
}

/* Metric Cards */
div[data-testid="metric-container"]{
    background:white;
    border:1px solid #d9e2ec;
    border-radius:15px;
    padding:18px;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
}

/* Selectbox */
.stSelectbox>div>div{
    background:white;
    border-radius:10px;
}

/* Multiselect */
.stMultiSelect>div>div{
    background:white;
    border-radius:10px;
}

/* DataFrame */
[data-testid="stDataFrame"]{
    background:white;
    border-radius:12px;
    border:1px solid #d9e2ec;
    padding:8px;
}

/* Buttons */
.stDownloadButton button{
    background:#1976d2;
    color:white;
    border:none;
    border-radius:8px;
    padding:10px 18px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div style="
background:#1f77b4;
padding:22px;
border-radius:15px;
text-align:center;
margin-bottom:25px;
box-shadow:0 4px 12px rgba(0,0,0,.15);
">

<h1 style="margin:0;color:white;">
🏭 Plant Availability Drilldown Dashboard
</h1>

<p style="
margin-top:8px;
font-size:18px;
color:white;">
Asset Group → Machine Drilldown
</p>

</div>
""", unsafe_allow_html=True)

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_excel("DailyAvailability.xlsx")

# -----------------------------
# Data Cleaning
# -----------------------------
df["date"] = pd.to_datetime(df["date"])

df = df.dropna(subset=["availability_pct"])

df["asset_group"] = (
    df["asset_group"]
    .astype(str)
    .str.strip()
)

df["machine_id"] = (
    df["machine_id"]
    .astype(str)
    .str.strip()
)

# Remove Weekends
df = df[df["date"].dt.weekday < 5]

# -----------------------------
# Date Columns
# -----------------------------
df["Month"] = df["date"].dt.strftime("%B %Y")
df["Week"] = df["date"].dt.strftime("%Y-W%U")
df["Day"] = df["date"].dt.strftime("%d-%b")

# -----------------------------
# Plant Overview
# -----------------------------
plant_availability = df["availability_pct"].mean()

st.subheader("🏭 Plant Overview")

st.metric(
    "Plant Availability",
    f"{plant_availability:.2f}%"
)

# -----------------------------
# Filters
# -----------------------------
st.subheader("🎯 Filters")

col1, col2, col3, col4 = st.columns([1.2,1.4,1,1])

with col1:
    asset = st.selectbox(
        "Select Asset Group",
        sorted(df["asset_group"].unique())
    )

group_df = df[df["asset_group"] == asset]

if group_df.empty:
    st.warning("No data available.")
    st.stop()

with col2:
    selected_units = st.multiselect(
        "Select Machines",
        sorted(group_df["machine_id"].unique()),
        default=sorted(group_df["machine_id"].unique())
    )

unit_df = group_df[
    group_df["machine_id"].isin(selected_units)
].copy()

with col3:
    month = st.selectbox(
        "Select Month",
        sorted(unit_df["Month"].unique())
    )

month_df = unit_df[
    unit_df["Month"] == month
]

with col4:
    week = st.selectbox(
        "Select Week",
        sorted(month_df["Week"].unique())
    )

week_df = month_df[
    month_df["Week"] == week
]

# -----------------------------
# Weekly & Monthly Roll-up
# -----------------------------
weekly_summary = (
    unit_df
    .groupby("Week", as_index=False)
    .agg(
        availability_pct=("availability_pct", "mean"),
        uptime_hours=("uptime_hours", "sum"),
        downtime_hours=("downtime_hours", "sum")
    )
)

monthly_summary = (
    unit_df
    .groupby("Month", as_index=False)
    .agg(
        availability_pct=("availability_pct", "mean"),
        uptime_hours=("uptime_hours", "sum"),
        downtime_hours=("downtime_hours", "sum")
    )
)
# -----------------------------
# Overview Metrics
# -----------------------------
st.subheader("📊 Overview")

avg_availability = week_df["availability_pct"].mean()
uptime = week_df["uptime_hours"].sum()
downtime = week_df["downtime_hours"].sum()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Average Availability",
        f"{avg_availability:.2f}%"
    )

with c2:
    st.metric(
        "Total Uptime",
        f"{uptime:.2f} Hours"
    )

with c3:
    st.metric(
        "Total Downtime",
        f"{downtime:.2f} Hours"
    )

# -----------------------------
# Weekly Availability
# -----------------------------
st.subheader("📊 Weekly Availability")

fig_week = px.bar(
    weekly_summary,
    x="Week",
    y="availability_pct",
    text_auto=".2f",
    title="Weekly Availability"
)

fig_week.update_traces(marker_color="#00B4D8")

fig_week.update_yaxes(range=[0,100])

fig_week.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20)
)

st.plotly_chart(fig_week, use_container_width=True)

# -----------------------------
# Monthly Availability
# -----------------------------
st.subheader("📅 Monthly Availability")

fig_month = px.bar(
    monthly_summary,
    x="Month",
    y="availability_pct",
    text_auto=".2f",
    title="Monthly Availability"
)

fig_month.update_traces(marker_color="#0077B6")

fig_month.update_yaxes(range=[0,100])

fig_month.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20)
)

st.plotly_chart(fig_month, use_container_width=True)

# -----------------------------
# Daily Availability
# -----------------------------
week_df = week_df.sort_values("date")

st.subheader("📈 Daily Availability")

fig_day = px.line(
    week_df,
    x="Day",
    y="availability_pct",
    color="machine_id",
    markers=True,
    title="Daily Availability"
)

fig_day.update_traces(
    line=dict(width=3),
    marker=dict(size=8)
)

fig_day.update_yaxes(range=[0,100])

fig_day.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20)
)

st.plotly_chart(fig_day, use_container_width=True)

# -----------------------------
# Uptime vs Downtime
# -----------------------------
st.subheader("🥧 Uptime vs Downtime")

pie_df = pd.DataFrame({
    "Type":["Uptime","Downtime"],
    "Hours":[
        week_df["uptime_hours"].sum(),
        week_df["downtime_hours"].sum()
    ]
})

fig_pie = px.pie(
    pie_df,
    names="Type",
    values="Hours",
    hole=0.5,
    color_discrete_sequence=["#2ECC71","#E74C3C"]
)

fig_pie.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# Machine-wise Availability
# -----------------------------
st.subheader("📊 Machine-wise Availability")

machine_summary = (
    month_df
    .groupby("machine_id", as_index=False)
    .agg(
        availability_pct=("availability_pct","mean")
    )
)

fig_machine = px.bar(
    machine_summary,
    x="machine_id",
    y="availability_pct",
    color="availability_pct",
    text_auto=".2f",
    title="Machine-wise Average Availability",
    color_continuous_scale="Blues"
)

fig_machine.update_yaxes(range=[0,100])

fig_machine.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20)
)

st.plotly_chart(fig_machine, use_container_width=True)

# -----------------------------
# Machine Summary
# -----------------------------
st.subheader("📋 Machine Summary")

summary = week_df[
    [
        "machine_id",
        "date",
        "uptime_hours",
        "downtime_hours",
        "availability_pct"
    ]
].copy()

summary.rename(
    columns={
        "machine_id":"Machine",
        "date":"Date",
        "uptime_hours":"Uptime (Hours)",
        "downtime_hours":"Downtime (Hours)",
        "availability_pct":"Availability %"
    },
    inplace=True
)

summary["Date"] = pd.to_datetime(
    summary["Date"]
).dt.strftime("%d-%b-%Y")

summary["Uptime (Hours)"] = summary["Uptime (Hours)"].round(2)
summary["Downtime (Hours)"] = summary["Downtime (Hours)"].round(2)
summary["Availability %"] = summary["Availability %"].round(2)

summary = summary.sort_values("Date")

st.dataframe(
    summary.style.background_gradient(
        subset=["Availability %"],
        cmap="Greens"
    ),
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Download Button
# -----------------------------
csv = summary.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Summary",
    csv,
    "Machine_Summary.csv",
    "text/csv"
)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")

st.markdown(
    """
<div style='text-align:center;
color:gray;
font-size:14px;'>

🏭 <b>Plant Availability Drilldown Dashboard</b><br>

Daily → Weekly → Monthly Roll-up (Weekends Excluded)

</div>
""",
    unsafe_allow_html=True
)