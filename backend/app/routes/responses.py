from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.questionnaire import Questionnaire
from app.models.response import Response

bp = Blueprint('responses', __name__, url_prefix='/api/responses')

@bp.route('/questionnaire/<int:questionnaire_id>', methods=['POST'])
@login_required
def submit_response(questionnaire_id):
    """Submit a response to a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    data = request.get_json()
    
    if not data or 'answers' not in data:
        return jsonify({'error': 'Missing answers'}), 400
    
    # Create new response
    response = Response(
        questionnaire_id=questionnaire_id,
        user_id=current_user.id,
        started_at=datetime.utcnow()
    )
    response.set_answers(data['answers'])
    response.submit()  # Sets submitted_at and calculates completion_time
    
    db.session.add(response)
    db.session.commit()
    
    return jsonify(response.to_dict()), 201

@bp.route('/questionnaire/<int:questionnaire_id>', methods=['GET'])
@login_required
def get_questionnaire_responses(questionnaire_id):
    """Get all responses for a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    
    # Only allow questionnaire creator to view all responses
    if questionnaire.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    responses = Response.query.filter_by(questionnaire_id=questionnaire_id).all()
    return jsonify([r.to_dict() for r in responses])

@bp.route('/<int:response_id>', methods=['GET'])
@login_required
def get_response(response_id):
    """Get a specific response"""
    response = Response.query.get_or_404(response_id)
    
    # Allow access only to response owner or questionnaire creator
    if response.user_id != current_user.id and response.questionnaire.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(response.to_dict())

@bp.route('/questionnaire/<int:questionnaire_id>/analytics', methods=['GET'])
@login_required
def get_response_analytics(questionnaire_id):
    """Get analytics for questionnaire responses"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    
    # Only allow questionnaire creator to view analytics
    if questionnaire.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = Response.get_analytics(questionnaire_id)
    return jsonify(analytics)

@bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_responses(user_id):
    """Get all responses by a user"""
    # Only allow users to view their own responses
    if user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    responses = Response.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in responses])
