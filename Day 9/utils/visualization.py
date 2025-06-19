import plotly.express as px
from typing import Dict, List
from utils.schemas import GapAnalysis

def create_gap_radar_chart(gap_analysis: GapAnalysis):
    """Create a radar chart visualizing skill gaps"""
    categories = []
    current_levels = []
    required_levels = []
    
    for gap in gap_analysis.critical_gaps + gap_analysis.moderate_gaps:
        categories.append(gap.skill)
        current_levels.append(gap.current_level.value)
        required_levels.append(gap.required_level.value)
    
    fig = px.line_polar(
        r=current_levels + required_levels,
        theta=categories + categories,
        color=["Current"]*len(categories) + ["Required"]*len(categories),
        line_close=True,
        title="Skill Level Comparison"
    )
    
    fig.update_traces(fill='toself')
    return fig

def create_roadmap_gantt_chart(roadmap):
    """Create a Gantt chart for the learning roadmap"""
    tasks = []
    for week in roadmap.weeks:
        for task in week.tasks:
            tasks.append({
                "Task": task.title,
                "Start": f"Week {week.week_number}",
                "Finish": f"Week {week.week_number}",
                "Duration": task.duration_hours,
                "Resource": ", ".join(task.resources[:1])
            })
    
    fig = px.timeline(
        tasks,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        title="Learning Roadmap Timeline"
    )
    fig.update_yaxes(autorange="reversed")
    return fig