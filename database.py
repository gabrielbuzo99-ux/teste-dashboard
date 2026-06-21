from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    from models import User, Regional, BSC, Equipe, ServicoComercial, ServicoEmergencial
    db.create_all()
    _seed(app)

def _seed(app):
    from models import User, Regional, BSC, Equipe, ServicoComercial, ServicoEmergencial
    from datetime import date
    import random

    if User.query.first():
        return  # já populado

    # Usuários
    admin = User(username='admin', role='admin', nome='Administrador')
    admin.set_password('admin123')
    op = User(username='operador', role='operador', nome='Operador Copel')
    op.set_password('copel2026')
    db.session.add_all([admin, op])

    # 5 Regionais com 8 BSCs cada = 40 BSCs
    regionais_data = [
        ('Regional Curitiba', 'CWB', ['CWB-01','CWB-02','CWB-03','CWB-04','CWB-05','CWB-06','CWB-07','CWB-08']),
        ('Regional Norte',    'NRT', ['NRT-01','NRT-02','NRT-03','NRT-04','NRT-05','NRT-06','NRT-07','NRT-08']),
        ('Regional Oeste',    'OES', ['OES-01','OES-02','OES-03','OES-04','OES-05','OES-06','OES-07','OES-08']),
        ('Regional Sul',      'SUL', ['SUL-01','SUL-02','SUL-03','SUL-04','SUL-05','SUL-06','SUL-07','SUL-08']),
        ('Regional Leste',    'LES', ['LES-01','LES-02','LES-03','LES-04','LES-05','LES-06','LES-07','LES-08']),
    ]

    tipos_comercial = [
        'Ligação Nova Monofásico', 'Ligação Nova Bifásico', 'Ligação Nova Trifásico',
        'Religação Normal', 'Religação de Urgência', 'Corte por Inadimplência',
        'Vistoria de Medidor', 'Troca de Medidor', 'Alteração de Carga',
        'Inspeção de Rede', 'Mudança de Padrão', 'Regularização de Ligação',
        'Serviço de Poda', 'Retirada de Equipamento', 'Atendimento Técnico'
    ]

    tipos_emergencial = [
        'Falta de Energia - Residencial', 'Falta de Energia - Comercial',
        'Poste Caído', 'Fio Partido na Via', 'Transformador em Chamas',
        'Rede em Contato com Vegetação', 'Curto-Circuito na Rede',
        'Falta de Energia - Hospital', 'Poste com Risco de Queda',
        'Rede Elétrica Danificada por Acidente', 'Explosão de Equipamento',
        'Afundamento de Tensão Crítico', 'Falta de Energia - Semáforo',
        'Descarga Atmosférica em Subestação', 'Vandalismo em Equipamentos'
    ]

    municipios_pr = {
        'CWB': ['Curitiba','São José dos Pinhais','Araucária','Colombo','Pinhais','Almirante Tamandaré','Campo Largo'],
        'NRT': ['Londrina','Maringá','Apucarana','Arapongas','Cambé','Rolândia','Cornélio Procópio'],
        'OES': ['Cascavel','Foz do Iguaçu','Toledo','Medianeira','Santa Helena','Matelândia','Missal'],
        'SUL': ['Ponta Grossa','Guarapuava','Irati','Palmeira','Castro','Telêmaco Borba','Lapa'],
        'LES': ['Paranaguá','Matinhos','Guaratuba','Morretes','Antonina','Pontal do Paraná','São Mateus do Sul'],
    }

    equipes_criadas = []
    hoje = date.today()

    for reg_nome, reg_sigla, bsc_codigos in regionais_data:
        regional = Regional(nome=reg_nome, sigla=reg_sigla)
        db.session.add(regional)
        db.session.flush()

        for i, bsc_cod in enumerate(bsc_codigos):
            municipio = municipios_pr[reg_sigla][i % len(municipios_pr[reg_sigla])]
            bsc = BSC(nome=f'BSC {bsc_cod}', codigo=bsc_cod, municipio=municipio, regional_id=regional.id)
            db.session.add(bsc)
            db.session.flush()

            # 17-18 equipes por BSC → ~700 total
            n_equipes = 17 if i < 6 else 18
            for j in range(1, n_equipes + 1):
                status = random.choices(
                    ['EM_CAMPO','DISPONIVEL','EM_PAUSA','INDISPONIVEL'],
                    weights=[55, 25, 12, 8]
                )[0]
                especialidade = random.choice(['COMERCIAL','EMERGENCIAL','MISTA'])
                eq = Equipe(
                    codigo=f'{bsc_cod}-EQ{j:02d}',
                    nome=f'Equipe {bsc_cod}-{j:02d}',
                    bsc_id=bsc.id,
                    status=status,
                    especialidade=especialidade,
                    n_tecnicos=random.randint(2, 4),
                    veiculo=f'PR-{random.randint(1000,9999)}',
                    ativa=True
                )
                db.session.add(eq)
                db.session.flush()
                equipes_criadas.append(eq)

    db.session.flush()

    # Serviços comerciais: ~1500
    for k in range(1500):
        eq = random.choice(equipes_criadas)
        hora = random.randint(6, 19)
        minuto = random.randint(0, 59)
        criado = datetime_from_today(hora, minuto)
        status = random.choices(
            ['PENDENTE','EM_ATENDIMENTO','CONCLUIDO','CANCELADO'],
            weights=[30, 25, 40, 5]
        )[0]
        sc = ServicoComercial(
            protocolo=f'COM{k+1:06d}',
            tipo=random.choice(tipos_comercial),
            status=status,
            prioridade=random.choices([1,2,3], weights=[60,30,10])[0],
            endereco=f'Rua {random.choice(["das Flores","Sete de Setembro","XV de Novembro","Marechal Deodoro"])}, {random.randint(10,2000)}',
            cliente=f'Cliente {random.randint(10000,99999)}',
            equipe_id=eq.id,
            data=hoje,
            criado_em=criado,
        )
        db.session.add(sc)

    # Serviços emergenciais: ~500
    for k in range(500):
        eq = random.choice(equipes_criadas)
        hora = random.randint(0, 23)
        minuto = random.randint(0, 59)
        criado = datetime_from_today(hora, minuto)
        status = random.choices(
            ['ABERTO','EM_ATENDIMENTO','CONCLUIDO'],
            weights=[25, 35, 40]
        )[0]
        se = ServicoEmergencial(
            protocolo=f'EME{k+1:06d}',
            tipo=random.choice(tipos_emergencial),
            status=status,
            prioridade=random.choices([1,2,3], weights=[40,35,25])[0],
            endereco=f'Av. {random.choice(["Brasil","Paraná","Iguaçu","das Araucárias"])}, {random.randint(10,5000)}',
            n_clientes_afetados=random.randint(1, 3000),
            equipe_id=eq.id,
            data=hoje,
            criado_em=criado,
        )
        db.session.add(se)

    db.session.commit()
    print("✅ Banco de dados populado com sucesso.")

def datetime_from_today(hora, minuto):
    from datetime import datetime, date
    d = date.today()
    return datetime(d.year, d.month, d.day, hora, minuto)
