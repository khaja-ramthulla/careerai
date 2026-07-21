"""
CareerAI — Intelligence Layer

Advanced analysis endpoints that power the premium features:
  - /transition-advisor : step-by-step career transition strategy
  - /learning-pace      : personalized weekly study plan
  - /skill-market       : real-world market intelligence per skill
"""

import math
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import profiles, roadmaps, quiz_scores, progress
from utils.career_engine import recommend_careers, analyze_skill_gap, _careers_by_title
from models.careers_data import CAREERS

intelligence_bp = Blueprint("intelligence", __name__)

# ----------------------------------------------------------------------
# Market intelligence database — real-world signals
# ----------------------------------------------------------------------
SKILL_MARKET = {
    # Programming
    "Python":        {"demand": 95, "salary_usd": [90000, 140000], "trend": "hot",      "related_roles": ["Data Scientist", "ML Engineer", "Backend Developer", "Data Analyst"]},
    "Java":          {"demand": 80, "salary_usd": [85000, 135000], "trend": "stable",   "related_roles": ["Backend Developer", "Full-Stack Developer", "Android Developer"]},
    "JavaScript":    {"demand": 92, "salary_usd": [80000, 130000], "trend": "hot",      "related_roles": ["Frontend Developer", "Full-Stack Developer"]},
    "TypeScript":    {"demand": 88, "salary_usd": [85000, 140000], "trend": "growing",  "related_roles": ["Frontend Developer", "Full-Stack Developer"]},
    "C++":           {"demand": 65, "salary_usd": [80000, 140000], "trend": "stable",   "related_roles": ["Systems Engineer", "Game Developer"]},
    "C#":            {"demand": 70, "salary_usd": [75000, 125000], "trend": "stable",   "related_roles": ["Backend Developer", "Game Developer"]},
    "Go":            {"demand": 72, "salary_usd": [100000, 160000], "trend": "growing", "related_roles": ["Backend Developer", "DevOps Engineer"]},
    "Rust":          {"demand": 55, "salary_usd": [110000, 170000], "trend": "growing", "related_roles": ["Systems Engineer"]},
    "Swift":         {"demand": 58, "salary_usd": [95000, 150000], "trend": "stable",   "related_roles": ["Mobile Developer"]},
    "Kotlin":        {"demand": 55, "salary_usd": [90000, 145000], "trend": "growing",  "related_roles": ["Mobile Developer", "Backend Developer"]},
    "PHP":           {"demand": 50, "salary_usd": [65000, 110000], "trend": "stable",   "related_roles": ["Backend Developer"]},
    "R":             {"demand": 45, "salary_usd": [85000, 130000], "trend": "stable",   "related_roles": ["Data Scientist", "Data Analyst"]},
    "SQL":           {"demand": 85, "salary_usd": [75000, 125000], "trend": "stable",   "related_roles": ["Data Analyst", "Backend Developer", "Full-Stack Developer"]},
    # Web
    "HTML":          {"demand": 82, "salary_usd": [0, 0],         "trend": "stable",   "related_roles": ["Frontend Developer", "UI/UX Designer"]},
    "CSS":           {"demand": 80, "salary_usd": [0, 0],         "trend": "stable",   "related_roles": ["Frontend Developer", "UI/UX Designer"]},
    "React":         {"demand": 90, "salary_usd": [90000, 150000], "trend": "hot",     "related_roles": ["Frontend Developer", "Full-Stack Developer"]},
    "Angular":       {"demand": 68, "salary_usd": [85000, 140000], "trend": "stable",  "related_roles": ["Frontend Developer"]},
    "Vue":           {"demand": 52, "salary_usd": [80000, 130000], "trend": "growing", "related_roles": ["Frontend Developer"]},
    "Next.js":       {"demand": 75, "salary_usd": [90000, 150000], "trend": "hot",     "related_roles": ["Frontend Developer", "Full-Stack Developer"]},
    "Bootstrap":     {"demand": 45, "salary_usd": [0, 0],         "trend": "stable",   "related_roles": ["Frontend Developer"]},
    "Tailwind CSS":  {"demand": 72, "salary_usd": [0, 0],         "trend": "growing",  "related_roles": ["Frontend Developer"]},
    # Data / ML
    "Pandas":        {"demand": 82, "salary_usd": [90000, 140000], "trend": "growing",  "related_roles": ["Data Scientist", "Data Analyst", "ML Engineer"]},
    "NumPy":         {"demand": 75, "salary_usd": [90000, 140000], "trend": "stable",   "related_roles": ["Data Scientist", "ML Engineer"]},
    "TensorFlow":    {"demand": 78, "salary_usd": [100000, 160000], "trend": "growing", "related_roles": ["ML Engineer", "Data Scientist"]},
    "PyTorch":       {"demand": 80, "salary_usd": [100000, 170000], "trend": "hot",     "related_roles": ["ML Engineer", "Data Scientist"]},
    "Scikit-learn":  {"demand": 70, "salary_usd": [90000, 145000], "trend": "stable",   "related_roles": ["Data Scientist", "ML Engineer"]},
    # Infra
    "Docker":        {"demand": 85, "salary_usd": [95000, 155000], "trend": "hot",      "related_roles": ["DevOps Engineer", "Backend Developer"]},
    "Kubernetes":    {"demand": 78, "salary_usd": [110000, 170000], "trend": "hot",     "related_roles": ["DevOps Engineer"]},
    "AWS":           {"demand": 90, "salary_usd": [100000, 165000], "trend": "hot",     "related_roles": ["DevOps Engineer", "Backend Developer", "Data Engineer"]},
    "Azure":         {"demand": 80, "salary_usd": [95000, 160000], "trend": "growing",  "related_roles": ["DevOps Engineer", "Data Engineer"]},
    "GCP":           {"demand": 65, "salary_usd": [100000, 165000], "trend": "growing",  "related_roles": ["Data Engineer", "DevOps Engineer"]},
    "Terraform":     {"demand": 72, "salary_usd": [110000, 170000], "trend": "growing", "related_roles": ["DevOps Engineer"]},
    "CI/CD":         {"demand": 75, "salary_usd": [90000, 150000], "trend": "stable",   "related_roles": ["DevOps Engineer"]},
    "Jenkins":       {"demand": 55, "salary_usd": [85000, 140000], "trend": "stable",   "related_roles": ["DevOps Engineer"]},
    "Git":           {"demand": 90, "salary_usd": [0, 0],         "trend": "hot",       "related_roles": ["All roles"]},
    "Linux":         {"demand": 78, "salary_usd": [80000, 140000], "trend": "stable",   "related_roles": ["DevOps Engineer", "Backend Developer"]},
    "Bash":          {"demand": 60, "salary_usd": [75000, 130000], "trend": "stable",   "related_roles": ["DevOps Engineer"]},
    # Design
    "UI/UX Design":  {"demand": 75, "salary_usd": [70000, 120000], "trend": "growing",  "related_roles": ["UI/UX Designer"]},
    "Figma":         {"demand": 78, "salary_usd": [70000, 120000], "trend": "hot",      "related_roles": ["UI/UX Designer"]},
    "Wireframing":   {"demand": 65, "salary_usd": [65000, 110000], "trend": "stable",   "related_roles": ["UI/UX Designer"]},
    "Prototyping":   {"demand": 62, "salary_usd": [65000, 110000], "trend": "stable",   "related_roles": ["UI/UX Designer"]},
    "Adobe XD":      {"demand": 50, "salary_usd": [65000, 110000], "trend": "stable",   "related_roles": ["UI/UX Designer"]},
    # Soft
    "Communication":  {"demand": 95, "salary_usd": [0, 0], "trend": "hot",       "related_roles": ["All roles"]},
    "Problem Solving": {"demand": 95, "salary_usd": [0, 0], "trend": "hot",      "related_roles": ["All roles"]},
    "Leadership":     {"demand": 80, "salary_usd": [0, 0], "trend": "stable",   "related_roles": ["All roles"]},
    "Teamwork":       {"demand": 85, "salary_usd": [0, 0], "trend": "stable",   "related_roles": ["All roles"]},
}


