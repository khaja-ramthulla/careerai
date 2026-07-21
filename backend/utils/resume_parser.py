"""
CareerAI — Resume Parser & Skill Extractor

- extract_text(filepath)  : pull raw text from a PDF using PyMuPDF
- extract_skills(text)    : find canonical skills via spaCy PhraseMatcher
- parse_resume(filepath)  : full pipeline -> skills, contact info, education,
                             and lightweight experience signals

The skill taxonomy below is the single source of truth for skill names.
The career engine (utils/career_engine.py) uses the same canonical names,
so extracted skills always align with career requirements.
"""

import re

import fitz  # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher

from models.careers_data import ROLE_HINTS

# ----------------------------------------------------------------------
# Skill taxonomy: canonical name -> list of aliases found in resumes.
# The canonical name itself is always matched too.
# ----------------------------------------------------------------------
SKILL_TAXONOMY = {
    # Programming languages
    "Python": ["python3", "py"],
    "Java": [],
    "JavaScript": ["js", "ecmascript"],
    "TypeScript": ["ts"],
    "C++": ["cpp", "c plus plus"],
    "C#": ["c sharp", "csharp"],
    "C": [],
    "Go": ["golang"],
    "PHP": [],
    "Ruby": [],
    "Swift": [],
    "Kotlin": [],
    "R": ["r programming", "r language"],
    "SQL": ["structured query language"],
    # Web frontend
    "HTML": ["html5"],
    "CSS": ["css3"],
    "React": ["react.js", "reactjs", "react js"],
    "Angular": ["angularjs", "angular.js"],
    "Vue": ["vue.js", "vuejs", "vue js"],
    "Next.js": ["nextjs", "next js"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    "Bootstrap": [],
    "Redux": [],
    "jQuery": [],
    # Backend
    "Node.js": ["nodejs", "node js", "node"],
    "Express": ["express.js", "expressjs"],
    "Django": [],
    "Flask": [],
    "FastAPI": ["fast api"],
    "Spring Boot": ["springboot", "spring"],
    "Laravel": [],
    "REST API": ["rest apis", "restful api", "restful apis", "rest"],
    "GraphQL": [],
    "Microservices": ["micro services", "microservice"],
    # Databases
    "MongoDB": ["mongo db", "mongo"],
    "MySQL": ["my sql"],
    "PostgreSQL": ["postgres", "postgre sql"],
    "Redis": [],
    "SQLite": [],
    "Oracle": ["oracle db", "oracle database"],
    "Firebase": [],
    "Elasticsearch": ["elastic search"],
    # Data science & AI
    "Machine Learning": ["ml"],
    "Deep Learning": ["dl"],
    "Natural Language Processing": ["nlp"],
    "Computer Vision": ["cv", "opencv"],
    "TensorFlow": ["tensor flow"],
    "PyTorch": ["py torch", "torch"],
    "Keras": [],
    "Scikit-learn": ["sklearn", "scikit learn"],
    "Pandas": [],
    "NumPy": ["numpy"],
    "Matplotlib": [],
    "Data Analysis": ["data analytics"],
    "Data Visualization": ["data viz"],
    "Statistics": ["statistical analysis", "statistical modeling"],
    "Big Data": [],
    "Apache Spark": ["pyspark", "spark"],
    "Hadoop": [],
    "Power BI": ["powerbi"],
    "Tableau": [],
    "Excel": ["ms excel", "microsoft excel"],
    "MLOps": ["ml ops"],
    "Generative AI": ["genai", "gen ai", "llm", "llms", "large language models"],
    # DevOps & cloud
    "Docker": [],
    "Kubernetes": ["k8s"],
    "AWS": ["amazon web services"],
    "Azure": ["microsoft azure"],
    "Google Cloud": ["gcp", "google cloud platform"],
    "CI/CD": ["cicd", "continuous integration", "continuous deployment"],
    "Jenkins": [],
    "Terraform": [],
    "Linux": ["unix"],
    "Git": ["github", "gitlab", "version control"],
    "Bash": ["shell scripting", "shell"],
    "Nginx": [],
    # Mobile
    "Android": ["android development"],
    "iOS": ["ios development"],
    "React Native": [],
    "Flutter": ["dart"],
    # Design
    "UI/UX Design": ["ui design", "ux design", "ui ux", "user experience", "user interface"],
    "Figma": [],
    "Adobe XD": ["adobe experience design"],
    "Photoshop": ["adobe photoshop"],
    "Wireframing": ["wireframes"],
    "Prototyping": ["prototypes"],
    # Testing & security
    "Software Testing": ["qa testing", "quality assurance", "manual testing"],
    "Selenium": [],
    "Unit Testing": ["pytest", "junit", "jest"],
    "Cybersecurity": ["cyber security", "information security", "network security"],
    "Penetration Testing": ["pen testing", "ethical hacking"],
    # Soft skills
    "Communication": ["communication skills"],
    "Teamwork": ["team work", "collaboration"],
    "Leadership": ["team leadership"],
    "Problem Solving": ["problem-solving", "analytical skills"],
    "Project Management": ["agile", "scrum", "kanban", "jira"],
    "Time Management": [],
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.sc", "bsc", "m.sc", "msc", "b.tech",
    "btech", "m.tech", "mtech", "bca", "mca", "b.e", "m.e", "mba",
    "diploma", "degree", "undergraduate", "postgraduate", "higher national diploma", "hnd",
]

EDUCATION_LEVELS = [
    ("phd", ["phd", "doctorate"]),
    ("master", ["master", "msc", "m.sc", "mtech", "m.tech", "mba"]),
    ("bachelor", ["bachelor", "bsc", "b.sc", "btech", "b.tech", "b.e", "be"]),
    ("diploma", ["diploma", "certification", "certificate", "hnd"]),
]

EXPERIENCE_REGEX = re.compile(
    r"(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
    re.IGNORECASE,
)

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3}[\s-]?\d{4}")

