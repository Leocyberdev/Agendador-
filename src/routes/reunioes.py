from flask import Blueprint, jsonify, request, session
from src.models.user import User, Meeting, db # Alterado de Reuniao para Meeting
from src.routes.auth import login_required
from datetime import datetime, date, time # Adicionado 'time'
from src.email_service import EmailService # Alterado para EmailService
import threading # Adicionado para envio de email em thread

reunioes_bp = Blueprint("reunioes", __name__)
email_service = EmailService()

from datetime import datetime, date, time # Certifique-se de importar time

# ...

@reunioes_bp.route('/reunioes', methods=['POST'])
@login_required
def create_reuniao():
    data = request.json
    titulo = data.get('titulo')
    data_reuniao_str = data.get('data')
    hora_inicio_str = data.get('hora_inicio')
    hora_termino_str = data.get('hora_termino')
    local = data.get('local')
    participantes = data.get('participantes')
    descricao = data.get('descricao')
    criado_por = session.get('user_id')

    if not all([titulo, data_reuniao_str, hora_inicio_str, hora_termino_str, local, participantes, descricao, criado_por]):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

    # Converter strings de data e hora para objetos date e time
    try:
        data_reuniao = datetime.strptime(data_reuniao_str, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_termino = datetime.strptime(hora_termino_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Formato de data ou hora inválido. Use YYYY-MM-DD para data e HH:MM para hora.'}), 400

    new_reuniao = Meeting(
        titulo=titulo,
        data=data_reuniao,
        hora_inicio=hora_inicio, # Novo campo
        hora_termino=hora_termino, # Novo campo
        local=local,
        participantes=participantes,
        descricao=descricao,
        created_by=criado_por
    )
    db.session.add(new_reuniao)
    db.session.commit()
    return jsonify(new_reuniao.to_dict()), 201

    # Enviar notificação por e-mail em uma thread separada
    if participantes_str:
        participantes_emails = [p.strip() for p in participantes_str.split(",") if "@" in p]
        meeting_data = {
            "titulo": titulo,
            "descricao": descricao,
            "data": data_reuniao.strftime("%d/%m/%Y"),
            "hora_inicio": hora_inicio.strftime("%H:%M"),
            "hora_termino": hora_termino.strftime("%H:%M"),
            "local": local,
            "participantes": participantes_emails
        }
        for email in participantes_emails:
            threading.Thread(target=email_service.send_meeting_notification, args=(email, meeting_data)).start()

    return jsonify({"message": "Reunião agendada com sucesso!"}), 201

@reunioes_bp.route("/reunioes/<int:reuniao_id>", methods=["GET"])
@login_required
def get_reuniao(reuniao_id):
    reuniao = Meeting.query.get_or_404(reuniao_id)
    return jsonify(reuniao_to_dict(reuniao)), 200

@reunioes_bp.route("/reunioes/<int:reuniao_id>", methods=["PUT"])
@login_required
def update_reuniao(reuniao_id):
    data = request.json
    reuniao = Meeting.query.get_or_404(reuniao_id)

    if reuniao.created_by != session.get("user_id"):
        return jsonify({"error": "Você não tem permissão para editar esta reunião"}), 403

    reuniao.title = data.get("titulo", reuniao.title)
    reuniao.description = data.get("descricao", reuniao.description)
    
    data_reuniao_str = data.get("data")
    if data_reuniao_str:
        try:
            reuniao.date = datetime.strptime(data_reuniao_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    hora_inicio_str = data.get("hora_inicio")
    if hora_inicio_str:
        try:
            reuniao.start_time = datetime.strptime(hora_inicio_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Formato de hora de início inválido. Use HH:MM."}), 400

    hora_termino_str = data.get("hora_termino")
    if hora_termino_str:
        try:
            reuniao.end_time = datetime.strptime(hora_termino_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Formato de hora de término inválido. Use HH:MM."}), 400

    reuniao.location = data.get("local", reuniao.location)
    reuniao.participants = data.get("participantes", reuniao.participants)

    db.session.commit()
    return jsonify({"message": "Reunião atualizada com sucesso!"}), 200

@reunioes_bp.route("/reunioes/<int:reuniao_id>", methods=["DELETE"])
@login_required
def delete_reuniao(reuniao_id):
    reuniao = Meeting.query.get_or_404(reuniao_id)

    if reuniao.created_by != session.get("user_id"):
        return jsonify({"error": "Você não tem permissão para excluir esta reunião"}), 403

    db.session.delete(reuniao)
    db.session.commit()
    return jsonify({"message": "Reunião excluída com sucesso!"}), 200

@reunioes_bp.route("/minhas-reunioes", methods=["GET"])
@login_required
def get_minhas_reunioes():
    reunioes = Meeting.query.filter_by(created_by=session.get("user_id")).order_by(Meeting.date.asc(), Meeting.start_time.asc()).all()
    return jsonify([reuniao_to_dict(reuniao) for reuniao in reunioes]), 200

def reuniao_to_dict(reuniao):
    return {
        "id": reuniao.id,
        "titulo": reuniao.title,
        "descricao": reuniao.description,
        "data": reuniao.date.strftime("%Y-%m-%d"),
        "hora_inicio": reuniao.start_time.strftime("%H:%M"),
        "hora_termino": reuniao.end_time.strftime("%H:%M"),
        "local": reuniao.location,
        "participantes": reuniao.participants.split(",") if reuniao.participants else [],
        "criado_por": User.query.get(reuniao.created_by).username if User.query.get(reuniao.created_by) else "Desconhecido",
        "criado_em": reuniao.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }


