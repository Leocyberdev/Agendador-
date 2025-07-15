from flask import Blueprint, jsonify, request, session
from src.models.user import User, db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username e senha são obrigatórios'}), 400

    user = User.query.filter_by(username=username, is_active=True).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user = User.query.get(session['user_id'])
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'error': 'Usuário não encontrado'}), 404

@auth_bp.route('/create-user', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if not username or not email or not password:
        return jsonify({'error': 'Username, email e senha são obrigatórios'}), 400

    # Verificar se usuário já existe
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username já existe'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já existe'}), 400

    # Criar novo usuário
    user = User(username=username, email=email, is_admin=is_admin)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Usuário criado com sucesso',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Não permitir deletar o próprio usuário admin
    if user.id == session['user_id']:
        return jsonify({'error': 'Não é possível deletar seu próprio usuário'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200

@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Não permitir desativar o próprio usuário admin
    if user.id == session['user_id']:
        return jsonify({'error': 'Não é possível alterar o status do seu próprio usuário'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'ativado' if user.is_active else 'desativado'
    return jsonify({
        'message': f'Usuário {status} com sucesso',
        'user': user.to_dict()
    }), 200

