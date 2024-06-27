"""
from fpdf import FPDF
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variável global para armazenar os dados do currículo
curriculo_data = {
    'dadosPessoais': {},
    'objetivoProfissional': {},
    'academica': [],
    'experiencia': [],
    'certificacoes': [],
    'idiomas': []
}

steps = [
    {'question': 'Qual é o seu email?', 'key': 'email'},
    {'question': 'Qual é o seu telefone?', 'key': 'telefone'},
    {'question': 'Qual é a sua cidade?', 'key': 'cidade'},
    {'question': 'Qual é a sua data de nascimento?', 'key': 'dataNascimento'},
    {'question': 'Descreva seu objetivo profissional.', 'key': 'descricao', 'section': 'objetivoProfissional'},
    {'question': 'Qual é o seu curso?', 'key': 'curso', 'section': 'academica', 'index': 0},
    {'question': 'Qual é a instituição de ensino?', 'key': 'instituicao', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o período do curso?', 'key': 'periodo', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o status atual do curso?', 'key': 'statusAtual', 'section': 'academica', 'index': 0},
    {'question': 'Qual é a fase atual do curso?', 'key': 'faseAtual', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o nome da empresa em que trabalhou?', 'key': 'nome', 'section': 'experiencia', 'index': 0},
    {'question': 'Qual era o cargo ocupado?', 'key': 'cargo', 'section': 'experiencia', 'index': 0},
    {'question': 'Descreva uma função que você desempenhou.', 'key': 'funcao1', 'section': 'experiencia', 'index': 0, 'subkey': 'funcoes'},
    {'question': 'Descreva outra função que você desempenhou.', 'key': 'funcao2', 'section': 'experiencia', 'index': 0, 'subkey': 'funcoes'},
    {'question': 'Qual é o nome do seu certificado?', 'key': 'nome', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual é o curso relacionado ao certificado?', 'key': 'curso', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual é a instituição emissora do certificado?', 'key': 'instituicao', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual idioma você fala?', 'key': 'lingua', 'section': 'idiomas', 'index': 0},
    {'question': 'Qual é o seu nível de fluência no idioma?', 'key': 'fluencia', 'section': 'idiomas', 'index': 0},
]

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, 'Currículo', 0, 1, 'C')
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", 'B', 12)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, title + ":", 0, 1, 'L')
        self.ln(2)

    def section_body(self, text):
        self.set_font("Arial", '', 8)  # Diminuir tamanho da fonte
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, text)
        self.ln(2)

    def add_section(self, title, content):
        self.section_title(title)
        self.section_body(content)
        self.ln(5)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()

    # Seções
    pdf.add_section("Dados Pessoais", "\n".join([f"{key.capitalize()}: {value}" for key, value in data["dadosPessoais"].items()]))
    pdf.add_section("Certificações", "\n".join([f"{cert['nome']}\n{cert['curso']}\n{cert['instituicao']}" for cert in data["certificacoes"]]))
    pdf.add_section("Idiomas", "\n".join([f"{idioma['lingua']}: {idioma['fluencia']}" for idioma in data["idiomas"]]))
    experiencia_content = "\n".join([
        f"{empresa['nome']} - {empresa['cargo']}\n" +
        "\n".join([f"{funcao}" for funcao in empresa["funcoes"]])
        for empresa in data["experiencia"]
    ])
    pdf.add_section("Experiência", experiencia_content)
    pdf.add_section("Formação Acadêmica", "\n".join([f"{form['curso']}\n{form['instituicao']}\n{form['periodo']}\n{form['statusAtual']}, {form['faseAtual']}" for form in data["academica"]]))
    pdf.add_section("Objetivo Profissional", data["objetivoProfissional"]["descricao"])

    pdf_file = "curriculo.pdf"
    pdf.output(pdf_file)
    return pdf_file

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Bom dia!"
    elif current_hour < 18:
        greeting = "Boa tarde!"
    else:
        greeting = "Boa noite!"
    
    emit('message', {'text': f'{greeting} Vamos criar seu currículo. Qual é o seu email?'})

@socketio.on('message')
def handle_message(data):
    global curriculo_data

    if 'dadosPessoais' not in curriculo_data:
        curriculo_data['dadosPessoais'] = {}
    
    if 'current_step' not in curriculo_data:
        curriculo_data['current_step'] = 0

    step = steps[curriculo_data['current_step']]

    if 'section' in step:
        section = step['section']
        if section not in curriculo_data:
            curriculo_data[section] = [{}]
        if 'index' in step:
            index = step['index']
            if index >= len(curriculo_data[section]):
                curriculo_data[section].append({})
            if 'subkey' in step:
                subkey = step['subkey']
                if subkey not in curriculo_data[section][index]:
                    curriculo_data[section][index][subkey] = []
                curriculo_data[section][index][subkey].append(data['text'])
            else:
                curriculo_data[section][index][step['key']] = data['text']
        else:
            curriculo_data[section][step['key']] = data['text']
    else:
        curriculo_data['dadosPessoais'][step['key']] = data['text']

    curriculo_data['current_step'] += 1

    if curriculo_data['current_step'] < len(steps):
        next_step = steps[curriculo_data['current_step']]
        emit('message', {'text': next_step['question']})
    else:
        emit('message', {'text': 'Obrigado por fornecer todas as informações! Clique no link abaixo para baixar seu currículo.'})
        emit('complete', {'link': '/download'})

@app.route('/download')
def download_curriculo():
    pdf_file = generate_pdf(curriculo_data)
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

# ------------------------------------------------------------------------- v 1.0.0

import os
from fpdf import FPDF
from flask import Flask, render_template, send_file, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Pasta onde os currículos serão salvos
CURRICULO_DIR = os.path.join(os.getcwd(), 'curriculos')
if not os.path.exists(CURRICULO_DIR):
    os.makedirs(CURRICULO_DIR)

# Variável global para armazenar os dados do currículo
curriculo_data = {
    'dadosPessoais': {},
    'objetivoProfissional': {},
    'academica': [],
    'experiencia': [],
    'certificacoes': [],
    'idiomas': [],
    'current_step': 0
}

steps = [
    {'question': 'Qual é o seu email?', 'key': 'email'},
    {'question': 'Qual é o seu telefone?', 'key': 'telefone'},
    {'question': 'Qual é a sua cidade?', 'key': 'cidade'},
    {'question': 'Qual é a sua data de nascimento?', 'key': 'dataNascimento'},
    {'question': 'Descreva seu objetivo profissional.', 'key': 'descricao', 'section': 'objetivoProfissional'},
    {'question': 'Qual é o seu curso?', 'key': 'curso', 'section': 'academica', 'index': 0},
    {'question': 'Qual é a instituição de ensino?', 'key': 'instituicao', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o período do curso?', 'key': 'periodo', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o status atual do curso?', 'key': 'statusAtual', 'section': 'academica', 'index': 0},
    {'question': 'Qual é a fase atual do curso?', 'key': 'faseAtual', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o nome da empresa em que trabalhou?', 'key': 'nome', 'section': 'experiencia', 'index': 0},
    {'question': 'Qual era o cargo ocupado?', 'key': 'cargo', 'section': 'experiencia', 'index': 0},
    {'question': 'Descreva uma função que você desempenhou.', 'key': 'funcao1', 'section': 'experiencia', 'index': 0, 'subkey': 'funcoes'},
    {'question': 'Descreva outra função que você desempenhou.', 'key': 'funcao2', 'section': 'experiencia', 'index': 0, 'subkey': 'funcoes'},
    {'question': 'Qual é o nome do seu certificado?', 'key': 'nome', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual é o curso relacionado ao certificado?', 'key': 'curso', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual é a instituição emissora do certificado?', 'key': 'instituicao', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual idioma você fala?', 'key': 'lingua', 'section': 'idiomas', 'index': 0},
    {'question': 'Qual é o seu nível de fluência no idioma?', 'key': 'fluencia', 'section': 'idiomas', 'index': 0},
]

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, 'Currículo', 0, 1, 'C')
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", 'B', 12)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, title + ":", 0, 1, 'L')
        self.ln(2)

    def section_body(self, text):
        self.set_font("Arial", '', 8)  # Diminuir tamanho da fonte
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, text)
        self.ln(2)

    def add_section(self, title, content):
        self.section_title(title)
        self.section_body(content)
        self.ln(5)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()

    # Seções
    pdf.add_section("Dados Pessoais", "\n".join([f"{key.capitalize()}: {value}" for key, value in data["dadosPessoais"].items()]))
    pdf.add_section("Certificações", "\n".join([f"{cert['nome']}\n{cert['curso']}\n{cert['instituicao']}" for cert in data["certificacoes"]]))
    pdf.add_section("Idiomas", "\n".join([f"{idioma['lingua']}: {idioma['fluencia']}" for idioma in data["idiomas"]]))
    experiencia_content = "\n".join([
        f"{empresa['nome']} - {empresa['cargo']}\n" +
        "\n".join([f"{funcao}" for funcao in empresa["funcoes"]])
        for empresa in data["experiencia"]
    ])
    pdf.add_section("Experiência", experiencia_content)
    pdf.add_section("Formação Acadêmica", "\n".join([f"{form['curso']}\n{form['instituicao']}\n{form['periodo']}\n{form['statusAtual']}, {form['faseAtual']}" for form in data["academica"]]))
    pdf.add_section("Objetivo Profissional", data["objetivoProfissional"]["descricao"])

    pdf_filename = f"curriculo_{data['dadosPessoais'].get('email', 'sem_email')}.pdf"
    pdf_filepath = os.path.join(CURRICULO_DIR, pdf_filename)
    pdf.output(pdf_filepath)
    return pdf_filepath

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Bom dia!"
    elif current_hour < 18:
        greeting = "Boa tarde!"
    else:
        greeting = "Boa noite!"
    
    emit('message', {'text': f'{greeting} Vamos criar seu currículo. Qual é o seu email?'})

@socketio.on('message')
def handle_message(data):
    global curriculo_data

    if 'dadosPessoais' not in curriculo_data:
        curriculo_data['dadosPessoais'] = {}
    
    step_index = curriculo_data['current_step']

    if step_index < len(steps):
        step = steps[step_index]

        if 'section' in step:
            section = step['section']
            if section not in curriculo_data:
                curriculo_data[section] = [{}]
            if 'index' in step:
                index = step['index']
                if index >= len(curriculo_data[section]):
                    curriculo_data[section].append({})
                if 'subkey' in step:
                    subkey = step['subkey']
                    if subkey not in curriculo_data[section][index]:
                        curriculo_data[section][index][subkey] = []
                    curriculo_data[section][index][subkey].append(data['text'])
                else:
                    curriculo_data[section][index][step['key']] = data['text']
            else:
                curriculo_data[section][step['key']] = data['text']
        else:
            curriculo_data['dadosPessoais'][step['key']] = data['text']

        curriculo_data['current_step'] += 1

        if curriculo_data['current_step'] < len(steps):
            next_step = steps[curriculo_data['current_step']]
            emit('message', {'text': next_step['question']})
        else:
            emit('message', {'text': 'Obrigado por fornecer todas as informações! Clique no link abaixo para baixar seu currículo.'})
            emit('complete', {'link': '/download'})
    else:
        emit('message', {'text': 'Erro: Passo atual fora do intervalo dos passos definidos.'})

@app.route('/download')
def download_curriculo():
    pdf_file = generate_pdf(curriculo_data)
    return send_file(pdf_file, as_attachment=True)

@app.route('/curriculos/<filename>')
def get_curriculo(filename):
    return send_from_directory(CURRICULO_DIR, filename)

@app.route('/curriculos')
def list_curriculos():
    curriculos = os.listdir(CURRICULO_DIR)
    return jsonify(curriculos)

if __name__ == '__main__':
    socketio.run(app, debug=True)

"""

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from fpdf import FPDF

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")

