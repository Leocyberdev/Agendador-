from flask import Blueprint, jsonify, request, session
from src.models.user import User, Reuniao, db
from src.routes.auth import login_required
from datetime import datetime

reunioes_bp = Blueprint('reunioes', __name__)

@reunioes_bp.route('/reunioes', methods=['GET'])
@login_required
def get_reunioes():
    reunioes = Reuniao.query.order_by(Reuniao.data.asc(), Reuniao.hora.asc()).all()
    return jsonify([reuniao.to_dict() for reuniao in reunioes]), 200

@reunioes_bp.route('/reunioes', methods=['POST'])
@login_required
def create_reuniao():
    data = request.json
    titulo = data.get('titulo')
    data_str = data.get('data')
    hora_str = data.get('hora')
    local = data.get('local', '')
    participantes = data.get('participantes', '')
    descricao = data.get('descricao', '')

    if not titulo or not data_str or not hora_str:
        return jsonify({'error': 'Título, data e hora são obrigatórios'}), 400

    try:
        # Converter strings para objetos date e time
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Formato de data ou hora inválido'}), 400

    # Criar nova reunião
    reuniao = Reuniao(
        titulo=titulo,
        data=data_obj,
        hora=hora_obj,
        local=local,
        participantes=participantes,
        descricao=descricao,
        created_by=session['user_id']
    )
    
    db.session.add(reuniao)
    db.session.commit()

    return jsonify({
        'message': 'Reunião criada com sucesso',
        'reuniao': reuniao.to_dict()
    }), 201

@reunioes_bp.route('/reunioes/<int:reuniao_id>', methods=['GET'])
@login_required
def get_reuniao(reuniao_id):
    reuniao = Reuniao.query.get_or_404(reuniao_id)
    return jsonify(reuniao.to_dict()), 200

@reunioes_bp.route('/reunioes/<int:reuniao_id>', methods=['PUT'])
@login_required
def update_reuniao(reuniao_id):
    reuniao = Reuniao.query.get_or_404(reuniao_id)
    
    # Verificar se o usuário é o criador da reunião ou é admin
    user = User.query.get(session['user_id'])
    if reuniao.created_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Você só pode editar suas próprias reuniões'}), 403

    data = request.json
    titulo = data.get('titulo')
    data_str = data.get('data')
    hora_str = data.get('hora')

    if titulo:
        reuniao.titulo = titulo
    
    if data_str:
        try:
            reuniao.data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
    
    if hora_str:
        try:
            reuniao.hora = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Formato de hora inválido'}), 400

    reuniao.local = data.get('local', reuniao.local)
    reuniao.participantes = data.get('participantes', reuniao.participantes)
    reuniao.descricao = data.get('descricao', reuniao.descricao)
    
    db.session.commit()

    return jsonify({
        'message': 'Reunião atualizada com sucesso',
        'reuniao': reuniao.to_dict()
    }), 200

@reunioes_bp.route('/reunioes/<int:reuniao_id>', methods=['DELETE'])
@login_required
def delete_reuniao(reuniao_id):
    reuniao = Reuniao.query.get_or_404(reuniao_id)
    
    # Verificar se o usuário é o criador da reunião ou é admin
    user = User.query.get(session['user_id'])
    if reuniao.created_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Você só pode deletar suas próprias reuniões'}), 403
    
    db.session.delete(reuniao)
    db.session.commit()
    
    return jsonify({'message': 'Reunião deletada com sucesso'}), 200

@reunioes_bp.route('/minhas-reunioes', methods=['GET'])
@login_required
def get_minhas_reunioes():
    reunioes = Reuniao.query.filter_by(created_by=session['user_id']).order_by(Reuniao.data.asc(), Reuniao.hora.asc()).all()
    return jsonify([reuniao.to_dict() for reuniao in reunioes]), 200

