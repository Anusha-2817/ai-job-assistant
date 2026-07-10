import json
from agents.job_agent import job_analyzer
from agents.resume_agent import resume_analyzer
from agents.cover_letter_agent import cover_letter_writer
from agents.scoring_agent import skill_matcher
from agents.ontology_agent import SkillOntologyAgent

from agents.resume_parser_agent import ResumeIngestionAgent
with open("data/data.json", "r") as f:
    ontology = json.load(f)

ontology_agent = SkillOntologyAgent(ontology)

def coordinator(job_text, resume_file_path, ontology_agent, user_name):
    ingestion_agent = ResumeIngestionAgent()
    resume_data = ingestion_agent.process_resume(resume_file_path)

    sections = resume_data["sections"]
    full_text = resume_data["full_text"]
    # sections = ingestion_agent.process_resume("resume.pdf")
    job_skills = job_analyzer(job_text, ontology_agent) #extraction
    resume_skills = resume_analyzer(sections,full_text,ontology_agent)
    enriched_job_skills = ontology_agent.enrich_skills(job_skills) #enrichh
    enriched_resume_skills = ontology_agent.enrich_skills(resume_skills)
    skill_match = skill_matcher(enriched_job_skills, enriched_resume_skills) #match them
    cover_letter = cover_letter_writer(
    job_text,
    full_text,
    user_name,
    skill_match,
    enriched_job_skills,
    enriched_resume_skills
)

    return {
    "job_skills": job_skills,
    "resume_skills": resume_skills,
    "enriched_job_skills": enriched_job_skills,
    "enriched_resume_skills": enriched_resume_skills,
    "skill_match": skill_match,
    "cover_letter": cover_letter
    }