# ----------------------------------------------------------------------
# spaCy pipeline + PhraseMatcher (built once at import, reused per request)
# ----------------------------------------------------------------------
try:
    _nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "lemmatizer"])
except OSError:
    _nlp = None  # checked at call time in extract_skills

_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")

for canonical, aliases in SKILL_TAXONOMY.items():
    patterns = [_nlp.make_doc(term) for term in [canonical, *aliases]]
    _matcher.add(canonical, patterns)


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def extract_text(filepath):
    """
    Extract raw text from every page of a PDF.
    Raises ValueError if the file cannot be read or contains no text.
    """
    try:
        with fitz.open(filepath) as pdf:
            text = "\n".join(page.get_text("text") for page in pdf)
    except Exception as exc:
        raise ValueError(f"Could not read the PDF file: {exc}") from exc

    text = text.strip()
    if not text:
        raise ValueError(
            "No readable text found in this PDF. "
            "Scanned/image-only resumes are not supported."
        )
    return text


def extract_skills(text):
    """Return a sorted list of canonical skill names found in the text."""
    if _nlp is None:
        raise OSError(
            "spaCy model 'en_core_web_sm' is not installed. "
            "Run: python -m spacy download en_core_web_sm"
        )
    doc = _nlp.make_doc(text)
    found = set()
    for match_id, _start, _end in _matcher(doc):
        found.add(_nlp.vocab.strings[match_id])
    return sorted(found)


def extract_education(text):
    """Return education-related lines detected in the resume text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    education_lines = []
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in EDUCATION_KEYWORDS):
            education_lines.append(line[:160])
        if len(education_lines) == 5:
            break
    return education_lines


def extract_education_level(text):
    """Return the highest education level mentioned in the resume text."""
    lowered = text.lower()
    for level, keywords in EDUCATION_LEVELS:
        if any(keyword in lowered for keyword in keywords):
            return level
    return ""


def extract_experience_years(text):
    """Return the highest explicit experience value detected in years."""
    matches = [float(match.group("years")) for match in EXPERIENCE_REGEX.finditer(text)]
    return round(max(matches), 1) if matches else 0.0


def extract_target_roles(text):
    """Return likely target job titles inferred from the resume header/body."""
    lines = [line.strip().lower() for line in text.splitlines() if line.strip()]
    header_text = " ".join(lines[:12])
    searchable_text = f"{header_text} {text.lower()}"

    inferred_roles = []
    for alias, careers in ROLE_HINTS.items():
        if alias in searchable_text:
            inferred_roles.extend(careers)

    deduped = []
    for role in inferred_roles:
        if role not in deduped:
            deduped.append(role)
    return deduped


def parse_resume(filepath):
    """
    Full parsing pipeline for an uploaded resume PDF.
    Returns a dict ready to store and to feed the career engine.
    """
    text = extract_text(filepath)

    emails = EMAIL_REGEX.findall(text)
    phones = [p.strip() for p in PHONE_REGEX.findall(text) if len(re.sub(r"\D", "", p)) >= 9]

    return {
        "skills": extract_skills(text),
        "education": extract_education(text),
        "education_level": extract_education_level(text),
        "experience_years": extract_experience_years(text),
        "target_roles": extract_target_roles(text),
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "word_count": len(text.split()),
        "char_count": len(text),
        "raw_text": text,
    }


def all_known_skills():
    """Expose the canonical skill list (used by the career engine)."""
    return list(SKILL_TAXONOMY.keys())
