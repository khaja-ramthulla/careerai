"""
CareerAI — Career Recommendation Engine

Hybrid scoring model:
  1. TF-IDF + cosine similarity between the user's skill profile and each
     career's skill document (captures overall profile alignment).
  2. Weighted skill coverage (captures how many *core* requirements are met).
    3. Resume-text alignment, education fit, experience fit, and inferred
         target-role fit for uploads that include richer resume signals.

Final match score blends skills, resume text, education, and experience so
uploaded resumes are scored more dynamically than manual skill lists.

Career definitions live in models/careers_data.py and use the same
canonical skill names as utils/resume_parser.py, so extracted resume
skills align 1:1 with career requirements.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models.careers_data import CAREERS, CAREER_SIGNAL_PROFILE, ROLE_HINTS

SKILL_SIMILARITY_WEIGHT = 0.30
COVERAGE_WEIGHT = 0.34
TEXT_ALIGNMENT_WEIGHT = 0.12
EXPERIENCE_WEIGHT = 0.06
EDUCATION_WEIGHT = 0.04
ROLE_WEIGHT = 0.14
CORE_SKILL_WEIGHT = 2.0
BONUS_SKILL_WEIGHT = 1.0


# ----------------------------------------------------------------------
# Vectorizer setup — each skill is ONE token (multi-word safe).
# Documents are pipe-joined skill lists; fit once at import time.
# ----------------------------------------------------------------------
def _skill_tokenizer(document):
    return document.split("|")


def _career_document(career):
    """Build the skill document for a career (core skills counted twice)."""
    tokens = []
    for skill in career["core_skills"]:
        tokens.extend([skill.lower(), skill.lower()])  # emphasize core skills
    for skill in career["bonus_skills"]:
        tokens.append(skill.lower())
    return "|".join(tokens)


def _career_text(career):
    """Build a natural-language career document for resume text matching."""
    signal_profile = CAREER_SIGNAL_PROFILE.get(career["title"], {})
    return " ".join(
        [
            career["title"],
            career["category"],
            career["description"],
            " ".join(career["core_skills"]),
            " ".join(career["bonus_skills"]),
            " ".join(signal_profile.get("preferred_education", [])),
        ]
    )


_career_titles = [career["title"] for career in CAREERS]
_career_docs = [_career_document(career) for career in CAREERS]
_career_text_docs = [_career_text(career) for career in CAREERS]

_vectorizer = TfidfVectorizer(
    tokenizer=_skill_tokenizer,
    preprocessor=lambda x: x,
    token_pattern=None,
    lowercase=False,
)
_career_matrix = _vectorizer.fit_transform(_career_docs)

_text_vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
_career_text_matrix = _text_vectorizer.fit_transform(_career_text_docs)

_careers_by_title = {career["title"].lower(): career for career in CAREERS}


# ----------------------------------------------------------------------
# Internal scoring
# ----------------------------------------------------------------------
def _coverage_score(user_skill_set, career):
    """Weighted fraction of the career's requirements the user satisfies."""
    total = 0.0
    earned = 0.0

    for skill in career["core_skills"]:
        total += CORE_SKILL_WEIGHT
        if skill.lower() in user_skill_set:
            earned += CORE_SKILL_WEIGHT

    for skill in career["bonus_skills"]:
        total += BONUS_SKILL_WEIGHT
        if skill.lower() in user_skill_set:
            earned += BONUS_SKILL_WEIGHT

    return earned / total if total else 0.0


def _split_skills(user_skill_set, career):
    """Partition career requirements into matched vs missing for the user."""
    matched, missing_core, missing_bonus = [], [], []

    for skill in career["core_skills"]:
        if skill.lower() in user_skill_set:
            matched.append(skill)
        else:
            missing_core.append(skill)

    for skill in career["bonus_skills"]:
        if skill.lower() in user_skill_set:
            matched.append(skill)
        else:
            missing_bonus.append(skill)

    return matched, missing_core, missing_bonus


def _role_fit_score(target_roles, career):
    """Return a role-match score based on inferred resume job titles."""
    if not target_roles:
        return 0.0

    if career["title"] in target_roles:
        return 1.0

    for alias, careers in ROLE_HINTS.items():
        if career["title"] in careers and alias in target_roles:
            return 1.0

    return 0.0


def _experience_score(experience_years, career):
    """Return a soft fit score for the user's experience against a career."""
    if experience_years is None:
        return 0.0

    required_years = float(
        CAREER_SIGNAL_PROFILE.get(career["title"], {}).get("min_experience_years", 0.0)
    )
    if required_years <= 0:
        return 1.0 if experience_years >= 0 else 0.0

    return min(experience_years / required_years, 1.0)


