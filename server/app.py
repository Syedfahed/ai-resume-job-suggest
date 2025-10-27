from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import asyncio
import io
from PyPDF2 import PdfReader
from docx import Document
import re
from collections import defaultdict
from typing import Optional

app = FastAPI(title="AI Resume Scanner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional spaCy support
nlp: Optional[object] = None


def _load_spacy_nlp() -> Optional[object]:
    try:
        import spacy  # type: ignore
    except Exception:
        return None
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        try:
            from spacy.cli import download as spacy_download  # type: ignore
            spacy_download("en_core_web_sm")
            return spacy.load("en_core_web_sm")
        except Exception:
            return None


nlp = _load_spacy_nlp()


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

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
        return text

    def extract_text_from_docx(self, file_content: bytes) -> str:
        doc = Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def extract_contact_info(self, text: str) -> Dict:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(?:\+?\d[\d\-\s().]{7,}\d)'

        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)

        return {
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None
        }

    def extract_skills(self, text: str) -> List[str]:
        found_skills = []

        for skill in self.skills_database:
            if skill.lower() in text.lower():
                found_skills.append(skill)

        if nlp is not None:
            doc = nlp(text.lower())
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE"]:
                    if ent.text.title() not in found_skills:
                        found_skills.append(ent.text.title())

        return list(set(found_skills))

    def extract_experience(self, text: str) -> List[Dict]:
        experiences = []

        experience_patterns = [
            r'(\w+\s+\d{4})\s*-\s*(\w+\s+\d{4}|\w+)',
            r'(\d{4})\s*-\s*(\d{4}|present|current)'
        ]

        for pattern in experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                experiences.append({
                    "start_date": match.group(1),
                    "end_date": match.group(2),
                    "context": text[max(0, match.start() - 100):match.end() + 100]
                })

        return experiences

    def ai_recommend_jobs_and_skills(self, user_skills: List[str]) -> Dict:
        job_scores = defaultdict(int)
        skills_to_learn = defaultdict(list)

        def rough_similarity(a: str, b: str) -> float:
            a_l = a.lower()
            b_l = b.lower()
            if a_l == b_l:
                return 1.0
            if a_l in b_l or b_l in a_l:
                return 0.9
            return 0.0

        for job, required_skills in self.job_roles.items():
            matched = set()
            for skill in required_skills:
                for user_skill in user_skills:
                    sim = (
                        nlp(skill.lower()).similarity(nlp(user_skill.lower()))
                        if nlp is not None
                        else rough_similarity(skill, user_skill)
                    )
                    if sim > 0.75:
                        matched.add(skill)
                        break
            score = len(matched)
            job_scores[job] = score
            missing = set(required_skills) - matched
            skills_to_learn[job] = list(missing)

        recommended_jobs = sorted(job_scores, key=job_scores.get, reverse=True)[:2]
        recommended_skills = list(set(skill for job in recommended_jobs for skill in skills_to_learn[job]))

        return {
            "recommended_jobs": recommended_jobs,
            "skills_to_develop": recommended_skills
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
    if not resume.filename.endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    try:
        content = await resume.read()

        if resume.filename.endswith('.pdf'):
            text = parser.extract_text_from_pdf(content)
        elif resume.filename.endswith(('.docx', '.doc')):
            text = parser.extract_text_from_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        contact_info = parser.extract_contact_info(text)
        skills = parser.extract_skills(text)
        experience = parser.extract_experience(text)
        recommendations = parser.ai_recommend_jobs_and_skills(skills)

        word_count = len(text.split())
        skill_count = len(skills)
        score = min(100, (skill_count * 5) + min(50, word_count // 10))

        return {
            "filename": resume.filename,
            "contact_info": contact_info,
            "skills": skills,
            "experience": experience,
            "metrics": {
                "word_count": word_count,
                "skill_count": skill_count,
                "experience_years": len(experience),
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
