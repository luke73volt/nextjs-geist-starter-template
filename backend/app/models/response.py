from datetime import datetime
import json
from app import db

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON field storing answers
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    completion_time = db.Column(db.Float)  # in seconds
    
    def set_answers(self, answers):
        """Set answers as JSON string"""
        self.answers = json.dumps(answers)
    
    def get_answers(self):
        """Get answers as Python object"""
        return json.loads(self.answers) if self.answers else {}
    
    def submit(self):
        """Mark response as submitted and calculate completion time"""
        self.submitted_at = datetime.utcnow()
        if self.started_at:
            self.completion_time = (self.submitted_at - self.started_at).total_seconds()
    
    def to_dict(self):
        return {
            'id': self.id,
            'questionnaire_id': self.questionnaire_id,
            'user_id': self.user_id,
            'answers': self.get_answers(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'completion_time': self.completion_time
        }

    @staticmethod
    def get_analytics(questionnaire_id):
        """Get detailed analytics for a questionnaire's responses"""
        responses = Response.query.filter_by(questionnaire_id=questionnaire_id).all()
        
        if not responses:
            return {
                'response_count': 0,
                'completion_stats': None,
                'answer_distribution': None,
                'time_series_data': None
            }
        
        # Basic response statistics
        total_responses = len(responses)
        completed_responses = len([r for r in responses if r.submitted_at])
        
        # Completion time statistics
        completion_times = [r.completion_time for r in responses if r.completion_time]
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Answer distribution
        answer_distribution = {}
        for response in responses:
            answers = response.get_answers()
            for q_id, answer in answers.items():
                if q_id not in answer_distribution:
                    answer_distribution[q_id] = {}
                if answer not in answer_distribution[q_id]:
                    answer_distribution[q_id][answer] = 0
                answer_distribution[q_id][answer] += 1
        
        # Time series data (responses over time)
        time_series = {}
        for response in responses:
            date_key = response.started_at.date().isoformat()
            if date_key not in time_series:
                time_series[date_key] = 0
            time_series[date_key] += 1
        
        return {
            'response_count': {
                'total': total_responses,
                'completed': completed_responses,
                'completion_rate': completed_responses / total_responses if total_responses > 0 else 0
            },
            'completion_stats': {
                'average_time': avg_completion_time,
                'min_time': min(completion_times) if completion_times else None,
                'max_time': max(completion_times) if completion_times else None
            },
            'answer_distribution': answer_distribution,
            'time_series_data': [
                {'date': date, 'count': count}
                for date, count in sorted(time_series.items())
            ]
        }
