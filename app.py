from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from database import db, init_db
from models import User, Regional, BSC, Equipe, ServicoComercial, ServicoEmergencial
from datetime import datetime, date
import random

app = Flask(__name__)
app.secret_key = 'copel-despacho-2026-secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///copel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('home'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    hoje = date.today()
    total_comerciais = ServicoComercial.query.filter_by(data=hoje).count()
    total_emergenciais = ServicoEmergencial.query.filter_by(data=hoje).count()
    total_equipes = Equipe.query.filter_by(ativa=True).count()
    equipes_campo = Equipe.query.filter_by(status='EM_CAMPO', ativa=True).count()
    comerciais_pendentes = ServicoComercial.query.filter_by(data=hoje, status='PENDENTE').count()
    comerciais_concluidos = ServicoComercial.query.filter_by(data=hoje, status='CONCLUIDO').count()
    emergenciais_abertos = ServicoEmergencial.query.filter_by(data=hoje, status='ABERTO').count()
    emergenciais_concluidos = ServicoEmergencial.query.filter_by(data=hoje, status='CONCLUIDO').count()
    regionais = Regional.query.all()
    stats_regionais = []
    for r in regionais:
        bsc_ids = [b.id for b in r.bscs]
        eq_ids = [e.id for b in r.bscs for e in b.equipes]
        com = ServicoComercial.query.filter(ServicoComercial.data == hoje, ServicoComercial.equipe_id.in_(eq_ids)).count() if eq_ids else 0
        eme = ServicoEmergencial.query.filter(ServicoEmergencial.data == hoje, ServicoEmergencial.equipe_id.in_(eq_ids)).count() if eq_ids else 0
        stats_regionais.append({'nome': r.nome, 'comerciais': com, 'emergenciais': eme, 'equipes': len(eq_ids)})
    return render_template('home.html',
        total_comerciais=total_comerciais, total_emergenciais=total_emergenciais,
        total_equipes=total_equipes, equipes_campo=equipes_campo,
        comerciais_pendentes=comerciais_pendentes, comerciais_concluidos=comerciais_concluidos,
        emergenciais_abertos=emergenciais_abertos, emergenciais_concluidos=emergenciais_concluidos,
        stats_regionais=stats_regionais, hoje=hoje.strftime('%d/%m/%Y'))

@app.route('/comerciais')
@login_required
def comerciais():
    hoje = date.today()
    regional_id = request.args.get('regional_id', type=int)
    bsc_id = request.args.get('bsc_id', type=int)
    status_f = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    regionais = Regional.query.order_by(Regional.nome).all()
    bscs = BSC.query.order_by(BSC.nome).all()
    query = ServicoComercial.query.filter_by(data=hoje)
    if regional_id:
        bsc_ids_reg = [b.id for b in BSC.query.filter_by(regional_id=regional_id).all()]
        eq_ids_reg = [e.id for b in BSC.query.filter_by(regional_id=regional_id).all() for e in b.equipes]
        query = query.filter(ServicoComercial.equipe_id.in_(eq_ids_reg))
    if bsc_id:
        eq_ids_bsc = [e.id for e in Equipe.query.filter_by(bsc_id=bsc_id).all()]
        query = query.filter(ServicoComercial.equipe_id.in_(eq_ids_bsc))
    if status_f:
        query = query.filter_by(status=status_f)
    total = query.count()
    servicos = query.order_by(ServicoComercial.prioridade.desc(), ServicoComercial.criado_em.asc()).paginate(page=page, per_page=50, error_out=False)
    pendentes = ServicoComercial.query.filter_by(data=hoje, status='PENDENTE').count()
    em_atendimento = ServicoComercial.query.filter_by(data=hoje, status='EM_ATENDIMENTO').count()
    concluidos = ServicoComercial.query.filter_by(data=hoje, status='CONCLUIDO').count()
    return render_template('comerciais.html', servicos=servicos, regionais=regionais, bscs=bscs,
        regional_id=regional_id, bsc_id=bsc_id, status_f=status_f, total=total,
        pendentes=pendentes, em_atendimento=em_atendimento, concluidos=concluidos, hoje=hoje.strftime('%d/%m/%Y'))

@app.route('/equipes')
@login_required
def equipes():
    regional_id = request.args.get('regional_id', type=int)
    bsc_id = request.args.get('bsc_id', type=int)
    status_f = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    regionais = Regional.query.order_by(Regional.nome).all()
    bscs = BSC.query.order_by(BSC.nome).all()
    query = Equipe.query.filter_by(ativa=True)
    if regional_id:
        bsc_ids = [b.id for b in BSC.query.filter_by(regional_id=regional_id).all()]
        query = query.filter(Equipe.bsc_id.in_(bsc_ids))
    if bsc_id:
        query = query.filter_by(bsc_id=bsc_id)
    if status_f:
        query = query.filter_by(status=status_f)
    equipes_pg = query.order_by(Equipe.codigo).paginate(page=page, per_page=50, error_out=False)
    hoje = date.today()
    disponivel = Equipe.query.filter_by(status='DISPONIVEL', ativa=True).count()
    em_campo = Equipe.query.filter_by(status='EM_CAMPO', ativa=True).count()
    em_pausa = Equipe.query.filter_by(status='EM_PAUSA', ativa=True).count()
    indisponivel = Equipe.query.filter_by(status='INDISPONIVEL', ativa=True).count()
    return render_template('equipes.html', equipes=equipes_pg, regionais=regionais, bscs=bscs,
        regional_id=regional_id, bsc_id=bsc_id, status_f=status_f,
        disponivel=disponivel, em_campo=em_campo, em_pausa=em_pausa, indisponivel=indisponivel)