# ----------------------------------------------------------------------
# 1. Career Transition Advisor
# ----------------------------------------------------------------------
@intelligence_bp.route("/transition-advisor", methods=["POST"])
@jwt_required()
def transition_advisor():
    """
    Given a target career, returns a strategic transition plan:
    - Difficulty assessment (based on skill gap size)
    - Phased action plan with priorities
    - Estimated timeline with milestones
    - Quick wins vs long-term investments
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    target = (data.get("career") or "").strip()

    if not target:
        return jsonify({"error": "Target career is required."}), 400

    profile = profiles.find_one({"user_id": user_id})
    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    skills = profile.get("current_skills", [])
    if not skills:
        return jsonify({"error": "No skills found. Upload a resume first."}), 422

    gap = analyze_skill_gap(skills, target)
    if gap is None:
        return jsonify({"error": f"Unknown career: '{target}'"}), 404

    matched = gap.get("matched_skills", [])
    missing_core = gap.get("missing_core_skills", [])
    missing_bonus = gap.get("missing_bonus_skills", [])
    readiness = gap.get("readiness", 0)
    total_missing = len(missing_core) + len(missing_bonus)

    # --- Difficulty assessment ---
    if readiness >= 70:
        difficulty = "Ready to transition"
        diff_level = "easy"
        timeline_weeks = max(4, total_missing * 2)
    elif readiness >= 40:
        difficulty = "Moderate gap — achievable with focus"
        diff_level = "moderate"
        timeline_weeks = max(8, len(missing_core) * 3 + len(missing_bonus) * 1)
    else:
        difficulty = "Significant gap — dedicated study required"
        diff_level = "hard"
        timeline_weeks = max(16, len(missing_core) * 4 + len(missing_bonus) * 2)

    # --- Phase-based plan ---
    phases = []

    # Phase 1: Quick wins (skills that overlap with what user already has)
    related_skills = []
    for skill in matched:
        market = SKILL_MARKET.get(skill, {})
        for role in market.get("related_roles", []):
            if role != target and role != "All roles":
                related_skills.append(skill)
                break

    if matched:
        phases.append({
            "name": "Leverage Existing Skills",
            "description": "Your current skills that directly apply to this role.",
            "items": [
                {"skill": s, "action": "Highlight in portfolio and interviews", "weeks": 0}
                for s in matched[:5]
            ],
        })

    # Phase 2: Core gaps (highest priority)
    if missing_core:
        core_items = []
        for i, skill in enumerate(missing_core):
            market = SKILL_MARKET.get(skill, {})
            core_items.append({
                "skill": skill,
                "action": f"Complete structured learning path",
                "priority": "high",
                "weeks": 3 if i < 3 else 2,
                "salary_impact": f"+${market.get('salary_usd', [0,0])[0]:,}" if market.get('salary_usd', [0,0])[0] > 0 else "",
            })
        phases.append({
            "name": "Build Core Skills",
            "description": "Essential skills employers filter for in job postings.",
            "items": core_items,
        })

    # Phase 3: Bonus gaps (polish)
    if missing_bonus:
        bonus_items = []
        for skill in missing_bonus[:4]:
            bonus_items.append({
                "skill": skill,
                "action": "Complete supplementary learning",
                "priority": "medium",
                "weeks": 1,
            })
        phases.append({
            "name": "Polish & Differentiate",
            "description": "Bonus skills that set you apart from other candidates.",
            "items": bonus_items,
        })

    # --- Milestones ---
    milestones = []
    week_cursor = 0
    for phase in phases:
        for item in phase["items"]:
            w = item.get("weeks", 1)
            week_cursor += w
            if w > 0:
                milestones.append({
                    "week": week_cursor,
                    "milestone": f"Complete: {item['skill']}",
                })
    milestones.append({
        "week": timeline_weeks,
        "milestone": "Ready to start applying",
    })

    # --- Resume keyword suggestions ---
    career_def = _careers_by_title.get(target.lower(), {})
    keywords = []
    for s in missing_core[:5]:
        keywords.append(s)
    for s in missing_bonus[:3]:
        keywords.append(s)

    return jsonify({
        "career": target,
        "readiness": readiness,
        "difficulty": difficulty,
        "difficulty_level": diff_level,
        "timeline_weeks": timeline_weeks,
        "estimated_months": round(timeline_weeks / 4.3, 1),
        "phases": phases,
        "milestones": milestones,
        "resume_keywords": keywords,
        "existing_transferable": matched,
    }), 200


# ----------------------------------------------------------------------
# 2. Smart Learning Pace Calculator
# ----------------------------------------------------------------------
@intelligence_bp.route("/learning-pace", methods=["GET"])
@jwt_required()
def learning_pace():
    """
    Calculates a personalized study schedule based on:
    - Quiz performance (accuracy, consistency)
    - Progress activity patterns
    - Current roadmap position
    Returns optimal hours/week, best study days, and projected completion.
    """
    user_id = get_jwt_identity()

    # --- Gather quiz data ---
    quizzes = list(quiz_scores.find({"user_id": user_id}))
    avg_score = 0
    pass_rate = 0
    quiz_count = len(quizzes)
    if quiz_count > 0:
        scores = [q.get("percentage", 0) for q in quizzes]
        avg_score = sum(scores) / len(scores)
        pass_rate = sum(1 for q in quizzes if q.get("passed")) / quiz_count

    # --- Gather activity data ---
    events = list(progress.find({"user_id": user_id}))
    activity_days = set()
    for e in events:
        d = e.get("date")
        if d:
            activity_days.add(d.date().isoformat())

    # --- Roadmap progress ---
    roadmap = roadmaps.find_one({"user_id": user_id})
    total_modules = 0
    completed_modules = 0
    in_progress_modules = 0
    career = None
    if roadmap:
        modules = roadmap.get("modules", [])
        total_modules = len(modules)
        completed_modules = sum(1 for m in modules if m.get("status") == "completed")
        in_progress_modules = sum(1 for m in modules if m.get("status") == "in_progress")
        career = roadmap.get("career")

    remaining_modules = total_modules - completed_modules
    remaining_quizzes = sum(
        1 for m in roadmap.get("modules", [])
        if m.get("status") != "completed" and m.get("quiz_question_count", 0) > 0
    ) if roadmap else 0

    # --- Calculate pace ---
    if avg_score >= 80 and pass_rate >= 0.8:
        recommended_hours = 8
        pace_label = "Accelerated"
        pace_description = "You're performing excellently. Push harder and finish early."
    elif avg_score >= 60 and pass_rate >= 0.6:
        recommended_hours = 5
        pace_label = "Steady"
        pace_description = "Good progress. Maintain consistency to stay on track."
    else:
        recommended_hours = 3
        pace_label = "Foundation"
        pace_description = "Focus on understanding concepts deeply before moving on."

    # Boost recommended hours if many modules remain
    if remaining_modules > 6:
        recommended_hours = min(recommended_hours + 2, 12)

    # --- Best study days (based on activity patterns) ---
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_counts = [0] * 7
    for e in events:
        d = e.get("date")
        if d:
            day_counts[d.weekday()] += 1
    most_active_days = sorted(range(7), key=lambda i: day_counts[i], reverse=True)
    best_days = [day_names[i] for i in most_active_days[:3] if day_counts[i] > 0] or ["Mon", "Wed", "Fri"]

    # --- Projected completion ---
    if remaining_modules <= 0:
        weeks_to_complete = 0
    elif quiz_count >= 3:
        weeks_to_complete = math.ceil(remaining_modules * 2 / max(pass_rate, 0.3))
    else:
        weeks_to_complete = remaining_modules * 3

    completion_date = datetime.now(timezone.utc) + timedelta(weeks=weeks_to_complete)

    weekly_schedule = {
        "hours_per_week": recommended_hours,
        "sessions_per_week": min(recommended_hours, 5),
        "minutes_per_session": round((recommended_hours * 60) / min(recommended_hours, 5)),
        "best_days": best_days,
        "pace_label": pace_label,
        "pace_description": pace_description,
    }

    return jsonify({
        "career_target": career,
        "quiz_stats": {
            "total_quizzes": quiz_count,
            "average_score": round(avg_score, 1),
            "pass_rate": round(pass_rate * 100, 1),
        },
        "progress": {
            "total_modules": total_modules,
            "completed": completed_modules,
            "in_progress": in_progress_modules,
            "remaining": remaining_modules,
            "active_days": len(activity_days),
        },
        "recommendation": weekly_schedule,
        "projected_weeks_to_complete": weeks_to_complete,
        "projected_completion_date": completion_date.date().isoformat(),
    }), 200


# ----------------------------------------------------------------------
# 3. Skill Market Intelligence
# ----------------------------------------------------------------------
@intelligence_bp.route("/skill-market", methods=["POST"])
@jwt_required()
def skill_market():
    """
    Returns market intelligence for a list of skills:
    - Demand score (0-100)
    - Salary ranges
    - Trend (hot/growing/stable/declining)
    - Related roles
    - Learning priority recommendation
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    skills = data.get("skills", [])

    if not skills:
        profile = profiles.find_one({"user_id": user_id})
        if profile:
            skills = profile.get("current_skills", [])

    if not skills:
        return jsonify({"error": "No skills to analyze."}), 422

    results = []
    for skill in skills:
        market = SKILL_MARKET.get(skill, None)
        if market:
            results.append({
                "skill": skill,
                "demand": market["demand"],
                "salary_range": market["salary_usd"],
                "trend": market["trend"],
                "related_roles": market["related_roles"],
                "market_value": (
                    "premium" if market["salary_usd"][1] >= 150000
                    else "strong" if market["salary_usd"][1] >= 120000
                    else "standard" if market["salary_usd"][1] > 0
                    else "fundamental"
                ),
            })
        else:
            results.append({
                "skill": skill,
                "demand": 50,
                "salary_range": [0, 0],
                "trend": "unknown",
                "related_roles": [],
                "market_value": "unknown",
            })

    # Sort by demand
    results.sort(key=lambda x: x["demand"], reverse=True)

    # Overall portfolio score
    total_demand = sum(r["demand"] for r in results) / len(results) if results else 0
    top_salary = max((r["salary_range"][1] for r in results), default=0)
    hot_count = sum(1 for r in results if r["trend"] == "hot")

    return jsonify({
        "skills": results,
        "portfolio_summary": {
            "average_demand": round(total_demand, 1),
            "highest_potential_salary": top_salary,
            "hot_skills_count": hot_count,
            "total_skills": len(results),
            "portfolio_strength": (
                "Elite" if total_demand >= 80 and hot_count >= 3
                else "Strong" if total_demand >= 65
                else "Developing" if total_demand >= 45
                else "Early Stage"
            ),
        },
    }), 200
