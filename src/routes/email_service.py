import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Configurações SMTP do Gmail
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587  # TLS
        self.email_user = os.environ.get('EMAIL_USER', 'agendamontereletrica@gmail.com')
        self.email_password = os.environ.get('EMAIL_PASSWORD', 'Agendamonter30')
        
    def send_email(self, to_email, subject, body, is_html=False):
        """
        Envia um e-mail usando as configurações SMTP do Gmail
        
        Args:
            to_email (str): E-mail do destinatário
            subject (str): Assunto do e-mail
            body (str): Corpo do e-mail
            is_html (bool): Se o corpo é HTML ou texto simples
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar corpo da mensagem
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Habilitar TLS
            server.login(self.email_user, self.email_password)
            
            # Enviar e-mail
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            logger.info(f"E-mail enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {to_email}: {str(e)}")
            return False
    
    def send_meeting_notification(self, user_email, meeting_data):
        """
        Envia notificação de nova reunião agendada
        
        Args:
            user_email (str): E-mail do usuário
            meeting_data (dict): Dados da reunião
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        subject = f"Nova Reunião Agendada: {meeting_data.get('titulo', 'Sem título')}"
        
        # Formatear data e hora
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
    
    def send_meeting_reminder(self, user_email, meeting_data):
        """
        Envia lembrete de reunião
        
        Args:
            user_email (str): E-mail do usuário
            meeting_data (dict): Dados da reunião
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        subject = f"Lembrete: Reunião {meeting_data.get('titulo', 'Sem título')} hoje"
        
        # Formatear data e hora
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
        """
        Envia notificação de cancelamento de reunião
        
        Args:
            user_email (str): E-mail do usuário
            meeting_data (dict): Dados da reunião
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        subject = f"Reunião Cancelada: {meeting_data.get('titulo', 'Sem título')}"
        
        # Formatear data e hora
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

