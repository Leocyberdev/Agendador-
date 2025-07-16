import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agendador-reunioes-secret-key-2025'
    
    # Configuração do banco de dados com fallback
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    # Correção para PostgreSQL no Render
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Fallback para SQLite em desenvolvimento se não houver DATABASE_URL
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///agendador.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações adicionais para PostgreSQL
    if database_url and 'postgresql://' in database_url:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

