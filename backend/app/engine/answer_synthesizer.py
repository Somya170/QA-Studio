import json
from typing import List, Dict, Any
from app.models.schemas import GroundingAudit
from app.llm.cloud_provider import cloud_llm

def format_currency(val):
    if val is None:
        return ""
    try:
        return f"${float(val):,.2f}"
    except (ValueError, TypeError):
        return str(val)

def format_num(val):
    if val is None:
        return ""
    try:
        return f"{float(val):,.1f}"
    except (ValueError, TypeError):
        return str(val)

def synthesize_grounded_answer(query: str, results: List[Dict[str, Any]], audit: GroundingAudit, viz_hint: str) -> str:
    """
    Formats natural language answer strictly grounded on database rows.
    Uses Gemini AI if initialized, with automatic local fallback on quota errors.
    """
    if not results:
        return f"Based on historical database logs, no matching records were found for query: '{query}'."

    # Try Gemini Grounded Synthesis if initialized and has quota
    if cloud_llm.initialized:
        try:
            system_prompt = (
                "You are a high-precision industrial data QA coordinator.\n"
                "You are given a user query and the exact database rows retrieved from the warehouse.\n"
                "Your task is to answer the user query directly and concisely using ONLY the provided database rows.\n"
                "Rules:\n"
                "1. Keep your answer highly specific, direct, and short.\n"
                "2. Do NOT extrapolate, speculate, or fabricate any numbers, facts, or logs that are not present in the data.\n"
                "3. If the answer is not present in the provided data, state that the information was not found."
            )
            prompt = f"User Question:\n{query}\n\nDatabase Records:\n{json.dumps(results, indent=2)}"
            answer = cloud_llm.generate(prompt, system_prompt=system_prompt)
            if answer and "API Query Error" not in answer and "⚠️" not in answer:
                return answer
            else:
                print("Gemini API returned error/quota warning, falling back to local synthesizer. Detail:", answer)
        except Exception as e:
            print("Gemini synthesis fallback triggered:", e)

    # Heuristic template fallback (runs when Gemini is offline, limited, or rate-limited)
    q_lower = query.lower()
    first = results[0]
    
    mac_id = first.get("machine_id") or first.get("id") or first.get("equipment_id") or ""
    mac_name = first.get("name") or first.get("machine_name") or mac_id or "Machine"
    category = first.get("category") or first.get("type") or ""
    location = first.get("location") or first.get("area") or first.get("plant") or first.get("bay")
    cost = first.get("total_maintenance_cost") or first.get("cost") or first.get("repair_cost")
    downtime = first.get("total_downtime_hours") or first.get("downtime_hours") or first.get("downtime")
    operator = first.get("operator_name") or first.get("current_operator") or first.get("operator")
    shift = first.get("shift") or first.get("operator_shift") or first.get("work_shift") or first.get("shift_timing")
    notes = first.get("technician_notes") or first.get("notes") or first.get("description")
    parts = first.get("parts_replaced") or first.get("parts")
    issue = first.get("issue_type") or first.get("issue")
    health = first.get("health_score") or first.get("health")

    # Detect multi-attribute query intent
    has_operator_q = any(k in q_lower for k in ["operator", "who", "worker", "operated"])
    has_issue_q = any(k in q_lower for k in ["issue", "failure", "problem", "fault"])
    has_downtime_q = "downtime" in q_lower
    has_location_q = any(k in q_lower for k in ["location", "where", "located", "place", "bay", "plant"])
    
    asked_count = sum([has_operator_q, has_issue_q, has_downtime_q, has_location_q])
    
    if asked_count > 1:
        details = []
        if operator: details.append(f"Operator: **{operator}**")
        if shift: details.append(f"Shift: **{shift}**")
        if location: details.append(f"Location: **{location}**")
        if issue: details.append(f"Issue: **{issue}**")
        if downtime is not None: details.append(f"Downtime: **{format_num(downtime)} hrs**")
        if cost is not None: details.append(f"Cost: **{format_currency(cost)}**")
        
        detail_str = " | ".join(details)
        return f"For **{mac_name}** ({mac_id}): {detail_str}."

    # Single attribute lookup handlers
    elif has_location_q:
        if location:
            return f"The location of **{mac_name}** ({mac_id}) is **{location}**."
        else:
            return f"No location data was found in the record for **{mac_name}** ({mac_id})."

    elif "health" in q_lower or "score" in q_lower:
        if health is not None:
            return f"The health score of **{mac_name}** ({mac_id}) is **{health}%**."
        else:
            return f"No health score was found in the record for **{mac_name}** ({mac_id})."

    elif any(k in q_lower for k in ["parts", "replaced", "part"]):
        if parts:
            return f"The parts replaced for **{mac_name}** ({mac_id}) were: **{parts}**."
        else:
            return f"No parts were replaced in this record for **{mac_name}** ({mac_id})."

    elif has_issue_q:
        if issue:
            return f"The logged issue for **{mac_name}** ({mac_id}) was: **{issue}**."
        else:
            return f"No issue type was logged in this record for **{mac_name}** ({mac_id})."

    elif "downtime" in q_lower and ("highest" in q_lower or "max" in q_lower or "most" in q_lower or "total" in q_lower):
        top_name = mac_name if mac_name != mac_id else f"Machine {mac_id}"
        cat_str = f" ({category})" if category else ""
        hours_str = f"**{format_num(downtime)} hours**" if downtime is not None else "**top downtime**"
        cost_str = f" with total cost **{format_currency(cost)}**" if cost is not None else ""
        return f"**{top_name}**{cat_str} recorded the highest total downtime with {hours_str}{cost_str} across {len(results)} matching records."

    elif ("cost" in q_lower or "spend" in q_lower or "price" in q_lower or "expensive" in q_lower) and ("highest" in q_lower or "max" in q_lower or "total" in q_lower):
        top_name = mac_name if mac_name != mac_id else f"Machine {mac_id}"
        cost_str = f"**{format_currency(cost)}**" if cost is not None else "highest cost"
        notes_str = f" Technician Note: *'{notes}'*" if notes else ""
        return f"**{top_name}** recorded the highest maintenance spend totaling {cost_str}.{notes_str}"

    elif has_operator_q or any(k in q_lower for k in ["shift", "timing", "schedule"]):
        details = []
        if operator: details.append(f"Operator: **{operator}**")
        if shift: details.append(f"Shift Timing: **{shift}**")
        if mac_name: details.append(f"Assigned Machine: **{mac_name}** ({mac_id})")
        if issue: details.append(f"Issue Logged: **{issue}**")
        if downtime is not None: details.append(f"Downtime: **{format_num(downtime)} hrs**")
        
        detail_str = " | ".join(details)
        notes_str = f"\n\n**Technician Log Notes:** *\"{notes}\"*" if notes else ""
        return f"Shift & Operator Log: {detail_str}.{notes_str}"

    elif any(k in q_lower for k in ["note", "technician", "history", "repair"]):
        details = []
        if operator: details.append(f"Operator: **{operator}**")
        if shift: details.append(f"Shift Timing: **{shift}**")
        if issue: details.append(f"Issue: **{issue}**")
        if cost is not None: details.append(f"Cost: **{format_currency(cost)}**")
        if downtime is not None: details.append(f"Downtime: **{format_num(downtime)} hrs**")
        if parts: details.append(f"Parts Replaced: **{parts}**")
        
        detail_str = " | ".join(details)
        notes_str = f"\n\n**Technician Log Notes:** *\"{notes}\"*" if notes else ""
        
        return f"Historical Record for **{mac_name}** ({mac_id}): {detail_str}.{notes_str}"

    else:
        details = []
        if operator: details.append(f"Operator: **{operator}**")
        if shift: details.append(f"Shift Timing: **{shift}**")
        if issue: details.append(f"Issue: **{issue}**")
        if downtime is not None: details.append(f"Downtime: **{format_num(downtime)} hrs**")
        
        detail_str = f" ({' | '.join(details)})" if details else ""
        notes_str = f"\n\n**Technician Log Notes:** *\"{notes}\"*" if notes else ""
        
        return f"Retrieved **{len(results)} matching ground-truth records** for **{mac_name}** ({mac_id}){detail_str}.{notes_str}"
