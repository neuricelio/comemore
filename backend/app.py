from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # ✅ Resolve o bloqueio do botão
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Configuração correta da pasta static
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # ✅ Libera o botão para funcionar sem erro

# Conexão com o banco Railway
def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

# ✅ Rota correta para exibir o contrato
@app.route('/')
def home():
    return send_from_directory('static', 'contrato.html')

# ✅ Rota para salvar
@app.route('/salvar-contrato', methods=['POST'])
def salvar_contrato():
    try:
        dados = request.json

        # Cálculo automático de valores
        data_evento = datetime.strptime(dados['data_evento'], '%d/%m/%Y')
        dia_semana = data_evento.weekday()

        if dia_semana in range(0, 4):
            valor_base = 400.00
            valor_entrada = 150.00
        elif dia_semana in (4, 6):
            valor_base = 450.00
            valor_entrada = 200.00
        else:
            valor_base = 550.00
            valor_entrada = 250.00

        # Adicionais
        if dados['qtd_mesas'] == 20: valor_base += 60.00
        if dados['qtd_mesas'] == 25: valor_base += 120.00
        if dados['uso_som'] == 'sim_microfone': valor_base += 30.00
        if dados['pula_pula']: valor_base += 110.00
        if dados['piscina_bolinha']: valor_base += 110.00

        data_vencimento = data_evento.replace(day=data_evento.day - 5)

        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO contratos (
            nome_contratado, cpf_contratado, endereco_contratado, telefone_contratado,
            nome_contratante, cpf_contratante, endereco_contratante, telefone_contratante,
            tipo_evento, observacao_evento, data_evento, horario_inicio, horario_termino,
            qtd_mesas, uso_piscina, uso_som, horario_entrega_bebidas, horario_recebimento_espaco,
            pula_pula, piscina_bolinha, valor_locacao, valor_entrada, forma_pagamento_entrada,
            data_vencimento_restante, aceite_funcionamento, aceite_uso_espaco,
            aceite_obrigacoes_contratado, aceite_obrigacoes_contratante, aceite_cancelamento,
            aceite_gerais, aceite_final_contrato
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            "Leandro Ruy Batista da Silva", "682.459.552-72",
            "Rua Isaura Parente, esquina com a Rua Veneza, nº 100 - Rio Branco/AC",
            "(68) 99921-7686 / 99241-4341",
            dados['nome_contratante'], dados['cpf_contratante'], dados['endereco_contratante'],
            dados['telefone_contratante'], dados['tipo_evento'], dados['observacao_evento'],
            data_evento.strftime('%Y-%m-%d'), dados['horario_inicio'], dados['horario_termino'],
            dados['qtd_mesas'], dados['uso_piscina'], dados['uso_som'], dados['horario_entrega_bebidas'],
            dados['horario_recebimento_espaco'], dados['pula_pula'], dados['piscina_bolinha'],
            valor_base, valor_entrada, dados['forma_pagamento_entrada'],
            data_vencimento.strftime('%Y-%m-%d'),
            dados['aceite_funcionamento'], dados['aceite_uso_espaco'], dados['aceite_obrigacoes_contratado'],
            dados['aceite_obrigacoes_contratante'], dados['aceite_cancelamento'], dados['aceite_gerais'],
            dados['aceite_final_contrato']
        )

        cursor.execute(sql, valores)
        conexao.commit()
        id_gerado = cursor.lastrowid

        cursor.close()
        conexao.close()

        return jsonify({
            "sucesso": True,
            "mensagem": "✅ Contrato salvo com sucesso!",
            "id_contrato": id_gerado,
            "valor_total": round(valor_base, 2),
            "valor_entrada": round(valor_entrada, 2)
        }), 201

    except mysql.connector.IntegrityError:
        return jsonify({"sucesso": False, "mensagem": "⚠️ Já existe agendamento para essa data/horário!"}), 409
    except Exception as erro:
        return jsonify({"sucesso": False, "mensagem": f"❌ Erro: {str(erro)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
