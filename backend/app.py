from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def conectar_banco():
    return mysql.connector.connect(
        host="seu-host-railway",
        user="seu-usuario",
        password="sua-senha",
        database="seu-banco"
    )

@app.route('/salvar-contrato', methods=['POST'])
def salvar_contrato():
    try:
        dados = request.json
        data_evento = datetime.strptime(dados['data_evento'], '%d/%m/%Y')
        dia_semana = data_evento.weekday()

        if dia_semana in range(0,4): valor_base = 400.00
        elif dia_semana in (4,6): valor_base = 450.00
        else: valor_base = 550.00

        if dados['qtd_mesas'] == 20: valor_base += 60.00
        if dados['qtd_mesas'] == 25: valor_base += 120.00
        if dados['uso_som'] == 'sim_microfone': valor_base += 30.00
        if dados['pula_pula']: valor_base += 110.00
        if dados['piscina_bolinha']: valor_base += 110.00

        conexao = conectar_banco()
        cursor = conexao.cursor()
        sql = """INSERT INTO contratos (...) VALUES (...)"""
        cursor.execute(sql, dados)
        conexao.commit()
        return jsonify({"sucesso": True}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
