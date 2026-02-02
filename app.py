import streamlit as st
from main import coordinator

st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide"
)

st.title("🤖 AI Resume Analyzer")
st.write("Paste a job description and your resume to see how well you match.")

col1, col2 = st.columns(2)

with col1:
    job_text = st.text_area(
        "📌 Job Description",
        height=250,
        placeholder="Paste the job description here..."
    )

with col2:
    resume_text = st.text_area(
        "📄 Resume",
        height=250,
        placeholder="Paste your resume here..."
    )

if st.button("🔍 Analyze"):
    if not job_text or not resume_text:
        st.warning("Please enter both job description and resume.")
    else:
        with st.spinner("Analyzing..."):
            result = coordinator(job_text, resume_text)

        st.success("Done!")

        st.metric(
            label="Resume Match Percentage",
            value=f"{result['skill_match']['match_percent']}%"
        )
        st.subheader("🧠 Extracted Skills")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Job Skills")
            st.write(result["job_skills"])

        with c2:
            st.markdown("### Resume Skills")
            st.write(result["resume_skills"])

        st.subheader("📊 Skill Match Analysis")
        st.markdown("**Matched Skills**")
        st.write(result["skill_match"]["matched_skills"])

        st.markdown("**Missing Skills**")
        st.write(result["skill_match"]["missing_skills"])
        

        st.subheader("✍️ AI-Generated Cover Letter")
        st.text_area(
            "Generated Cover Letter",
            value=result["cover_letter"],
            height=300
        )
