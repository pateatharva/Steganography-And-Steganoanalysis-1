from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_models import db, ProcessingHistory, Favorite, UserPreference, ApiKey, User
from datetime import datetime
import secrets
import os

print("[API.PY] Loading JWT-based API routes", flush=True)

api = Blueprint('api', __name__)

def get_upload_dir():
    from flask import current_app
    return os.path.join(os.path.dirname(current_app.root_path), 'instance', 'uploads')

@api.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid user identity'}), 401
    history = ProcessingHistory.query.filter_by(user_id=user_id_int).order_by(ProcessingHistory.timestamp.desc()).all()
    return jsonify([
        {
            'id': h.id,
            'operation_type': h.operation_type,
            'image_path': h.image_path,
            'message_length': h.message_length,
            'success': h.success,
            'timestamp': h.timestamp.isoformat()
        } for h in history
    ])

@api.route('/history/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    user_id = get_jwt_identity()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid user identity'}), 401
    h = ProcessingHistory.query.filter_by(id=history_id, user_id=user_id_int).first()
    if not h:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(h)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

@api.route('/favorites', methods=['GET', 'POST'])
@jwt_required()
def manage_favorites():
    user_id = get_jwt_identity()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid user identity'}), 401
    if request.method == 'GET':
        favorites = Favorite.query.filter_by(user_id=user_id_int).all()
        return jsonify([{'id': f.id, 'image_path': f.image_path, 'message': f.message, 'created_at': f.created_at.isoformat()} for f in favorites])
    data = request.get_json() or {}
    favorite = Favorite(user_id=user_id_int, image_path=data.get('image_path'), message=data.get('message', ''))
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'id': favorite.id, 'message': 'Favorite added'}), 201

@api.route('/preferences', methods=['GET', 'PUT'])
@jwt_required()
def manage_preferences():
    user_id = get_jwt_identity()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid user identity'}), 401
    pref = UserPreference.query.filter_by(user_id=user_id_int).first()
    if request.method == 'GET':
        if not pref:
            return jsonify({'theme': 'light', 'notifications': True})
        return jsonify({'theme': pref.theme, 'notifications': pref.notifications})
    data = request.get_json() or {}
    if not pref:
        pref = UserPreference(user_id=user_id_int)
        db.session.add(pref)
    if 'theme' in data:
        pref.theme = data['theme']
    if 'notifications' in data:
        pref.notifications = data['notifications']
    db.session.commit()
    return jsonify({'message': 'Preferences updated'})

@api.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid user identity'}), 401
    history = ProcessingHistory.query.filter_by(user_id=user_id_int).all()
    total_operations = len(history)
    successful = sum(1 for h in history if h.success)
    success_rate = (successful / total_operations * 100) if total_operations > 0 else 0
    return jsonify({'totalOperations': total_operations, 'successfulOperations': successful, 'successRate': round(success_rate, 2), 'recentOperations': [{'id': h.id, 'operation_type': h.operation_type, 'success': h.success, 'timestamp': h.timestamp.isoformat()} for h in sorted(history, key=lambda x: x.timestamp, reverse=True)[:5]]})
