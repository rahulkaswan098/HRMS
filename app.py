from flask import Flask, render_template, request, jsonify, send_file, session
import os
import config
from services.screening_engine import ScreeningEngine
from utils.file_handler import FileHandler
from utils.output_generator import OutputGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE * 50  # Allow multiple files

# Initialize services
screening_engine = ScreeningEngine()
file_handler = FileHandler()
output_generator = OutputGenerator()

# Store results in session (for demo - in production use database)
screening_results = {}


@app.route('/')
def landing():
    """Landing page with feature selection"""
    return render_template('index.html')


@app.route('/screening')
def screening():
    """Resume screening page"""
    return render_template('screening.html')


@app.route('/gdpr-chatbot')
def gdpr_chatbot():
    """GDPR chatbot page"""
    return render_template('gdpr_chatbot.html')


@app.route('/jd-creator')
def jd_creator():
    """JD creator page"""
    return render_template('jd_creator.html')


@app.route('/screen', methods=['POST'])
def screen_resumes():
    """Process resume screening request"""
    try:
        # Get form data
        job_description = request.form.get('job_description', '')
        min_experience = int(request.form.get('min_experience', 0))
        max_experience = int(request.form.get('max_experience', 20))
        organizations = request.form.get('organizations', '')
        
        # Parse organizations
        org_list = [org.strip() for org in organizations.split(',') if org.strip()] if organizations else None
        
        # Get uploaded files
        files = request.files.getlist('resumes')
        
        if not files or len(files) == 0:
            return jsonify({'error': 'No files uploaded'}), 400
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Save files
        saved_paths, session_id = file_handler.save_files(files)
        
        if not saved_paths:
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        # Screen resumes
        results = screening_engine.screen_resumes(
            resume_files=saved_paths,
            job_description=job_description,
            min_experience=min_experience,
            max_experience=max_experience,
            preferred_organizations=org_list
        )
        
        # Store results
        screening_results[session_id] = {
            'results': results,
            'file_paths': saved_paths
        }
        
        return jsonify({'session_id': session_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<session_id>')
def show_results(session_id):
    """Display screening results"""
    if session_id not in screening_results:
        return "Results not found", 404
    
    results = screening_results[session_id]['results']
    return render_template('results.html', results=results, session_id=session_id)


@app.route('/candidate-report/<session_id>/<int:candidate_index>')
def candidate_report(session_id, candidate_index):
    """Show detailed report for a candidate"""
    if session_id not in screening_results:
        return "Results not found", 404
    
    results = screening_results[session_id]['results']
    candidates = results.get('candidates', [])
    
    if candidate_index >= len(candidates):
        return "Candidate not found", 404
    
    candidate = candidates[candidate_index]
    html_report = output_generator.generate_candidate_report(candidate, session_id)
    
    return html_report


@app.route('/download/excel/<session_id>')
def download_excel(session_id):
    """Download Excel report"""
    if session_id not in screening_results:
        return "Results not found", 404
    
    results = screening_results[session_id]['results']
    filepath = output_generator.generate_excel(results, session_id)
    
    return send_file(filepath, as_attachment=True)


@app.route('/download/json/<session_id>')
def download_json(session_id):
    """Download JSON report"""
    if session_id not in screening_results:
        return "Results not found", 404
    
    results = screening_results[session_id]['results']
    filepath = output_generator.generate_json(results, session_id)
    
    return send_file(filepath, as_attachment=True)


@app.route('/gdpr-chatbot/ask', methods=['POST'])
def gdpr_chatbot_ask():
    """Handle GDPR chatbot questions"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Import GDPR service
        from services.gdpr_service import GDPRChatbotService
        gdpr_bot = GDPRChatbotService()
        
        result = gdpr_bot.ask_question(question)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/jd-creator/generate', methods=['POST'])
def jd_creator_generate():
    """Generate job description"""
    try:
        data = request.get_json()
        
        # Import JD service
        from services.jd_service import JDGeneratorService
        jd_bot = JDGeneratorService()
        
        result = jd_bot.generate_jd(
            role_title=data.get('role_title', ''),
            experience_range=data.get('experience_range', ''),
            department=data.get('department', ''),
            location=data.get('location', ''),
            employment_type=data.get('employment_type', ''),
            key_responsibilities=data.get('key_responsibilities', ''),
            required_skills=data.get('required_skills', ''),
            additional_info=data.get('additional_info', '')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create necessary folders
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
    os.makedirs('gdpr_chroma', exist_ok=True)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )