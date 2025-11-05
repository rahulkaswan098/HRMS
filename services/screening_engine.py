import os
from typing import List, Dict
from .llm_service import LLMService
from .resume_parser import ResumeParser

class ScreeningEngine:
    """Main engine for resume screening and candidate evaluation"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.resume_parser = ResumeParser()
    
    def screen_resumes(self, resume_files: List[str], job_description: str, 
                      min_experience: int = 0, max_experience: int = 20,
                      preferred_organizations: List[str] = None) -> Dict:
        """
        Screen multiple resumes against a job description
        
        Args:
            resume_files: List of paths to resume files
            job_description: Job description text
            min_experience: Minimum years of experience
            max_experience: Maximum years of experience
            preferred_organizations: List of preferred company names
            
        Returns:
            Dictionary containing screening results
        """
        candidates = []
        
        for resume_file in resume_files:
            try:
                # Extract text from resume
                resume_text = self.resume_parser.parse_resume(resume_file)
                
                # Analyze resume with LLM
                analysis = self.llm_service.analyze_resume(
                    resume_text=resume_text,
                    job_description=job_description,
                    min_experience=min_experience,
                    max_experience=max_experience,
                    preferred_organizations=preferred_organizations
                )
                
                # Add file info
                analysis['filename'] = os.path.basename(resume_file)
                analysis['filepath'] = resume_file
                
                candidates.append(analysis)
                
            except Exception as e:
                print(f"Error processing {resume_file}: {str(e)}")
                candidates.append({
                    'filename': os.path.basename(resume_file),
                    'filepath': resume_file,
                    'error': str(e),
                    'name': 'Error',
                    'match_score': 0
                })
        
        # Sort candidates by match score
        candidates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Identify top candidate
        top_candidate = candidates[0] if candidates else None
        
        return {
            'candidates': candidates,
            'top_candidate': top_candidate,
            'total_candidates': len(candidates),
            'job_description': job_description,
            'criteria': {
                'min_experience': min_experience,
                'max_experience': max_experience,
                'preferred_organizations': preferred_organizations or []
            }
        }