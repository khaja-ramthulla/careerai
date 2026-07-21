"""
CareerAI — Learning Roadmap Engine

Builds a personalized, week-by-week learning roadmap from the gap between
a user's current skills and their target career's requirements.

- Missing CORE skills come first (highest employability impact),
  followed by missing BONUS skills.
- Each roadmap module carries free resources, an embeddable YouTube video,
  and a quiz. Quiz answers stay server-side: strip_quiz_answers() produces
  the client-safe version, grade_quiz() scores submissions.
"""

from models.careers_data import get_module
from utils.career_engine import get_career

QUIZ_PASS_PERCENTAGE = 60


# ----------------------------------------------------------------------
# Roadmap generation
# ----------------------------------------------------------------------
def generate_roadmap(user_skills, career_title):
    """
    Build a full roadmap dict for the given target career.
    Returns None if the career title is unknown.
    """
    career = get_career(career_title)
    if not career:
        return None

    user_skill_set = {skill.lower() for skill in user_skills}

    missing_core = [
        skill for skill in career["core_skills"]
        if skill.lower() not in user_skill_set
    ]
    missing_bonus = [
        skill for skill in career["bonus_skills"]
        if skill.lower() not in user_skill_set
    ]

    modules = []
    current_week = 1
    order = 1

    for priority, skills in (("core", missing_core), ("bonus", missing_bonus)):
        for skill in skills:
            module_data = get_module(skill)
            weeks = module_data["weeks"]

            modules.append(
                {
                    "order": order,
                    "skill": skill,
                    "priority": priority,
                    "start_week": current_week,
                    "end_week": current_week + weeks - 1,
                    "weeks": weeks,
                    "resources": module_data["resources"],
                    "videos": module_data["videos"],
                    "quiz": module_data["quiz"],  # includes answers — server only
                    "status": "not_started",       # not_started | in_progress | completed
                    "progress_percent": 0,
                    "quiz_score": None,
                }
            )
            current_week += weeks
            order += 1

    return {
        "career": career["title"],
        "category": career["category"],
        "description": career["description"],
        "total_modules": len(modules),
        "total_weeks": max(current_week - 1, 0),
        "already_have": sorted(
            skill
            for skill in career["core_skills"] + career["bonus_skills"]
            if skill.lower() in user_skill_set
        ),
        "modules": modules,
    }


# ----------------------------------------------------------------------
# Client-safe serialization
# ----------------------------------------------------------------------
def strip_quiz_answers(roadmap_doc):
    """
    Return a deep-copied roadmap safe to send to the browser:
    quiz answers are removed, questions and options are kept.
    """
    safe_modules = []
    for module in roadmap_doc.get("modules", []):
        safe_quiz = [
            {"q": question["q"], "options": question["options"]}
            for question in module.get("quiz", [])
        ]
        safe_module = {
            key: value for key, value in module.items() if key != "quiz"
        }
        safe_module["quiz"] = safe_quiz
        safe_module["quiz_question_count"] = len(safe_quiz)
        safe_modules.append(safe_module)

    return {
        "career": roadmap_doc["career"],
        "category": roadmap_doc["category"],
        "description": roadmap_doc["description"],
        "total_modules": roadmap_doc["total_modules"],
        "total_weeks": roadmap_doc["total_weeks"],
        "already_have": roadmap_doc.get("already_have", []),
        "modules": safe_modules,
    }


# ----------------------------------------------------------------------
# Quiz grading
# ----------------------------------------------------------------------
def grade_quiz(quiz, submitted_answers):
    """
    Grade a quiz submission.

    quiz              : list of {"q", "options", "answer"} (server-side data)
    submitted_answers : list of selected option indexes from the client

    Returns a dict with score, percentage, pass/fail, and per-question
    feedback (including the correct answer, since the attempt is over).
    """
    if not isinstance(submitted_answers, list):
        return None
    if len(submitted_answers) != len(quiz):
        return None

    results = []
    correct_count = 0

    for question, submitted in zip(quiz, submitted_answers):
        try:
            selected = int(submitted)
        except (TypeError, ValueError):
            selected = -1

        is_correct = selected == question["answer"]
        if is_correct:
            correct_count += 1

        results.append(
            {
                "question": question["q"],
                "selected": selected,
                "correct_answer": question["answer"],
                "is_correct": is_correct,
            }
        )

    total = len(quiz)
    percentage = round((correct_count / total) * 100, 1) if total else 0.0

    return {
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "passed": percentage >= QUIZ_PASS_PERCENTAGE,
        "results": results,
    }
