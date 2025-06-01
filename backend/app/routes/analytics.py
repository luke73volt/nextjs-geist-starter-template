from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
from app.models.questionnaire import Questionnaire
from app.models.response import Response

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/questionnaire/<int:questionnaire_id>/summary', methods=['GET'])
def get_summary_statistics(questionnaire_id):
    """Get comprehensive summary statistics for a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    
    responses = Response.query.filter_by(questionnaire_id=questionnaire_id).all()
    
    if not responses:
        return jsonify({
            'message': 'No responses available',
            'data': None
        })
    
    # Convert responses to pandas DataFrame for analysis
    response_data = []
    for response in responses:
        answers = response.get_answers()
        row = {
            'response_id': response.id,
            'user_id': response.user_id,
            'completion_time': response.completion_time,
            'submitted_at': response.submitted_at,
            **answers  # Unpack answers as columns
        }
        response_data.append(row)
    
    df = pd.DataFrame(response_data)
    
    # Calculate summary statistics
    summary = {
        'response_metrics': {
            'total_responses': len(responses),
            'average_completion_time': df['completion_time'].mean(),
            'completion_time_std': df['completion_time'].std(),
            'response_rate_over_time': _calculate_response_rate(df)
        },
        'question_analysis': _analyze_questions(questionnaire, df),
        'correlation_analysis': _analyze_correlations(df)
    }
    
    return jsonify(summary)

@bp.route('/questionnaire/<int:questionnaire_id>/export', methods=['GET'])
def export_analytics(questionnaire_id):
    """Export questionnaire data in various formats"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    
    format_type = request.args.get('format', 'json')
    responses = Response.query.filter_by(questionnaire_id=questionnaire_id).all()
    
    if not responses:
        return jsonify({
            'message': 'No data to export',
            'data': None
        })
    
    # Prepare data
    export_data = []
    for response in responses:
        answers = response.get_answers()
        row = {
            'response_id': response.id,
            'user_id': response.user_id,
            'completion_time': response.completion_time,
            'submitted_at': response.submitted_at.isoformat() if response.submitted_at else None,
            'answers': answers
        }
        export_data.append(row)
    
    if format_type == 'json':
        return jsonify(export_data)
    else:
        return jsonify({'error': 'Unsupported format'}), 400

def _calculate_response_rate(df):
    """Calculate response rate over time"""
    if 'submitted_at' not in df.columns or df.empty:
        return []
    
    # Group by date and count responses
    df['date'] = pd.to_datetime(df['submitted_at']).dt.date
    daily_responses = df.groupby('date').size().reset_index()
    daily_responses.columns = ['date', 'count']
    
    return daily_responses.to_dict('records')

def _analyze_questions(questionnaire, df):
    """Analyze individual questions"""
    questions = questionnaire.get_questions()
    analysis = {}
    
    for idx, question in enumerate(questions):
        q_id = str(idx)
        if q_id in df.columns:
            responses = df[q_id].value_counts()
            
            analysis[q_id] = {
                'question_text': question['text'],
                'type': question['type'],
                'response_distribution': responses.to_dict(),
                'response_count': len(responses),
                'unique_answers': len(responses.unique())
            }
            
            # Additional analysis for multiple choice questions
            if question['type'] == 'multiple_choice':
                analysis[q_id]['most_common'] = responses.index[0] if not responses.empty else None
                analysis[q_id]['least_common'] = responses.index[-1] if not responses.empty else None
    
    return analysis

def _analyze_correlations(df):
    """Analyze correlations between questions"""
    # Remove non-numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        return {}
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Convert to dictionary format and handle NaN values
    correlations = {}
    for col1 in corr_matrix.columns:
        correlations[col1] = {}
        for col2 in corr_matrix.columns:
            if col1 != col2:
                value = corr_matrix.loc[col1, col2]
                correlations[col1][col2] = None if pd.isna(value) else float(value)
    
    return correlations
