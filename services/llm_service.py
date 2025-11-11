import json
from typing import List, Dict
import openai
import config

class LLMService:
    """Service for interacting with OpenAI for resume analysis"""
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"
    
    def analyze_resume(self, resume_text: str, job_description: str,
                      min_experience: int = 0, max_experience: int = 20,
                      preferred_organizations: List[str] = None) -> Dict:
        """
        Analyze a resume against job requirements using LLM
        """
        
        org_list = ", ".join(preferred_organizations) if preferred_organizations else "any organization"
        
        prompt = f"""
You are an expert HR recruiter. Analyze this resume against the job description and provide a detailed evaluation.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

SCREENING CRITERIA:
- Experience Range: {min_experience}-{max_experience} years
- Preferred Organizations: {org_list}

Provide your analysis in the following JSON format:
{{
    "name": "Candidate full name",
    "email": "candidate email if found, else null",
    "phone": "candidate phone if found, else null",
    "experience_years": <number of years of experience>,
    "current_role": "current or most recent job title",
    "current_company": "current or most recent company",
    "skills": ["skill1", "skill2", "skill3"],
    "education": "highest degree and institution",
    "match_score": <0-100 integer score>,
    "strengths": ["strength1", "strength2", "strength3"],
    "concerns": ["concern1", "concern2"],
    "recommendation": "STRONG_FIT / GOOD_FIT / MODERATE_FIT / WEAK_FIT",
    "summary": "2-3 sentence overall assessment"
}}

Be objective and thorough. Match score should reflect:
- Skills alignment with job requirements (40%)
- Experience level match (30%)
- Company/industry relevance (20%)
- Education and qualifications (10%)
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR recruiter analyzing resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response["choices"][0]["message"]["content"]
            
            # Try to parse JSON from response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(result_text)
                
                # Ensure all required fields exist
                required_fields = {
                    'name': 'Unknown',
                    'email': None,
                    'phone': None,
                    'experience_years': 0,
                    'current_role': 'Not specified',
                    'current_company': 'Not specified',
                    'skills': [],
                    'education': 'Not specified',
                    'match_score': 50,
                    'strengths': [],
                    'concerns': [],
                    'recommendation': 'MODERATE_FIT',
                    'summary': 'Analysis completed'
                }
                
                for field, default in required_fields.items():
                    result.setdefault(field, default)
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Response text: {result_text}")
                
                # Return default structure if parsing fails
                return {
                    'name': 'Parse Error',
                    'email': None,
                    'phone': None,
                    'experience_years': 0,
                    'current_role': 'Error parsing resume',
                    'current_company': 'Unknown',
                    'skills': [],
                    'education': 'Unknown',
                    'match_score': 0,
                    'strengths': [],
                    'concerns': ['Unable to parse resume properly'],
                    'recommendation': 'WEAK_FIT',
                    'summary': 'Resume analysis failed'
                }
                
        except Exception as e:
            print(f"LLM service error: {str(e)}")
            return {
                'name': 'Error',
                'email': None,
                'phone': None,
                'experience_years': 0,
                'current_role': 'Error',
                'current_company': 'Error',
                'skills': [],
                'education': 'Error',
                'match_score': 0,
                'strengths': [],
                'concerns': [f'Error: {str(e)}'],
                'recommendation': 'WEAK_FIT',
                'summary': f'Analysis failed: {str(e)}'
            }
    
    def chat_with_results(self, query: str, candidates: List[Dict], 
                         job_description: str) -> Dict:
        """
        Handle conversational queries about screening results
        """
        
        # Prepare context with top candidates
        top_5 = candidates[:5] if len(candidates) > 5 else candidates
        context = f"Job Description: {job_description}\n\n"
        context += f"Total Candidates: {len(candidates)}\n\n"
        context += "Top Candidates:\n"
        
        for i, candidate in enumerate(top_5, 1):
            context += f"{i}. {candidate.get('name')} - {candidate.get('match_score')}% match\n"
            context += f"   Role: {candidate.get('current_role')} at {candidate.get('current_company')}\n"
            context += f"   Experience: {candidate.get('experience_years')} years\n\n"
        
        prompt = f"""
You are an HR assistant helping to analyze candidate screening results.

CONTEXT:
{context}

USER QUERY:
{query}

Provide a helpful, conversational answer. If the query asks about specific candidates,
provide their details. If it asks for recommendations, suggest the best matches.
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful HR assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            answer = response["choices"][0]["message"]["content"]
            
            return {
                'answer': answer,
                'query': query
            }
            
        except Exception as e:
            return {
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'query': query,
                'error': str(e)
            }