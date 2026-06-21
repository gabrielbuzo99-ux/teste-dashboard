# Copel Despacho — Sistema de Despacho de Equipes de Campo

## Descrição

Sistema web de despacho e acompanhamento de equipes de campo da Copel, desenvolvido em Flask com banco de dados SQLite.

## Estrutura

- 5 Regionais (Curitiba, Norte, Oeste, Sul, Leste)
- 40 BSCs (8 por regional)
- ~700 equipes de campo
- Geração automática de ~1500 serviços comerciais e ~500 emergenciais diários

## Páginas

| Rota             | Descrição                              |
|-----------------|----------------------------------------|
| `/login`        | Autenticação de usuário                |
| `/home`         | Painel geral com KPIs e resumo         |
| `/comerciais`   | Acompanhamento de serviços comerciais  |
| `/emergenciais` | Acompanhamento de emergências          |
| `/equipes`      | Status das equipes de campo            |

## Instalação

```bash
# 1. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie a aplicação (o banco é criado e populado automaticamente)
python app.py
```

Acesse em: **http://localhost:5000**

## Credenciais de Acesso


## Tecnologias

- Python 3.10+
- Flask 3.x
- Flask-SQLAlchemy
- SQLite3
- HTML5 / CSS3 / JavaScript (Vanilla)
- Design escuro com tema operacional