# Variável global para armazenar os dados do currículo
curriculo_data = {
    'dadosPessoais': {},
    'objetivoProfissional': {},
    'academica': [],
    'experiencia': [],
    'certificacoes': [],
    'idiomas': []
}

steps = [
    {'question': 'Qual é o seu email?', 'key': 'email'},
    {'question': 'Qual é o seu telefone?', 'key': 'telefone'},
    {'question': 'Qual é a sua cidade?', 'key': 'cidade'},
    {'question': 'Qual é a sua data de nascimento?', 'key': 'dataNascimento'},
    {'question': 'Descreva seu objetivo profissional.', 'key': 'descricao', 'section': 'objetivoProfissional'},
    {'question': 'Qual é o seu curso?', 'key': 'curso', 'section': 'academica', 'index': 0},
    {'question': 'Qual é a instituição de ensino?', 'key': 'instituicao', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o período do curso?', 'key': 'periodo', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o status atual do curso?', 'key': 'statusAtual', 'section': 'academica', 'index': 0},
    {'question': 'Qual é a fase atual do curso?', 'key': 'faseAtual', 'section': 'academica', 'index': 0},
    {'question': 'Qual é o nome da empresa em que trabalhou?', 'key': 'nome', 'section': 'experiencia', 'index': 0},
    {'question': 'Qual era o cargo ocupado?', 'key': 'cargo', 'section': 'experiencia', 'index': 0},
    {'question': 'Descreva uma função que você desempenhou.', 'key': 'funcao1', 'section': 'experiencia', 'index': 0, 'subkey': 'funcoes'},
    {'question': 'Descreva outra função que você desempenhou.', 'key': 'funcao2', 'section': 'experiencia', 'index': 0, 'subkey': 'funcoes'},
    {'question': 'Qual é o nome do seu certificado?', 'key': 'nome', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual é o curso relacionado ao certificado?', 'key': 'curso', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual é a instituição emissora do certificado?', 'key': 'instituicao', 'section': 'certificacoes', 'index': 0},
    {'question': 'Qual idioma você fala?', 'key': 'lingua', 'section': 'idiomas', 'index': 0},
    {'question': 'Qual é o seu nível de fluência no idioma?', 'key': 'fluencia', 'section': 'idiomas', 'index': 0},
]

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, 'Currículo', 0, 1, 'C')
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", 'B', 12)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, title + ":", 0, 1, 'L')
        self.ln(2)

    def section_body(self, text):
        self.set_font("Arial", '', 8)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, text)
        self.ln(2)

    def add_section(self, title, content):
        self.section_title(title)
        self.section_body(content)
        self.ln(5)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.add_section("Dados Pessoais", "\n".join([f"{key.capitalize()}: {value}" for key, value in data["dadosPessoais"].items()]))
    pdf.add_section("Certificações", "\n".join([f"{cert['nome']}\n{cert['curso']}\n{cert['instituicao']}" for cert in data["certificacoes"]]))
    pdf.add_section("Idiomas", "\n".join([f"{idioma['lingua']}: {idioma['fluencia']}" for idioma in data["idiomas"]]))
    experiencia_content = "\n".join([
        f"{empresa['nome']} - {empresa['cargo']}\n" +
        "\n".join([f"{funcao}" for funcao in empresa["funcoes"]])
        for empresa in data["experiencia"]
    ])
    pdf.add_section("Experiência", experiencia_content)
    pdf.add_section("Formação Acadêmica", "\n".join([f"{form['curso']}\n{form['instituicao']}\n{form['periodo']}\n{form['statusAtual']}, {form['faseAtual']}" for form in data["academica"]]))
    pdf.add_section("Objetivo Profissional", data["objetivoProfissional"]["descricao"])
    pdf_file = "/curriculos/curriculo.pdf"
    pdf.output(pdf_file)
    return pdf_file

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@socketio.on('connect')
def handle_connect():
    emit('message', {'text': 'Olá! Vamos criar seu currículo. Qual é o seu email?'})

