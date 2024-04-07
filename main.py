import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# Diretório para salvar os arquivos temporários
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

STATIC_FOLDER = 'static'
app.config['STATIC_FOLDER'] = STATIC_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Verifica se o arquivo está presente na solicitação
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado'
    
    file = request.files['file']

    # Verifica se o arquivo é do tipo CSV
    if file.filename == '':
        return 'Nenhum arquivo selecionado'
    
    if file and file.filename.endswith('.csv'):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) 
        file.save(filename)

        #Processa o arquivo CSV

        df = pd.read_csv(filename, skiprows=9)

        # Adicionar colunas 'Placa' e 'Hora' ao DataFrame
        df['Placa'] = ''
        df['Hora'] = ''

        # Dividir a coluna 'Data' em 'Data' e 'Hora'
        df[['Data', 'Hora']] = df['Data'].str.split(' ', expand=True)

        # Converter as colunas Latitude e Longitude para strings
        df['Latitude'] = df['Latitude'].astype(str)
        df['Longitude'] = df['Longitude'].astype(str)

        # Trocar o ponto por vírgula nas colunas Latitude e Longitude
        df['Latitude'] = df['Latitude'].str.replace('.', ',')
        df['Longitude'] = df['Longitude'].str.replace('.', ',')

        # Renomear a coluna 'Veloc' para 'Velocidade'
        df = df.rename(columns={'Veloc.': 'Velocidade'})
        # Selecionar as colunas necessárias
        df = df[['Placa', 'Data', 'Hora', 'Direção', 'Velocidade', 'Latitude', 'Longitude']]

        output_file = os.path.join(app.config['STATIC_FOLDER'], 'output.csv') 
        df.to_csv(output_file, index=False)

        os.remove(filename)

        return redirect(url_for('download', filename='output.csv'))
    else:
        return 'Formato do arquivo inválido. Por favor, envie um arquivo CSV.'
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
