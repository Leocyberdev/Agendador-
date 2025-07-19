from dotenv import load_dotenv
load_dotenv()
import os
import sys
from sqlalchemy.exc import SQLAlchemyError  # Importação adicionada

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.email_service import email_service
from flask import Flask, send_from_directory, jsonify  # jsonify adicionado
from flask_cors import CORS
from src.models.user import User
from src.models.user import db, User
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.reunioes import reunioes_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'agendador-reunioes-secret-key-2025'

# Configurar CORS para permitir requisições do frontend
CORS(app, supports_credentials=True)

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
print(f"DEBUG: SQLALCHEMY_DATABASE_URI = {os.environ.get('SQLALCHEMY_DATABASE_URI')}")

# Configurações avançadas do pool de conexões (CRÍTICO)
app.config.update(
    SQLALCHEMY_ENGINE_OPTIONS={
        "pool_pre_ping": True,       # Verifica conexões antes de usar
        "pool_recycle": 300,         # Recicla conexões a cada 5 minutos
        "pool_size": 10,             # Conexões mantidas permanentemente
        "max_overflow": 20,          # Conexões extras durante picos
        "pool_timeout": 30,          # 30 segundos de timeout
        "isolation_level": "READ COMMITTED"  # Nível de isolamento
    }
)

db.init_app(app)

# Middleware global para gerenciamento de sessões do banco
@app.after_request
def session_management(response):
    try:
        # Rollback se houve erro (status 4xx/5xx)
        if 400 <= response.status_code < 600:
            db.session.rollback()
        else:
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Erro de banco após request: {str(e)}")
    finally:
        # Sempre fecha a sessão para evitar vazamentos
        db.session.close()
    return response

def create_admin_user():
    """Criar usuário administrador padrão com tratamento de erros"""
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='agendamontereletrica@gmail.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Usuário administrador criado:")
            print("Username: admin")
            print("Senha: admin123")
    except SQLAlchemyError as e:
        print(f"ERRO ao criar admin: {str(e)}")
        db.session.rollback()

# Middleware para monitorar conexões (opcional)
@app.before_request
def log_session():
    app.logger.debug(f"Sessões ativas: {db.session.registry.size()}")

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(reunioes_bp, url_prefix='/api')

with app.app_context():
    try:
        db.create_all()
        create_admin_user()
    except SQLAlchemyError as e:
        print(f"ERRO FATAL ao iniciar banco: {str(e)}")
        # Tentar reiniciar conexão
        db.session.rollback()
        db.engine.dispose()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({"erro": "Configuração de arquivos estáticos ausente"}), 500

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        return jsonify({"erro": "Arquivo não encontrado"}), 404

# Rota de health check para monitoramento
@app.route('/health')
def health_check():
    try:
        # Teste simples de conexão com o banco
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "ok"}), 200
    except SQLAlchemyError:
        return jsonify({"status": "unhealthy", "database": "fail"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
