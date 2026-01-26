from flask import Flask, request, jsonify
from agents import job_analyzer, resume_analyzer, cover_letter_writer, skill_matcher

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    job = data["job"]
    resume = data["resume"]

    job_skills = job_analyzer(job)
    resume_skills = resume_analyzer(resume)
    cover_letter = cover_letter_writer(job, resume)

    return jsonify({
        "job_skills": job_skills,
        "resume_skills": resume_skills,
        "skill_match": skill_matcher(job_skills, resume_skills),
        "cover_letter": cover_letter
    })

if __name__ == "__main__":
    app.run(debug=False)