def _education_score(education_level, career):
    """Return a soft fit score for the user's education against a career."""
    if not education_level:
        return 0.0

    preferred_levels = CAREER_SIGNAL_PROFILE.get(career["title"], {}).get(
        "preferred_education", []
    )
    if not preferred_levels:
        return 0.5

    return 1.0 if education_level.lower() in preferred_levels else 0.35


def _text_alignment_score(resume_text):
    if not resume_text:
        return [0.0] * len(CAREERS)

    resume_vector = _text_vectorizer.transform([resume_text])
    return cosine_similarity(resume_vector, _career_text_matrix)[0]


def _normalize_user_profile(user_profile):
    if isinstance(user_profile, dict):
        return {
            "skills": user_profile.get("skills", []),
            "education_level": user_profile.get("education_level", ""),
            "experience_years": user_profile.get("experience_years", 0.0),
            "resume_text": user_profile.get("raw_text", ""),
            "target_roles": user_profile.get("target_roles", []),
        }

    return {
        "skills": user_profile or [],
        "education_level": "",
        "experience_years": 0.0,
        "resume_text": "",
        "target_roles": [],
    }


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def recommend_careers(user_profile, top_n=6):
    """
    Rank all careers for the given user profile or skill list.

    Returns a list of dicts (best match first):
      title, category, description, match_score (0-100),
      matched_skills, missing_core_skills, missing_bonus_skills
    """
    profile = _normalize_user_profile(user_profile)
    user_skill_set = {skill.lower() for skill in profile["skills"]}

    if user_skill_set:
        user_doc = "|".join(sorted(user_skill_set))
        user_vector = _vectorizer.transform([user_doc])
        similarities = cosine_similarity(user_vector, _career_matrix)[0]
    else:
        similarities = [0.0] * len(CAREERS)

    text_similarities = _text_alignment_score(profile["resume_text"])
    target_roles = profile["target_roles"]

    results = []
    for index, career in enumerate(CAREERS):
        coverage = _coverage_score(user_skill_set, career)
        experience = _experience_score(profile["experience_years"], career)
        education = _education_score(profile["education_level"], career)
        role_fit = _role_fit_score(target_roles, career)
        score = (
            SKILL_SIMILARITY_WEIGHT * float(similarities[index])
            + COVERAGE_WEIGHT * coverage
            + TEXT_ALIGNMENT_WEIGHT * float(text_similarities[index])
            + EXPERIENCE_WEIGHT * experience
            + EDUCATION_WEIGHT * education
            + ROLE_WEIGHT * role_fit
        )
        matched, missing_core, missing_bonus = _split_skills(user_skill_set, career)

        results.append(
            {
                "title": career["title"],
                "category": career["category"],
                "description": career["description"],
                "match_score": round(score * 100, 1),
                "matched_skills": matched,
                "missing_core_skills": missing_core,
                "missing_bonus_skills": missing_bonus,
                "experience_fit": round(experience * 100, 1),
                "education_fit": round(education * 100, 1),
                "role_fit": round(role_fit * 100, 1),
            }
        )

    results.sort(key=lambda item: item["match_score"], reverse=True)
    return results[:top_n]


def analyze_skill_gap(user_skills, career_title):
    """
    Detailed gap analysis for one target career.
    Returns None if the career title is unknown.
    """
    career = _careers_by_title.get(career_title.strip().lower())
    if not career:
        return None

    user_skill_set = {skill.lower() for skill in user_skills}
    matched, missing_core, missing_bonus = _split_skills(user_skill_set, career)
    coverage = _coverage_score(user_skill_set, career)

    return {
        "title": career["title"],
        "category": career["category"],
        "description": career["description"],
        "readiness": round(coverage * 100, 1),
        "matched_skills": matched,
        "missing_core_skills": missing_core,
        "missing_bonus_skills": missing_bonus,
        "estimated_weeks": max(1, len(missing_core) * 2 + len(missing_bonus)),
    }


def list_careers():
    """Lightweight career catalog for dropdowns/selection UIs."""
    return [
        {
            "title": career["title"],
            "category": career["category"],
            "description": career["description"],
        }
        for career in CAREERS
    ]


def get_career(career_title):
    """Full career definition (used by the roadmap engine)."""
    return _careers_by_title.get(career_title.strip().lower())
