import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Plant Availability Drilldown Dashboard",
    page_icon="🏭",
    layout="wide"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
st.markdown("""
<style>

.stApp{
    background:#f4f7fb;
}

.block-container{
    padding-top:1.5rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1,h2,h3{
    color:#1f4e79;
}

div[data-testid="metric-container"]{
    background:white;
    border:1px solid #d9e2ec;
    border-radius:12px;
    padding:18px;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
}

.stSelectbox>div>div{
    background:white;
}

.stMultiSelect>div>div{
    background:white;
}

[data-testid="stDataFrame"]{
    background:white;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Header
# ---------------------------------------------------
st.markdown("""
<div style="
background:#1f77b4;
padding:20px;
border-radius:12px;
text-align:center;
margin-bottom:20px;
">

<h1 style="
margin:0;
color:white;
font-size:38px;
font-weight:bold;
">
Plant Availability Drilldown Dashboard
</h1>

<p style="
margin-top:8px;
font-size:18px;
color:white;
">
Asset Group → Machine → Weekly → Monthly → Daily Drill-down
</p>

</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
df = pd.read_excel("DailyAvailability.xlsx")

# ---------------------------------------------------
# Data Cleaning
# ---------------------------------------------------
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

# ---------------------------------------------------
# Remove Weekends
# ---------------------------------------------------
df = df[df["date"].dt.weekday < 5]

# ---------------------------------------------------
# Date Columns
# Sunday Week Start
# ---------------------------------------------------
df["Month"] = df["date"].dt.strftime("%B %Y")

df["WeekStart"] = (
    df["date"]
      .dt.to_period("W-SAT")
      .apply(lambda x: x.start_time)
)

df["Week"] = df["WeekStart"].dt.strftime("%d-%b-%Y")

df["Day"] = df["date"].dt.strftime("%d-%b")

# ---------------------------------------------------
# Plant Overview
# ---------------------------------------------------
st.subheader("Plant Overview")

plant_availability = df["availability_pct"].mean()

st.metric(
    "Plant Availability",
    f"{plant_availability:.2f}%"
)

# ---------------------------------------------------
# Filters
# ---------------------------------------------------
st.subheader("Filters")

c1,c2,c3,c4 = st.columns(4)

with c1:
    asset = st.selectbox(
        "Asset Group",
        sorted(df["asset_group"].unique())
    )

group_df = df[
    df["asset_group"]==asset
]

if group_df.empty:
    st.warning("No data available.")
    st.stop()

with c2:
    selected_units = st.multiselect(
        "Machines",
        sorted(group_df["machine_id"].unique()),
        default=sorted(group_df["machine_id"].unique())
    )

unit_df = group_df[
    group_df["machine_id"].isin(selected_units)
]

with c3:
    month = st.selectbox(
        "Month",
        sorted(unit_df["Month"].unique())
    )

month_df = unit_df[
    unit_df["Month"]==month
]

with c4:
    week = st.selectbox(
        "Week",
        sorted(month_df["Week"].unique())
    )

week_df = month_df[
    month_df["Week"]==week
]

# ---------------------------------------------------
# Weekly Summary
# ---------------------------------------------------
weekly_summary = (
    unit_df
    .groupby(
        ["Week","WeekStart"],
        as_index=False
    )
    .agg(
        availability_pct=("availability_pct","mean"),
        uptime_hours=("uptime_hours","sum"),
        downtime_hours=("downtime_hours","sum")
    )
)

weekly_summary = weekly_summary.sort_values(
    "WeekStart"
)

# ---------------------------------------------------
# Monthly Summary
# ---------------------------------------------------
monthly_summary = (
    unit_df
    .groupby(
        "Month",
        as_index=False
    )
    .agg(
        availability_pct=("availability_pct","mean"),
        uptime_hours=("uptime_hours","sum"),
        downtime_hours=("downtime_hours","sum")
    )
)

monthly_summary["MonthDate"] = pd.to_datetime(
    monthly_summary["Month"],
    format="%B %Y"
)

monthly_summary = monthly_summary.sort_values(
    "MonthDate"
)

# ---------------------------------------------------
# Overview Metrics
# ---------------------------------------------------
st.subheader("Overview")

avg_availability = week_df["availability_pct"].mean()

uptime = week_df["uptime_hours"].sum()

downtime = week_df["downtime_hours"].sum()

m1,m2,m3 = st.columns(3)

m1.metric(
    "Average Availability",
    f"{avg_availability:.2f}%"
)

m2.metric(
    "Total Uptime",
    f"{uptime:.2f} Hours"
)

m3.metric(
    "Total Downtime",
    f"{downtime:.2f} Hours"
)
# ---------------------------------------------------
# Weekly Availability
# ---------------------------------------------------
st.subheader("Weekly Availability")

fig_week = px.bar(
    weekly_summary,
    x="Week",
    y="availability_pct",
    text_auto=".2f",
    title="Weekly Availability"
)

fig_week.update_traces(
    marker_color="#1976d2"
)

fig_week.update_yaxes(
    range=[0,100],
    title="Availability (%)"
)

fig_week.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20),
    xaxis_title="Week",
    yaxis_title="Availability (%)"
)

st.plotly_chart(
    fig_week,
    use_container_width=True
)

# ---------------------------------------------------
# Monthly Availability
# ---------------------------------------------------
st.subheader("Monthly Availability")

fig_month = px.bar(
    monthly_summary,
    x="Month",
    y="availability_pct",
    text_auto=".2f",
    title="Monthly Availability"
)

fig_month.update_traces(
    marker_color="#0077B6"
)

fig_month.update_yaxes(
    range=[0,100],
    title="Availability (%)"
)

fig_month.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20),
    xaxis_title="Month",
    yaxis_title="Availability (%)"
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)

# ---------------------------------------------------
# Uptime vs Downtime
# ---------------------------------------------------
st.subheader("Uptime vs Downtime")

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
    hole=0.50,
    color="Type",
    color_discrete_map={
        "Uptime":"#2ECC71",
        "Downtime":"#E74C3C"
    }
)

fig_pie.update_layout(
    template="plotly_white",
    height=430
)

st.plotly_chart(
    fig_pie,
    use_container_width=True
)

# ---------------------------------------------------
# Machine-wise Availability
# ---------------------------------------------------
st.subheader("Machine-wise Availability")

machine_summary = (
    month_df
    .groupby(
        "machine_id",
        as_index=False
    )
    .agg(
        availability_pct=("availability_pct","mean"),
        uptime_hours=("uptime_hours","sum"),
        downtime_hours=("downtime_hours","sum")
    )
)

machine_summary = machine_summary.sort_values(
    "machine_id"
)

fig_machine = px.bar(
    machine_summary,
    x="machine_id",
    y="availability_pct",
    color="availability_pct",
    text_auto=".2f",
    color_continuous_scale="Blues",
    title="Machine-wise Average Availability"
)

fig_machine.update_yaxes(
    range=[0,100],
    title="Availability (%)"
)

fig_machine.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20,r=20,t=50,b=20),
    coloraxis_showscale=False
)

st.plotly_chart(
    fig_machine,
    use_container_width=True
)
# ---------------------------------------------------
# Machine Summary
# ---------------------------------------------------
st.subheader("Machine Summary")

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
        "availability_pct":"Availability (%)"
    },
    inplace=True
)

summary["Date"] = pd.to_datetime(
    summary["Date"]
).dt.strftime("%d-%b-%Y")

summary["Uptime (Hours)"] = summary["Uptime (Hours)"].round(2)
summary["Downtime (Hours)"] = summary["Downtime (Hours)"].round(2)
summary["Availability (%)"] = summary["Availability (%)"].round(2)

summary = summary.sort_values(
    ["Machine","Date"]
)

st.dataframe(
    summary.style.background_gradient(
        subset=["Availability (%)"],
        cmap="Greens"
    ),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------
# Download Button
# ---------------------------------------------------
csv = summary.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Machine Summary",
    csv,
    "Machine_Summary.csv",
    "text/csv"
)

# ===================================================
# DAILY AVAILABILITY (Moved to Last - Drill Down)
# ===================================================

st.markdown("---")
st.subheader("Daily Availability (Drill Down)")

week_df = week_df.sort_values(
    ["date","machine_id"]
)

fig_day = px.line(
    week_df,
    x="date",
    y="availability_pct",
    color="machine_id",
    markers=True,
    title="Daily Availability by Machine"
)

fig_day.update_traces(
    line=dict(width=3),
    marker=dict(size=8)
)

fig_day.update_yaxes(
    range=[0,100],
    title="Availability (%)"
)

fig_day.update_xaxes(
    tickformat="%d-%b",
    title="Date"
)

fig_day.update_layout(
    template="plotly_white",
    height=500,
    hovermode="x unified",
    legend_title="Machine",
    margin=dict(l=20,r=20,t=50,b=20)
)

st.plotly_chart(
    fig_day,
    use_container_width=True
)

# ---------------------------------------------------
# Daily Detail Table
# ---------------------------------------------------
daily_table = week_df[
    [
        "machine_id",
        "date",
        "availability_pct",
        "uptime_hours",
        "downtime_hours"
    ]
].copy()

daily_table.rename(
    columns={
        "machine_id":"Machine",
        "date":"Date",
        "availability_pct":"Availability (%)",
        "uptime_hours":"Uptime (Hours)",
        "downtime_hours":"Downtime (Hours)"
    },
    inplace=True
)

daily_table["Date"] = pd.to_datetime(
    daily_table["Date"]
).dt.strftime("%d-%b-%Y")

daily_table["Availability (%)"] = daily_table["Availability (%)"].round(2)
daily_table["Uptime (Hours)"] = daily_table["Uptime (Hours)"].round(2)
daily_table["Downtime (Hours)"] = daily_table["Downtime (Hours)"].round(2)

st.dataframe(
    daily_table,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------
# Footer
# ---------------------------------------------------
st.markdown("---")

st.markdown(
"""
<div style="text-align:center;color:gray;font-size:14px">

<b>Plant Availability Drilldown Dashboard</b><br>

Weekly → Monthly Overview → Daily Drill-down

</div>
""",
unsafe_allow_html=True
)
