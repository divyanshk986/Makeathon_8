import re
from difflib import get_close_matches
from collections import Counter

# --------------------------------
# 1. SKILL DATABASE + SYNONYMS
# --------------------------------
SKILLS_DB = {
    "python": ["python","py"],
    "java": ["java"],
    "c++": ["c++","cpp"],
    "machine learning": ["machine learning","ml"],
    "deep learning": ["deep learning","dl"],
    "flask": ["flask"],
    "django": ["django"],
    "sql": ["sql","mysql","postgres"],
    "mongodb": ["mongodb","mongo"],
    "react": ["react","reactjs"],
    "node": ["node","nodejs"],
    "data analysis": ["data analysis","analytics"]
}

SKILL_WEIGHTS = {
    "python":10,"machine learning":12,"deep learning":12,
    "flask":8,"django":8,"sql":9,"mongodb":7,
    "react":8,"node":8,"java":9,"c++":9,"data analysis":10
}

ROLE_MAP = {
    "Backend Engineer":["python","flask","django","sql","mongodb","node"],
    "Frontend Developer":["react"],
    "Data Analyst":["data analysis","sql","python"],
    "ML Engineer":["machine learning","deep learning","python"]
}

# --------------------------------
# 2. TEXT CLEANING
# --------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9+# ]',' ',text)
    return text

# --------------------------------
# 3. SMART SKILL EXTRACTION
# --------------------------------
def extract_skills(text):
    text = clean_text(text)
    words = text.split()
    found = []

    for skill,variants in SKILLS_DB.items():
        for v in variants:
            if v in text:
                found.append(skill)
                break

            match = get_close_matches(v,words,n=1,cutoff=0.85)
            if match:
                found.append(skill)
                break

    return list(set(found))

# --------------------------------
# 4. EXPERIENCE DETECTION
# --------------------------------
def detect_experience(text):
    matches = re.findall(r'(\d+)\s*(years|yrs)',text.lower())
    if matches:
        return sum(int(m[0]) for m in matches)
    return 0

# --------------------------------
# 5. RESUME SECTION DETECTOR
# --------------------------------
def detect_sections(text):
    text = text.lower()
    sections = []

    if "project" in text:
        sections.append("Projects")
    if "education" in text:
        sections.append("Education")
    if "skill" in text:
        sections.append("Skills")
    if "experience" in text or "intern" in text:
        sections.append("Experience")

    return sections

# --------------------------------
# 6. SIMPLE NLP KEYWORD SCORE
# --------------------------------
def keyword_score(resume_text,job_desc):
    resume_words = Counter(clean_text(resume_text).split())
    job_words = Counter(clean_text(job_desc).split())

    common = sum(1 for w in job_words if w in resume_words)

    if len(job_words)==0:
        return 50

    return int((common/len(job_words))*100)

# --------------------------------
# 7. ROLE PREDICTION
# --------------------------------
def predict_roles(skills):
    role_scores = {}

    for role,role_skills in ROLE_MAP.items():
        score = len(set(skills)&set(role_skills))
        if score>0:
            role_scores[role]=score

    sorted_roles = sorted(role_scores,key=role_scores.get,reverse=True)
    return sorted_roles[:3]

# --------------------------------
# 8. DYNAMIC FEEDBACK GENERATOR
# --------------------------------
def generate_feedback(matched,missing,sections,exp_years):
    strengths=[]
    improvements=[]

    if len(matched)>=3:
        strengths.append("Strong technical skill alignment with job description")
    if exp_years>0:
        strengths.append(f"{exp_years}+ years experience detected")
    if "Projects" in sections:
        strengths.append("Projects section strengthens practical exposure")

    if len(missing)>0:
        improvements.append("Add missing skills: "+", ".join(missing))
    if "Experience" not in sections:
        improvements.append("Include internships or experience section")
    if "Skills" not in sections:
        improvements.append("Add a dedicated skills section")

    if len(strengths)==0:
        strengths.append("Basic keyword presence detected")

    return strengths,improvements

# --------------------------------
# 9. ATS PRO ANALYZER
# --------------------------------
def analyze_resume_with_ai(resume_text,job_desc):

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc)

    matched = list(set(resume_skills)&set(job_skills))
    missing = list(set(job_skills)-set(resume_skills))

    # weighted scoring
    total_weight=sum(SKILL_WEIGHTS.get(s,5) for s in job_skills)
    matched_weight=sum(SKILL_WEIGHTS.get(s,5) for s in matched)

    skill_score = int((matched_weight/total_weight)*100) if total_weight else 50
    nlp_score = keyword_score(resume_text,job_desc)
    exp_years = detect_experience(resume_text)

    exp_bonus=min(exp_years*2,10)

    final_score=min(int(skill_score*0.7+nlp_score*0.3+exp_bonus),100)

    sections=detect_sections(resume_text)
    strengths,improvements=generate_feedback(matched,missing,sections,exp_years)
    roles=predict_roles(resume_skills)

    # AI-style reasoning output (hackathon demo gold 🔥)
    reasoning = f"""
    Resume analyzed using offline NLP scoring.
    {len(matched)} key skills matched against job requirements.
    Experience signals contributed {exp_bonus} bonus points.
    Section detection found: {', '.join(sections) if sections else 'limited structure'}.
    """

    return {
        "ats_score":final_score,
        "matched_skills":matched,
        "missing_skills":missing,
        "experience_detected_years":exp_years,
        "resume_sections_detected":sections,
        "resume_strengths":strengths,
        "resume_improvements":improvements,
        "career_suggestions":[
            "Align resume keywords with job description",
            "Highlight measurable project outcomes",
            "Focus on role-specific technical stack"
        ],
        "recommended_roles":roles,
        "ai_reasoning":reasoning.strip()
    }