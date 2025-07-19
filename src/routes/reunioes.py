from flask import Blueprint, jsonify, request, session
from src.models.user import User, Reuniao, db
from src.routes.auth import login_required
from datetime import datetime, date, time
from src.email_service import email_service
from sqlalchemy import or_, and_



reunioes_bp = Blueprint('reunioes', __name__)

@reunioes_bp.route('/reunioes', methods=['GET'])
@login_required
def get_reunioes():
    reunioes = Reuniao.query.order_by(Reuniao.data.asc(), Reuniao.hora_inicio.asc()).all()
    return jsonify([reuniao.to_dict() for reuniao in reunioes]), 200

@reunioes_bp.route('/reunioes', methods=['POST'])
@login_required
def create_reuniao():
    data = request.json
    titulo = data.get("titulo")
    data_str = data.get("data")
    hora_inicio_str = data.get("hora_inicio")
    hora_termino_str = data.get("hora_termino")
    local = data.get("local", "")
    participantes = data.get("participantes", "")
    descricao = data.get("descricao", "")

    if not titulo or not data_str or not hora_inicio_str or not hora_termino_str:
        return jsonify({"error": "Título, data, hora de início e hora de término são obrigatórios"}), 400

    try:
        # Converter strings para objetos date e time
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        hora_inicio_obj = datetime.strptime(hora_inicio_str, "%H:%M").time()
        hora_termino_obj = datetime.strptime(hora_termino_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Formato de data ou hora inválido"}), 400

    # Validar se hora de início é anterior à hora de término
    if hora_inicio_obj >= hora_termino_obj:
        return jsonify({"error": "A hora de início deve ser anterior à hora de término"}), 400

    # CORREÇÃO: Verificar conflito de horário com lógica simplificada e correta
    # Duas reuniões se sobrepõem se:
    # - O início da nova reunião é antes do fim da existente E
    # - O fim da nova reunião é depois do início da existente
    conflito = Reuniao.query.filter(
        Reuniao.data == data_obj,
        Reuniao.hora_inicio < hora_termino_obj,
        Reuniao.hora_termino > hora_inicio_obj
    ).first()

    if conflito:
        return jsonify({
            "error": "Horário indisponível. Já existe uma reunião marcada nesse horário.",
            "reuniao_conflitante": conflito.to_dict()
        }), 409

    # Criar nova reunião
    reuniao = Reuniao(
        titulo=titulo,
        data=data_obj,
        hora_inicio=hora_inicio_obj,
        hora_termino=hora_termino_obj,
        local=local,
        participantes=participantes,
        descricao=descricao,
        created_by=session["user_id"]
    )
    
    db.session.add(reuniao)
    db.session.commit()
    
    email_service.send_meeting_notification_to_all({
        "titulo": titulo,
        "data": data_str,
        "hora_inicio": hora_inicio_str,
        "hora_termino": hora_termino_str,
        "local": local,
        "participantes": participantes,
        "descricao": descricao
    })

    return jsonify({
        "message": "Reunião criada com sucesso",
        "reuniao": reuniao.to_dict()
    }), 201

@reunioes_bp.route("/reunioes/<int:reuniao_id>", methods=["GET"])
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
    hora_inicio_str = data.get('hora_inicio')
    hora_termino_str = data.get('hora_termino')

    # Preparar novos valores (usar valores atuais se não fornecidos)
    nova_data = reuniao.data
    nova_hora_inicio = reuniao.hora_inicio
    nova_hora_termino = reuniao.hora_termino

    if titulo:
        reuniao.titulo = titulo
    
    if data_str:
        try:
            nova_data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
    
    if hora_inicio_str:
        try:
            nova_hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Formato de hora de início inválido'}), 400

    if hora_termino_str:
        try:
            nova_hora_termino = datetime.strptime(hora_termino_str, '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Formato de hora de término inválido'}), 400

    # Validar se hora de início é anterior à hora de término
    if nova_hora_inicio >= nova_hora_termino:
        return jsonify({"error": "A hora de início deve ser anterior à hora de término"}), 400

    # CORREÇÃO: Verificar conflito de horário na atualização (excluindo a própria reunião)
    conflito = Reuniao.query.filter(
        Reuniao.id != reuniao_id,  # Excluir a própria reunião da verificação
        Reuniao.data == nova_data,
        Reuniao.hora_inicio < nova_hora_termino,
        Reuniao.hora_termino > nova_hora_inicio
    ).first()

    if conflito:
        return jsonify({
            "error": "Horário indisponível. Já existe uma reunião marcada nesse horário.",
            "reuniao_conflitante": conflito.to_dict()
        }), 409

    # Aplicar as alterações
    reuniao.data = nova_data
    reuniao.hora_inicio = nova_hora_inicio
    reuniao.hora_termino = nova_hora_termino
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
    reunioes = Reuniao.query.filter_by(created_by=session['user_id']).order_by(Reuniao.data.asc(), Reuniao.hora_inicio.asc()).all()
    return jsonify([reuniao.to_dict() for reuniao in reunioes]), 200
