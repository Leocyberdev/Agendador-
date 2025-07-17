from src.database import db
from datetime import datetime

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False) # Nova coluna
    hora_termino = db.Column(db.Time, nullable=False) # Nova coluna
    local = db.Column(db.String(120), nullable=False)
    participantes = db.Column(db.String(500), nullable=False)
    descricao = db.Column(db.String(1000), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "data": self.data.isoformat(),
            "hora_inicio": self.hora_inicio.isoformat(), # Ajustado
            "hora_termino": self.hora_termino.isoformat(), # Ajustado
            "local": self.local,
            "participantes": self.participantes,
            "descricao": self.descricao,
            "created_by": self.created_by
        }

    def __repr__(self):
        return f"<Meeting {self.titulo}>"
        
