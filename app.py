from flask import Flask, render_template, request, jsonify

# ⭐ Import ATS Engine
from ats_engine import analyze_resume_with_ai

# ⭐ Import PDF Extractor from utils.py
from utils import extract_text_from_pdf

app = Flask(__name__)

# -----------------------------------
# HOME PAGE
# -----------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------------
# ANALYZE ROUTE — returns JSON
# -----------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files["resume"]
    job_desc = request.form.get("job_desc", "")

    if resume_file.filename == "":
        return jsonify({"error": "Empty file submitted"}), 400

    if not job_desc.strip():
        return jsonify({"error": "Job description is required"}), 400

    try:
        # ⭐ Extract Resume Text using utils.py
        resume_text = extract_text_from_pdf(resume_file)

        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from PDF. Please ensure it is not a scanned image."}), 400

        # ⭐ Call ATS PRO Engine
        result = analyze_resume_with_ai(resume_text, job_desc)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# -----------------------------------
# RUN APP
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True)
