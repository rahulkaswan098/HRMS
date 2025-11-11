import openai
import config
import json

class JDGeneratorService:
    """NeuronIQ AI – Job Description Creator"""

    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"

    def generate_jd(self, role_title, experience_range, department, location, employment_type, key_responsibilities, required_skills, additional_info=""):
        """
        Generate a structured Job Description based on company tone and template.
        """

        company_template = """
Company: NeuronIQ AI
Industry: Artificial Intelligence SaaS
Tone: Professional, inclusive, forward-thinking
Values: Innovation, Collaboration, Integrity, Continuous Learning

Standard JD Template:
1. Job Title
2. About NeuronIQ AI (pre-filled)
3. Role Overview
4. Key Responsibilities
5. Required Skills
6. Preferred Qualifications
7. Employment Details
8. Why Join Us
"""

        prompt = f"""
You are an expert HR content writer at NeuronIQ AI, an AI SaaS startup.
Using the standard company template, create a professional, structured Job Description.

Role Title: {role_title}
Experience Range: {experience_range}
Department: {department}
Location: {location}
Employment Type: {employment_type}

Key Responsibilities:
{key_responsibilities}

Required Skills:
{required_skills}

Additional Notes from HR:
{additional_info}

Return the JD as valid JSON with this structure:
{{
  "job_title": "",
  "about_company": "",
  "role_overview": "",
  "key_responsibilities": ["", "", ""],
  "required_skills": ["", "", ""],
  "preferred_qualifications": ["", "", ""],
  "experience_range": "",
  "department": "",
  "employment_type": "",
  "location": "",
  "why_join_us": ""
}}
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant at NeuronIQ AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )

            jd_text = response["choices"][0]["message"]["content"]

            try:
                jd_data = json.loads(jd_text)
            except json.JSONDecodeError:
                jd_data = {"full_text": jd_text}

            return jd_data

        except Exception as e:
            return {"error": str(e)}