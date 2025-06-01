from datetime import datetime
import json
from app import db

class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    questions = db.Column(db.Text, nullable=False)  # JSON field storing array of questions
    settings = db.Column(db.Text)  # JSON field for questionnaire configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    responses = db.relationship('Response', backref='questionnaire', lazy='dynamic')
    
    def set_questions(self, questions):
        """Set questions as JSON string"""
        self.questions = json.dumps(questions)
    
    def get_questions(self):
        """Get questions as Python object"""
        return json.loads(self.questions) if self.questions else []
    
    def set_settings(self, settings):
        """Set settings as JSON string"""
        self.settings = json.dumps(settings)
    
    def get_settings(self):
        """Get settings as Python object"""
        return json.loads(self.settings) if self.settings else {}
    
    def get_statistics(self):
        """Calculate basic statistics for the questionnaire"""
        responses = self.responses.all()
        total_responses = len(responses)
        
        if total_responses == 0:
            return {
                'total_responses': 0,
                'completion_rate': 0,
                'average_time': 0,
                'question_stats': []
            }
        
        # Calculate completion time statistics
        completion_times = [
            (r.submitted_at - r.started_at).total_seconds()
            for r in responses
            if r.submitted_at and r.started_at
        ]
        
        avg_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Calculate per-question statistics
        questions = self.get_questions()
        question_stats = []
        
        for q_idx, question in enumerate(questions):
            if question['type'] == 'multiple_choice':
                # Count responses for each option
                option_counts = {}
                for response in responses:
                    answers = json.loads(response.answers)
                    if str(q_idx) in answers:
                        answer = answers[str(q_idx)]
                        option_counts[answer] = option_counts.get(answer, 0) + 1
                
                question_stats.append({
                    'question_id': q_idx,
                    'question_text': question['text'],
                    'type': question['type'],
                    'option_distribution': option_counts,
                    'response_rate': len(option_counts) / total_responses
                })
        
        return {
            'total_responses': total_responses,
            'completion_rate': len(completion_times) / total_responses,
            'average_time': avg_time,
            'question_stats': question_stats
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'questions': self.get_questions(),
            'settings': self.get_settings(),
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }
