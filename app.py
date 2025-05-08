# ==== Import Libraries ====
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==== Mobile Warning Banner ====
st.markdown(
    """
    <div style="background-color: #fff3cd; border: 1px solid #ffeeba;
                padding: 10px; border-radius: 5px; margin-bottom: 20px;
                color: #856404; font-family: sans-serif; text-align: center;">
        📱 For the best experience on mobile, please enable <b>'Desktop site'</b> in your browser.
    </div>
    """,
    unsafe_allow_html=True
)

# ==== Load & Filter Data (Dummy Data Example) ====
df = pd.DataFrame({
    "Matchweek": list(range(1, 21)),
    "Man City": [i + (i % 3) for i in range(20)],
    "Crystal Palace": [i - (i % 4) for i in range(20)]
})

df_melted = df.melt(id_vars="Matchweek", var_name="Team", value_name="Points")

# ==== Plotly Graph ====
fig = go.Figure()

teams = df_melted["Team"].unique()
for team in teams:
    team_data = df_melted[df_melted["Team"] == team]
    fig.add_trace(go.Scatter(
        x=team_data["Matchweek"],
        y=team_data["Points"],
        mode='lines+markers',
        name=team
    ))

fig.update_layout(
    template='plotly_dark',
    title="Premier League Points",
    xaxis_title="Matchweek",
    yaxis_title="Points",
    width=1000,
    height=600,
    margin=dict(l=60, r=20, t=60, b=40)
)

# ==== Show Plot ====
st.plotly_chart(fig, use_container_width=True)