
import gradio as gr
from pypdf import PdfReader

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau",
    "pandas", "numpy", "machine learning", "data analysis",
    "data visualization", "statistics", "communication",
    "project management", "problem solving", "cloud computing",
    "aws", "azure", "html", "css", "javascript"
]


def analyze_resume(file_path, job_description):
    if not file_path:
        return "Please upload a PDF resume.", "", ""

    try:
        reader = PdfReader(file_path)
        resume_text = " ".join(
            page.extract_text() or "" for page in reader.pages
        ).lower()
    except Exception:
        return (
            "Could not read this PDF. Please try another file.",
            "",
            ""
        )

    if not resume_text.strip():
        return (
            "No readable text found. Please use a text-based PDF.",
            "",
            ""
        )

    found_skills = [
        skill for skill in SKILLS if skill in resume_text
    ]

    missing_skills = [
        skill for skill in SKILLS if skill not in resume_text
    ]

    score = round(len(found_skills) / len(SKILLS) * 100)

    # Compare resume keywords with the job description.
    job_words = {
        word.strip(".,:;()[]{}!?\"'").lower()
        for word in job_description.split()
        if len(word.strip(".,:;()[]{}!?\"'")) > 2
    }

    resume_words = set(resume_text.split())
    matching_words = sorted(job_words & resume_words)

    report = f"""
# Resume Analysis Report

## Resume Keyword Score: {score}/100

This score measures matches against a predefined list of
20 skills. It is not a professional hiring prediction.

## Skills Found
{", ".join(found_skills) if found_skills else "No listed skills found."}

## Skills Not Detected
{", ".join(missing_skills)}

## Resume Length
Approximately {len(resume_text.split())} words.
"""

    job_report = f"""
## Job Description Keyword Check

Matching words: {", ".join(matching_words[:40])
if matching_words else "No matching words detected."}

**Tip:** Add relevant skills only when you genuinely have them.
Tailor your resume to the actual requirements of the job.
"""

    suggestions = []

    if len(resume_text.split()) < 150:
        suggestions.append("Add more detail about your education and projects.")

    if not any(word in resume_text for word in ["project", "projects"]):
        suggestions.append("Include relevant academic or personal projects.")

    if not any(word in resume_text for word in ["experience", "internship"]):
        suggestions.append("Add relevant internship or practical experience, if applicable.")

    if not any(word in resume_text for word in ["education", "university", "degree"]):
        suggestions.append("Make your education section clear.")

    if not suggestions:
        suggestions.append(
            "Review the job description and make sure your strongest "
            "relevant achievements are easy to find."
        )

    suggestions_text = "\n".join(
        f"- {suggestion}" for suggestion in suggestions
    )

    return report, job_report, suggestions_text


with gr.Blocks(theme=gr.themes.Soft(), title="AI Resume Analyzer") as demo:
    gr.Markdown("# AI Resume Analyzer")
    gr.Markdown(
        "Upload your resume to review skill keywords and "
        "receive suggestions for improvement."
    )

    resume_file = gr.File(
        label="Upload Resume (PDF)",
        file_types=[".pdf"],
        type="filepath"
    )

    job_description = gr.Textbox(
        label="Paste Job Description (Optional)",
        placeholder="Paste the internship or job requirements here...",
        lines=5
    )

    analyze_button = gr.Button("Analyze My Resume", variant="primary")

    report_output = gr.Markdown()
    job_output = gr.Markdown()
    suggestions_output = gr.Markdown()

    analyze_button.click(
        fn=analyze_resume,
        inputs=[resume_file, job_description],
        outputs=[report_output, job_output, suggestions_output]
    )

if __name__ == "__main__":
    demo.launch()
