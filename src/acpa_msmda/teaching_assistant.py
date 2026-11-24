"""Rule-based assistant; no external LLM, no claims of empirical effectiveness."""
from .learning_library import load_situations
from .scenario_engine import recommend_phase_tools
from .session_context import APS, LEVELS, CONNECTIVITY

def suggestions(activity,level,connectivity,phase):
    if activity not in APS or level not in LEVELS or connectivity not in CONNECTIVITY:
        raise ValueError("Invalid teaching context")
    situations=[s for s in load_situations() if s["activity"]==activity and s["level"]==level]
    tools=recommend_phase_tools(phase,connectivity=connectivity,limit=3)
    return {"situations":situations,"tools":tools,"mode":"rule_based","institutional_validation":False}
