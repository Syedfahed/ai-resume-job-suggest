from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import spacy
import pandas as pd
from typing import Dict, List, Optional
import asyncio
import io
from PyPDF2 import PdfReader
from docx import Document
import re
from collections import defaultdict
from datetime import datetime

app = FastAPI(title="AI Resume Scanner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model with graceful fallback if model is missing
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = spacy.blank("en")


class ResumeParser:
    def __init__(self):
        self.skills_database = self._load_skills_database()
        self.job_roles = {
  "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Git", "Tailwind", "Next.js", "TypeScript", "Vue.js", "Angular", "Svelte", "Bootstrap", "SASS", "LESS", "Webpack", "Vite", "ESLint", "Prettier", "Redux", "GraphQL", "Apollo Client", "REST APIs", "Web Accessibility (a11y)", "Responsive Design", "Web Performance Optimization", "Jest", "Cypress", "Testing Library", "Figma", "Adobe XD", "WebSockets", "Progressive Web Apps (PWA)"],
  "Backend Developer": ["Python", "Node.js", "Java", "SQL", "MongoDB", "Django", "Express", "Ruby", "Ruby on Rails", "PHP", "Laravel", "Go", "C#", ".NET", "Spring Boot", "PostgreSQL", "MySQL", "Redis", "Elasticsearch", "GraphQL", "REST APIs", "gRPC", "RabbitMQ", "Kafka", "Docker", "Microservices Architecture", "API Design", "OAuth", "JWT", "Serverless", "Unit Testing", "Integration Testing", "Linux", "Nginx", "Apache"],
  "Full Stack Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Express", "Git", "TypeScript", "Vue.js", "Angular", "Next.js", "Tailwind", "SASS", "Python", "Django", "Flask", "Java", "Spring Boot", "REST APIs", "GraphQL", "PostgreSQL", "MySQL", "Redis", "Docker", "AWS", "Microservices", "WebSockets", "Jest", "Cypress", "Mocha", "Chai", "Web Accessibility (a11y)", "Responsive Design", "CI/CD", "Agile Methodologies"],
  "Data Scientist": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Machine Learning", "Deep Learning", "Data Visualization", "Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI", "Jupyter Notebooks", "Statistics", "Probability", "Linear Algebra", "Data Cleaning", "Feature Engineering", "Natural Language Processing (NLP)", "Computer Vision", "Time Series Analysis", "Hadoop", "Spark", "BigQuery", "AWS", "Azure", "Google Cloud Platform", "A/B Testing", "Experiment Design", "Data Wrangling"],
  "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Linux", "Jenkins", "Ansible", "Git", "GitHub Actions", "GitLab CI", "CircleCI", "Azure DevOps", "Google Cloud Platform", "Azure", "Helm", "Prometheus", "Grafana", "ELK Stack", "Nginx", "Apache", "Bash", "Python", "Go", "Infrastructure as Code (IaC)", "CloudFormation", "Pulumi", "Container Orchestration", "Monitoring and Logging", "Security Best Practices", "IAM (Identity and Access Management)", "Network Configuration", "High Availability", "Disaster Recovery"]
}
        self.canonical_skill_by_normalized = {self._normalize_skill(s): s for s in self.skills_database}
        self.normalized_skills_set = set(self.canonical_skill_by_normalized.keys())

    def _normalize_skill(self, text: str) -> str:
        s = text.lower().replace("-", " ")
        s = re.sub(r"[^a-z0-9+#\.\s/]", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _normalize_phone(self, raw: str) -> str:
        digits = re.sub(r"\D", "", raw)
        return ("+" + digits) if raw.strip().startswith("+") else digits

    def _month_to_num(self, month_token: str) -> Optional[int]:
        m = month_token.lower()[:3]
        months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
        return months.get(m)

    def _parse_date(self, text: str, default_to_today: bool = False) -> Optional[datetime]:
        if not text:
            return None
        t = text.strip().lower()
        if t in {"present", "current", "now"}:
            return datetime.today()
        m = re.search(r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})", t, flags=re.IGNORECASE)
        if m:
            month_num = self._month_to_num(m.group(1))
            year_num = int(m.group(2))
            if month_num:
                return datetime(year_num, month_num, 1)
        y = re.search(r"\b(\d{4})\b", t)
        if y:
            return datetime(int(y.group(1)), 1, 1)
        return datetime.today() if default_to_today else None

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        texts = []
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n".join(texts)

    def extract_text_from_docx(self, file_content: bytes) -> str:
        doc = Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def extract_contact_info(self, text: str) -> Dict:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}'

        emails = re.findall(email_pattern, text)
        phone_matches = re.findall(phone_pattern, text)

        first_email = emails[0] if emails else None
        first_phone = self._normalize_phone(phone_matches[0]) if phone_matches else None

        return {"email": first_email, "phone": first_phone}

    def extract_skills(self, text: str) -> List[str]:
        normalized = self._normalize_skill(text)
        tokens = [t for t in normalized.split(" ") if t]
        found = set()

        max_n = 4
        for n in range(1, max_n + 1):
            for i in range(len(tokens) - n + 1):
                phrase = " ".join(tokens[i:i+n]).strip()
                if phrase in self.normalized_skills_set:
                    found.add(self.canonical_skill_by_normalized[phrase])

        return sorted(found)

    def extract_experience(self, text: str) -> List[Dict]:
        experiences: List[Dict] = []
        patterns = [
            r'(?P<start>(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4})\s*[-–—]\s*(?P<end>(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}|present|current|now)',
            r'(?P<start>\d{4})\s*[-–—]\s*(?P<end>\d{4}|present|current|now)'
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start_raw = match.group('start')
                end_raw = match.group('end')
                start_dt = self._parse_date(start_raw)
                end_dt = self._parse_date(end_raw, default_to_today=True)
                if not start_dt or not end_dt or end_dt < start_dt:
                    continue

                months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 100)
                experiences.append({
                    "start_date": start_dt.strftime("%Y-%m"),
                    "end_date": end_dt.strftime("%Y-%m"),
                    "months": months,
                    "context": text[context_start:context_end]
                })

        return experiences

    def ai_recommend_jobs_and_skills(self, user_skills: List[str]) -> Dict:
        user_norm = {self._normalize_skill(s) for s in user_skills}
        job_scores: Dict[str, float] = {}
        skills_to_learn: Dict[str, List[str]] = {}

        for job, required_skills in self.job_roles.items():
            req_norm = {self._normalize_skill(s) for s in required_skills}
            matched_norm = user_norm & req_norm
            score = len(matched_norm) / max(1, len(req_norm))
            job_scores[job] = score
            missing_norm = req_norm - user_norm
            skills_to_learn[job] = [self.canonical_skill_by_normalized.get(s, s.title()) for s in sorted(missing_norm)]

        recommended_jobs = sorted(job_scores, key=job_scores.get, reverse=True)[:3]
        recommended_skills = sorted({skill for job in recommended_jobs for skill in skills_to_learn[job]})

        return {
            "recommended_jobs": recommended_jobs,
            "skills_to_develop": recommended_skills,
            "job_match_ratios": {job: job_scores[job] for job in recommended_jobs}
        }

    def _load_skills_database(self) -> List[str]:
        return [
            "Python", "JavaScript", "React", "Node.js", "Django", "Flask",
            "Machine Learning", "Data Science", "SQL", "MongoDB", "AWS",
            "Docker", "Kubernetes", "Git", "HTML", "CSS", "Java", "C++",
            "Project Management", "Agile", "Scrum", "Leadership", "Tailwind",
            "Next.js", "Pandas", "Scikit-learn", "Numpy", "Express", "Terraform", "CI/CD", "Linux"
        ]


