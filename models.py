from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100))
    role = db.Column(db.String(20), default='operador')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Regional(db.Model):
    __tablename__ = 'regionais'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    bscs = db.relationship('BSC', backref='regional', lazy=True)

class BSC(db.Model):
    __tablename__ = 'bscs'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), nullable=False)
    municipio = db.Column(db.String(100))
    regional_id = db.Column(db.Integer, db.ForeignKey('regionais.id'), nullable=False)
    equipes = db.relationship('Equipe', backref='bsc', lazy=True)

class Equipe(db.Model):
    __tablename__ = 'equipes'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=False)
    bsc_id = db.Column(db.Integer, db.ForeignKey('bscs.id'), nullable=False)
    status = db.Column(db.String(20), default='DISPONIVEL')  # DISPONIVEL, EM_CAMPO, EM_PAUSA, INDISPONIVEL
    especialidade = db.Column(db.String(20), default='MISTA')  # COMERCIAL, EMERGENCIAL, MISTA
    n_tecnicos = db.Column(db.Integer, default=2)
    veiculo = db.Column(db.String(20))
    ativa = db.Column(db.Boolean, default=True)
    comerciais = db.relationship('ServicoComercial', backref='equipe', lazy=True)
    emergenciais = db.relationship('ServicoEmergencial', backref='equipe', lazy=True)

class ServicoComercial(db.Model):
    __tablename__ = 'servicos_comerciais'
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), unique=True, nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, EM_ATENDIMENTO, CONCLUIDO, CANCELADO
    prioridade = db.Column(db.Integer, default=1)  # 1=Normal 2=Alta 3=Urgente
    endereco = db.Column(db.String(200))
    cliente = db.Column(db.String(100))
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=True)
    data = db.Column(db.Date, default=date.today)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def prioridade_label(self):
        return {1: 'Normal', 2: 'Alta', 3: 'Urgente'}.get(self.prioridade, 'Normal')

    @property
    def prioridade_class(self):
        return {1: 'normal', 2: 'alta', 3: 'urgente'}.get(self.prioridade, 'normal')

class ServicoEmergencial(db.Model):
    __tablename__ = 'servicos_emergenciais'
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), unique=True, nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='ABERTO')  # ABERTO, EM_ATENDIMENTO, CONCLUIDO
    prioridade = db.Column(db.Integer, default=1)  # 1=Baixa 2=Média 3=Crítica
    endereco = db.Column(db.String(200))
    n_clientes_afetados = db.Column(db.Integer, default=0)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=True)
    data = db.Column(db.Date, default=date.today)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def prioridade_label(self):
        return {1: 'Baixa', 2: 'Média', 3: 'Crítica'}.get(self.prioridade, 'Baixa')

    @property
    def prioridade_class(self):
        return {1: 'baixa', 2: 'media', 3: 'critica'}.get(self.prioridade, 'baixa')
