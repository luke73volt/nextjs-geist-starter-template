from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.questionnaire import Questionnaire

bp = Blueprint('questionnaires', __name__, url_prefix='/api/questionnaires')

@bp.route('/', methods=['GET'])
@login_required
def get_questionnaires():
    """Get all questionnaires or filter by user"""
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        questionnaires = Questionnaire.query.filter_by(created_by=user_id).all()
    else:
        questionnaires = Questionnaire.query.all()
    
    return jsonify([q.to_dict() for q in questionnaires])

@bp.route('/', methods=['POST'])
@login_required
def create_questionnaire():
    """Create a new questionnaire"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'questions')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    questionnaire = Questionnaire(
        title=data['title'],
        description=data.get('description', ''),
        created_by=current_user.id
    )
    
    questionnaire.set_questions(data['questions'])
    
    if 'settings' in data:
        questionnaire.set_settings(data['settings'])
    
    db.session.add(questionnaire)
    db.session.commit()
    
    return jsonify(questionnaire.to_dict()), 201

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_questionnaire(id):
    """Get a specific questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    return jsonify(questionnaire.to_dict())

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_questionnaire(id):
    """Update a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        questionnaire.title = data['title']
    if 'description' in data:
        questionnaire.description = data['description']
    if 'questions' in data:
        questionnaire.set_questions(data['questions'])
    if 'settings' in data:
        questionnaire.set_settings(data['settings'])
    
    db.session.commit()
    
    return jsonify(questionnaire.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_questionnaire(id):
    """Delete a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(questionnaire)
    db.session.commit()
    
    return jsonify({'message': 'Questionnaire deleted successfully'})

@bp.route('/<int:id>/statistics', methods=['GET'])
@login_required
def get_questionnaire_statistics(id):
    """Get statistics for a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(questionnaire.get_statistics())
