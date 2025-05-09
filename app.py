# ==== Import Libraries ====
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import streamlit.components.v1 as components

# ==== Load & Filter Data ====
df = pd.read_csv("premier_league_standings.csv")
df = df.drop(columns=['GoalsFor', 'GoalsAgainst', 'GoalDifference'])
clubs = ['Man City', 'Crystal Palace']
df_filtered = df[df['Club'].isin(clubs)]

# ==== Team Data ====
team_data = {club: df[df["Club"] == club] for club in clubs}
display_names = {
    "Man City": "Manchester City",
    "Crystal Palace": "Crystal Palace"
}

# ==== Encode Logos ====
def encode_logo(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

team_logos = {
    "Crystal Palace": {
        "img": encode_logo("images/crystal_palace_logo.png"),
        "sizex": 5,
        "sizey": 25
    },
    "Man City": {
        "img": encode_logo("images/man_city_logo.png"),
        "sizex": 6,
        "sizey": 30
    }
}

# ==== Style & Annotations ====
result_styles = {
    "Win": {"color": "green", "text": "W"},
    "Draw": {"color": "grey", "text": "D"},
    "Defeat": {"color": "red", "text": "L"},
}

team_annotations = {
    "Crystal Palace": {
        "shapes": [
            dict(type="rect", xref="x", yref="paper", x0=1, x1=8, y0=0, y1=1, fillcolor="rgba(200, 200, 200, 0.1)", line=dict(width=0)),
            dict(type="rect", xref="x", yref="paper", x0=12, x1=28, y0=0, y1=1, fillcolor="rgba(200, 200, 200, 0.1)", line=dict(width=0))
        ],
        "annotations": [
            dict(x=1 + (8-1)/2, y=55, text="<i>No wins</i> in the first<br><b><span style='color:#e07a5f'>nine</span></b> games", showarrow=False, font=dict(color="white", size=14), align="center", xanchor="center", yanchor="middle"),
            dict(x=13 + (28-13)/2, y=55, text="A run of 17 games with <b><span style='color:#81b29a'>just 3 defeats</span></b><br>transformed Palace’s season.", showarrow=False, font=dict(color="white", size=14), align="center", xanchor="center", yanchor="middle")
        ]
    },
    "Man City": {
        "shapes": [
            dict(type="rect", xref="x", yref="paper", x0=10, x1=18, y0=0, y1=1, fillcolor="rgba(200, 200, 200, 0.1)", line=dict(width=0)),
            dict(type="rect", xref="x", yref="paper", x0=1, x1=9, y0=0, y1=1, fillcolor="rgba(200, 200, 200, 0.1)", line=dict(width=0))
        ],
        "annotations": [
            dict(x=1 + (9-1)/2, y=55, text="<i>Seven wins</i> in the first <br><b><span style='color:#81b29a'>nine</span></b> games set City<br>off to a flying start", showarrow=False, font=dict(color="white", size=14), align="center", xanchor="center", yanchor="middle"),
            dict(x=10 + (18-10)/2, y=55, text="Just <i>one win</i> and<br> <b><span style='color:#e07a5f'>six </span></b>defeats in the<br> next <b><span style='color:#e07a5f'>nine </span></b>games <br>turned City's season<br> upside down.", showarrow=False, font=dict(color="white", size=14), align="center", xanchor="center", yanchor="middle")
        ]
    }
}

team_summary_text = {
    "Crystal Palace": "<b>Summary:</b> Most fans will be thrilled by a cup final appearance but will rue the poor home form and slow start to the season.",
    "Man City": "<b>Summary:</b> Poor season by <i>their</i> standards. Most fans will be disappointed.  <b>Lowest Pos:</b> 7th  <b>Final Pos:</b> 3rd  <b>Cup Finalist:</b> Yes",
}

# ==== Helpers ====
def get_team_position(df, team_name):
    team_df = df[df["Club"] == team_name]
    latest_row = team_df.loc[team_df["Matchweek"].idxmax()]
    return int(latest_row["Position"])

def build_title_text(team):
    team_df = team_data[team]
    counts = team_df["Result"].value_counts().to_dict()
    total_points = team_df["Points"].iloc[-1]
    position = get_team_position(df, team)

    return (
        f"<b>{display_names[team]}</b> – "
        f"<span style='font-size: 16px;'>Position: {position} | "
        f"{total_points} Pts, {counts.get('Win', 0)} Wins, {counts.get('Draw', 0)} Draws, {counts.get('Defeat', 0)} Defeats</span>"
        f"<br><span style='font-size:14px; color:lightgrey;'>{team_summary_text[team]}</span>"
    )

# ==== Chart Prep ====
fig = go.Figure()
team_traces = {}
comparison_traces = {}

def build_team_traces(main_team):
    df_main = team_data[main_team]
    df_other = team_data[[t for t in team_data if t != main_team][0]]
    indices = []

    comp_trace = go.Scatter(
        x=df_other["Matchweek"], y=df_other["Points"], mode="lines",
        line=dict(color="#888", width=1, dash='dot'),
        opacity=0.3, name=f"Comparison ({display_names[df_other['Club'].iloc[0]]})",
        showlegend=False, visible=(main_team == "Man City")
    )
    fig.add_trace(comp_trace)
    comparison_traces[main_team] = len(fig.data) - 1

    fig.add_trace(go.Scatter(
        x=df_main["Matchweek"], y=df_main["Points"], mode="lines",
        line=dict(color="#eeeeee", width=1),
        opacity=0.3, name=f"{main_team} Line",
        showlegend=False, visible=(main_team == "Man City")
    ))
    indices.append(len(fig.data) - 1)

    for result, style in result_styles.items():
        subset = df_main[df_main["Result"] == result]
        fig.add_trace(go.Scatter(
            x=subset["Matchweek"], y=subset["Points"], mode="markers+text",
            text=[style["text"]] * len(subset), textposition="middle center",
            marker=dict(size=20, color=style["color"], symbol="circle", line=dict(width=0.25, color='black')),
            name=f"{main_team} {result}",
            showlegend=False, visible=(main_team == "Man City")
        ))
        indices.append(len(fig.data) - 1)

    team_traces[main_team] = indices

def make_visibility(selected_team):
    vis = [False] * len(fig.data)
    vis[comparison_traces[selected_team]] = True
    for i in team_traces[selected_team]:
        vis[i] = True
    return vis

# ==== Build Traces ====
for team in team_data:
    build_team_traces(team)

# ==== Buttons ====
buttons = []
for team in team_data:
    logo = team_logos[team]
    buttons.append(dict(
        label=display_names[team],
        method="update",
        args=[{"visible": make_visibility(team)},
              {"title.text": build_title_text(team),
               "images": [dict(
                   source=f"data:image/png;base64,{logo['img']}",
                   sizex=logo['sizex'], sizey=logo['sizey'],
                   xref="x", yref="y", x=35, y=2,
                   xanchor="right", yanchor="bottom", opacity=0.9, layer="above"
               )],
               "shapes": team_annotations[team]["shapes"],
               "annotations": team_annotations[team]["annotations"]}]))

# ==== Layout ====
all_max_points = max(team_data[team]["Points"].max() for team in team_data)
fig.update_layout(
    template='plotly_dark',
    title=dict(
        text=build_title_text("Man City"),
        font=dict(family="Arial", size=24, color="white"),
        x=0.02,  
        xanchor="left",
        pad=dict(t=10, b=10)
        ),
    xaxis_title="", plot_bgcolor="#2b2b2b", paper_bgcolor="#2b2b2b", font=dict(color="white"),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(range=[-5, all_max_points + 5], showgrid=False, zeroline=False),
    width=950, height=570, margin=dict(l=70, r=20, t=100, b=40),
    updatemenus=[dict(
        type="buttons", direction="right", x=1.02, xanchor="right", y=1.2, yanchor="top",
        buttons=buttons, showactive=True,
        bgcolor="#444", font=dict(color="grey"),
        bordercolor="white", borderwidth=1,
        pad={"r": 10, "t": 10}
    )],
    images=[dict(
        source=f"data:image/png;base64,{team_logos['Man City']['img']}",
        xref="x", yref="y", x=35, y=2,
        sizex=team_logos['Man City']['sizex'],
        sizey=team_logos['Man City']['sizey'],
        xanchor="right", yanchor="bottom",
        opacity=0.9, layer="below"
    )],
    shapes=team_annotations["Man City"]["shapes"],
    annotations=team_annotations["Man City"]["annotations"]
)

# ==== Streamlit Display ====
st.set_page_config(layout="wide")  # Set to wide mode by default
st.markdown("<div style='text-align:center; color: red; font-size: 16px;'>⚠️ Please note: This chart is optimized for wide screens. On mobile devices, the chart may require scrolling.</div>", unsafe_allow_html=True)

# Display the chart
#st.plotly_chart(fig, use_container_width=True)
# Add mobile-friendly horizontal padding with max width
with st.container():
    st.markdown("""
    <div style="margin-left: 0px; margin-right: 100px;">
    """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