@app.route('/emergenciais')
@login_required
def emergenciais():
    hoje = date.today()
    regional_id = request.args.get('regional_id', type=int)
    bsc_id = request.args.get('bsc_id', type=int)
    status_f = request.args.get('status', '')
    prioridade_f = request.args.get('prioridade', '')
    page = request.args.get('page', 1, type=int)
    regionais = Regional.query.order_by(Regional.nome).all()
    bscs = BSC.query.order_by(BSC.nome).all()
    query = ServicoEmergencial.query.filter_by(data=hoje)
    if regional_id:
        eq_ids = [e.id for b in BSC.query.filter_by(regional_id=regional_id).all() for e in b.equipes]
        query = query.filter(ServicoEmergencial.equipe_id.in_(eq_ids))
    if bsc_id:
        eq_ids_bsc = [e.id for e in Equipe.query.filter_by(bsc_id=bsc_id).all()]
        query = query.filter(ServicoEmergencial.equipe_id.in_(eq_ids_bsc))
    if status_f:
        query = query.filter_by(status=status_f)
    if prioridade_f:
        query = query.filter_by(prioridade=int(prioridade_f))
    total = query.count()
    servicos = query.order_by(ServicoEmergencial.prioridade.desc(), ServicoEmergencial.criado_em.asc()).paginate(page=page, per_page=50, error_out=False)
    abertos = ServicoEmergencial.query.filter_by(data=hoje, status='ABERTO').count()
    em_atendimento = ServicoEmergencial.query.filter_by(data=hoje, status='EM_ATENDIMENTO').count()
    concluidos = ServicoEmergencial.query.filter_by(data=hoje, status='CONCLUIDO').count()
    criticos = ServicoEmergencial.query.filter_by(data=hoje, prioridade=3).count()
    return render_template('emergenciais.html', servicos=servicos, regionais=regionais, bscs=bscs,
        regional_id=regional_id, bsc_id=bsc_id, status_f=status_f, prioridade_f=prioridade_f,
        total=total, abertos=abertos, em_atendimento=em_atendimento, concluidos=concluidos,
        criticos=criticos, hoje=hoje.strftime('%d/%m/%Y'))

# API endpoints para atualização via AJAX
@app.route('/api/stats')
@login_required
def api_stats():
    hoje = date.today()
    return jsonify({
        'comerciais': {
            'total': ServicoComercial.query.filter_by(data=hoje).count(),
            'pendentes': ServicoComercial.query.filter_by(data=hoje, status='PENDENTE').count(),
            'em_atendimento': ServicoComercial.query.filter_by(data=hoje, status='EM_ATENDIMENTO').count(),
            'concluidos': ServicoComercial.query.filter_by(data=hoje, status='CONCLUIDO').count(),
        },
        'emergenciais': {
            'total': ServicoEmergencial.query.filter_by(data=hoje).count(),
            'abertos': ServicoEmergencial.query.filter_by(data=hoje, status='ABERTO').count(),
            'em_atendimento': ServicoEmergencial.query.filter_by(data=hoje, status='EM_ATENDIMENTO').count(),
            'concluidos': ServicoEmergencial.query.filter_by(data=hoje, status='CONCLUIDO').count(),
            'criticos': ServicoEmergencial.query.filter_by(data=hoje, prioridade=3).count(),
        },
        'equipes': {
            'total': Equipe.query.filter_by(ativa=True).count(),
            'disponivel': Equipe.query.filter_by(status='DISPONIVEL', ativa=True).count(),
            'em_campo': Equipe.query.filter_by(status='EM_CAMPO', ativa=True).count(),
            'em_pausa': Equipe.query.filter_by(status='EM_PAUSA', ativa=True).count(),
            'indisponivel': Equipe.query.filter_by(status='INDISPONIVEL', ativa=True).count(),
        }
    })

@app.route('/api/bscs/<int:regional_id>')
@login_required
def api_bscs(regional_id):
    bscs = BSC.query.filter_by(regional_id=regional_id).order_by(BSC.nome).all()
    return jsonify([{'id': b.id, 'nome': b.nome} for b in bscs])

@app.route('/efeitos-visuais')
@login_required
def efeitos_visuais():
    return render_template('efeitos_visuais.html')

@app.route('/efeitos-movimento')
@login_required
def efeitos_movimento():
    return render_template('efeitos_movimento.html')

@app.route('/efeitos-login')
@login_required
def efeitos_login():
    return render_template('efeitos_login.html')

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    app.run(debug=True, port=5000)