parser = ResumeParser()


@app.post("/api/upload-resume")
async def upload_resume(resume: UploadFile = File(...)):
    filename_lower = (resume.filename or "").lower()
    if not filename_lower.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    try:
        content = await resume.read()

        if filename_lower.endswith('.pdf'):
            text = parser.extract_text_from_pdf(content)
        elif filename_lower.endswith('.docx'):
            text = parser.extract_text_from_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        contact_info = parser.extract_contact_info(text)
        skills = parser.extract_skills(text)
        experience = parser.extract_experience(text)
        recommendations = parser.ai_recommend_jobs_and_skills(skills)

        word_count = len(text.split())
        skill_count = len(skills)
        total_months = sum((item.get("months") or 0) for item in experience)
        experience_years = round(total_months / 12.0, 1)
        top_ratio = 0.0
        if isinstance(recommendations, dict) and recommendations.get("job_match_ratios"):
            top_ratio = max(recommendations["job_match_ratios"].values())
        score = min(100, int(top_ratio * 60) + min(25, int(experience_years * 5)) + min(15, word_count // 50))

        return {
            "filename": resume.filename,
            "contact_info": contact_info,
            "skills": skills,
            "experience": experience,
            "metrics": {
                "word_count": word_count,
                "skill_count": skill_count,
                "experience_years": experience_years,
                "experience_months": total_months,
                "experience_entries": len(experience),
                "overall_score": score
            },
            "recommendations": recommendations,
            "raw_text": text[:500] + "..." if len(text) > 500 else text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Resume scanner API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
