from app import create_app, db
from app.models.user import User
from app.models.questionnaire import Questionnaire
from app.models.response import Response
from datetime import datetime, timedelta
import random
import json

def create_test_data():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create test user
        user = User(username='test_user', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create sample questionnaire
        questionnaire = Questionnaire(
            title='Customer Satisfaction Survey',
            description='Please help us improve our services',
            created_by=user.id
        )
        
        # Sample questions
        questions = [
            {
                'id': 0,
                'text': 'How satisfied are you with our service?',
                'type': 'multiple_choice',
                'options': ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied']
            },
            {
                'id': 1,
                'text': 'Would you recommend our service to others?',
                'type': 'multiple_choice',
                'options': ['Definitely', 'Probably', 'Not Sure', 'Probably Not', 'Definitely Not']
            },
            {
                'id': 2,
                'text': 'How often do you use our service?',
                'type': 'multiple_choice',
                'options': ['Daily', 'Weekly', 'Monthly', 'Rarely', 'Never']
            }
        ]
        
        questionnaire.set_questions(questions)
        db.session.add(questionnaire)
        db.session.commit()
        
        # Generate sample responses over the last 30 days
        start_date = datetime.utcnow() - timedelta(days=30)
        
        for day in range(31):
            # Generate 1-5 responses per day
            for _ in range(random.randint(1, 5)):
                response = Response(
                    questionnaire_id=questionnaire.id,
                    user_id=user.id,
                    started_at=start_date + timedelta(days=day, 
                                                    hours=random.randint(0, 23),
                                                    minutes=random.randint(0, 59))
                )
                
                # Generate random answers
                answers = {}
                for question in questions:
                    answers[str(question['id'])] = random.choice(question['options'])
                
                response.set_answers(answers)
                
                # Set completion time between 2-10 minutes
                completion_time = random.randint(120, 600)
                response.submitted_at = response.started_at + timedelta(seconds=completion_time)
                response.completion_time = completion_time
                
                db.session.add(response)
        
        db.session.commit()
        
        print("Test data created successfully!")
        print(f"Login credentials - Username: test_user, Password: password123")
        print(f"Questionnaire ID: {questionnaire.id}")

if __name__ == '__main__':
    create_test_data()