@socketio.on('message')
def handle_message(data):
    global curriculo_data
    if 'dadosPessoais' not in curriculo_data:
        curriculo_data['dadosPessoais'] = {}
    if 'current_step' not in curriculo_data:
        curriculo_data['current_step'] = 0
    step = steps[curriculo_data['current_step']]
    if 'section' in step:
        section = step['section']
        if section not in curriculo_data:
            curriculo_data[section] = [{}]
        if 'index' in step:
            index = step['index']
            if index >= len(curriculo_data[section]):
                curriculo_data[section].append({})
            if 'subkey' in step:
                subkey = step['subkey']
                if subkey not in curriculo_data[section][index]:
                    curriculo_data[section][index][subkey] = []
                curriculo_data[section][index][subkey].append(data['text'])
            else:
                curriculo_data[section][index][step['key']] = data['text']
        else:
            curriculo_data[section][step['key']] = data['text']
    else:
        curriculo_data['dadosPessoais'][step['key']] = data['text']
    curriculo_data['current_step'] += 1
    if curriculo_data['current_step'] < len(steps):
        next_step = steps[curriculo_data['current_step']]
        emit('message', {'text': next_step['question']})
    else:
        emit('message', {'text': 'Obrigado por fornecer todas as informações! Clique no link abaixo para baixar seu currículo.'})
        emit('complete', {'link': '/download'})

@app.route('/download')
def download_curriculo():
    pdf_file = generate_pdf(curriculo_data)
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
