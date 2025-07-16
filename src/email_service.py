import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from models import Usuario  # ajuste se o import for diferente
from app import db          # ajuste se você importar o db de outro lugar
import threading

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587  # TLS
        self.email_user = os.environ.get('EMAIL_USER', 'agendamontereletrica@gmail.com')
        self.email_password = os.environ.get('EMAIL_PASSWORD', 'Agendamonter30')

    def send_email(self, to_email, subject, body, is_html=False):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)

            server.sendmail(self.email_user, to_email, msg.as_string())
            server.quit()

            logger.info(f"E-mail enviado com sucesso para {to_email}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {to_email}: {str(e)}")
            return False

    def send_meeting_notification(self, user_email, meeting_data):
        subject = f"Nova Reunião Agendada: {meeting_data.get('titulo', 'Sem título')}"
        data_formatada = meeting_data.get('data', 'Data não informada')
        hora_formatada = meeting_data.get('hora', 'Hora não informada')

        body = f"""
Olá!

Uma nova reunião foi agendada no sistema:

📅 DETALHES DA REUNIÃO:
• Título: {meeting_data.get('titulo', 'Não informado')}
• Data: {data_formatada}
• Hora: {hora_formatada}
• Local: {meeting_data.get('local', 'Não informado')}
• Participantes: {meeting_data.get('participantes', 'Não informado')}

📝 DESCRIÇÃO:
{meeting_data.get('descricao', 'Nenhuma descrição fornecida')}

---
Este é um e-mail automático do Sistema Agendador de Reuniões.
Não responda a este e-mail.

Atenciosamente,
Sistema Agendador de Reuniões
        """

        return self.send_email(user_email, subject, body)

    def send_meeting_notification_to_all(self, meeting_data):
        # Pega todos os usuários
        usuarios = db.session.query(Usuario).all()
        subject = f"Nova Reunião Agendada: {meeting_data.get('titulo', 'Sem título')}"
        data_formatada = meeting_data.get('data', 'Data não informada')
        hora_formatada = meeting_data.get('hora', 'Hora não informada')

        body = f"""
Olá!

Uma nova reunião foi agendada no sistema:

📅 DETALHES DA REUNIÃO:
• Título: {meeting_data.get('titulo', 'Não informado')}
• Data: {data_formatada}
• Hora: {hora_formatada}
• Local: {meeting_data.get('local', 'Não informado')}
• Participantes: {meeting_data.get('participantes', 'Não informado')}

📝 DESCRIÇÃO:
{meeting_data.get('descricao', 'Nenhuma descrição fornecida')}

---
Este é um e-mail automático do Sistema Agendador de Reuniões.
Não responda a este e-mail.

Atenciosamente,
Sistema Agendador de Reuniões
        """

        def enviar():
            for usuario in usuarios:
                if usuario.email:
                    self.send_email(usuario.email, subject, body)

        # Envia em thread separada para não travar o app
        threading.Thread(target=enviar).start()

    def send_meeting_reminder(self, user_email, meeting_data):
        subject = f"Lembrete: Reunião {meeting_data.get('titulo', 'Sem título')} hoje"
        data_formatada = meeting_data.get('data', 'Data não informada')
        hora_formatada = meeting_data.get('hora', 'Hora não informada')

        body = f"""
Olá!

Este é um lembrete da sua reunião agendada para hoje:

📅 DETALHES DA REUNIÃO:
• Título: {meeting_data.get('titulo', 'Não informado')}
• Data: {data_formatada}
• Hora: {hora_formatada}
• Local: {meeting_data.get('local', 'Não informado')}
• Participantes: {meeting_data.get('participantes', 'Não informado')}

📝 DESCRIÇÃO:
{meeting_data.get('descricao', 'Nenhuma descrição fornecida')}

⏰ Não se esqueça da sua reunião!

---
Este é um e-mail automático do Sistema Agendador de Reuniões.
Não responda a este e-mail.

Atenciosamente,
Sistema Agendador de Reuniões
        """

        return self.send_email(user_email, subject, body)

    def send_meeting_cancellation(self, user_email, meeting_data):
        subject = f"Reunião Cancelada: {meeting_data.get('titulo', 'Sem título')}"
        data_formatada = meeting_data.get('data', 'Data não informada')
        hora_formatada = meeting_data.get('hora', 'Hora não informada')

        body = f"""
Olá!

A seguinte reunião foi cancelada:

📅 DETALHES DA REUNIÃO CANCELADA:
• Título: {meeting_data.get('titulo', 'Não informado')}
• Data: {data_formatada}
• Hora: {hora_formatada}
• Local: {meeting_data.get('local', 'Não informado')}
• Participantes: {meeting_data.get('participantes', 'Não informado')}

❌ Esta reunião foi removida do sistema.

---
Este é um e-mail automático do Sistema Agendador de Reuniões.
Não responda a este e-mail.

Atenciosamente,
Sistema Agendador de Reuniões
        """

        return self.send_email(user_email, subject, body)

# Instância global do serviço de e-mail
email_service = EmailService()
