from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ==============================================
# 🔧 CONEXÃO COM BANCO
# ==============================================
def conectar_banco():
    try:
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME")
        )
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

# ==============================================
# 📧 FUNÇÃO ENVIAR E-MAIL
# ==============================================
def enviar_email_contrato(destinatario, nome, id_contrato, dados, valor_total, valor_entrada):
    remetente = os.environ.get("EMAIL_REMETENTE")
    senha = os.environ.get("EMAIL_SENHA")
    smtp_servidor = os.environ.get("EMAIL_SMTP", "smtp.gmail.com")
    smtp_porta = int(os.environ.get("EMAIL_PORTA", 587))

    if not remetente or not senha or not destinatario:
        print("⚠️ E-mail não configurado ou destinatário vazio")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = f"Contrato nº {id_contrato} — Espaço Comemore"

        valor_pago = dados.get('valor_pago', 0)
        restante = valor_total - valor_pago

        corpo = f"""
==================================================
       CONTRATO DE LOCAÇÃO DE ESPAÇO
     Espaço Comemore Festas e Eventos
==================================================

CONTRATADO:
Leandro Ruy Batista da Silva
CPF: 682.459.552-72
Tel: (68) 99921-7686 / 99241-4341

--------------------------------------------------

CONTRATANTE:
Nome: {nome}
CPF: {dados['cpf_contratante']}
Endereço: {dados['endereco_contratante']}
Telefone: {dados['telefone_contratante']}

--------------------------------------------------

DADOS DO EVENTO:
Tipo: {dados['tipo_evento']}
Data: {dados['data_evento']}
Horário: {dados['horario_inicio']} às {dados['horario_termino']}
Mesas: {dados['qtd_mesas']}
Piscina: {dados['uso_piscina']}
Som: {dados['uso_som']}
Pula-Pula: {'SIM' if dados.get('pula_pula') else 'NÃO'}
Piscina de Bolinhas: {'SIM' if dados.get('piscina_bolinha') else 'NÃO'}

--------------------------------------------------

VALORES:
Valor Total: R$ {valor_total:.2f}
Entrada:     R$ {valor_entrada:.2f}
Pago:        R$ {valor_pago:.2f}
Restante:    R$ {restante:.2f}
Pagamento:   {dados['forma_pagamento_entrada']}

--------------------------------------------------

Rio Branco/AC, {datetime.now().strftime('%d/%m/%Y')}

Declaro que li e concordo com todos os termos.

==================================================
Espaço Comemore — Tel: (68) 99921-7686
Contrato nº {id_contrato}
==================================================
        """.strip()

        msg.attach(MIMEText(corpo, "plain"))

        # Anexar cópia do contrato em texto
        anexo = MIMEBase("text", "plain")
        anexo.set_payload(corpo.encode('utf-8'))
        encoders.encode_base64(anexo)
        anexo.add_header("Content-Disposition", f"attachment; filename=Contrato_{id_contrato}.txt")
        msg.attach(anexo)

        # Enviar
        with smtplib.SMTP(smtp_servidor, smtp_porta) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha)
            servidor.send_message(msg)

        print(f"✅ E-mail enviado para {destinatario}")
        return True

    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False

# ==============================================
# 🌐 ROTAS
# ==============================================
@app.route('/')
def home():
    return send_from_directory('static', 'contrato.html')

@app.route('/salvar-contrato', methods=['POST'])
def salvar_contrato():
    try:
        dados = request.get_json(force=True)
        print("📥 DADOS RECEBIDOS:", dados)

        # Converter data
        dia, mes, ano = map(int, dados['data_evento'].split('/'))
        data_evento = datetime(ano, mes, dia)
        dia_semana = data_evento.weekday()

        # Calcular valor base
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
        if dados.get('qtd_mesas') == 20: valor_base += 60.00
        if dados.get('qtd_mesas') == 25: valor_base += 120.00
        if dados.get('uso_som') == 'sim_microfone': valor_base += 30.00
        if dados.get('pula_pula'): valor_base += 110.00
        if dados.get('piscina_bolinha'): valor_base += 110.00

        # Promoção: kit = R$ 200 (economiza R$20)
        if dados.get('pula_pula') and dados.get('piscina_bolinha'):
            valor_base -= 20.00

        data_vencimento = data_evento - timedelta(days=5)

        # Salvar no banco
        conexao = conectar_banco()
        if not conexao:
            return jsonify({"sucesso": False, "mensagem": "❌ Sem conexão com o banco"}), 500

        cursor = conexao.cursor()
        sql = """
        INSERT INTO contratos (
            nome_contratado, cpf_contratado, endereco_contratado, telefone_contratado,
            nome_contratante, cpf_contratante, endereco_contratante, telefone_contratante, email_contratante,
            tipo_evento, observacao_evento, data_evento, horario_inicio, horario_termino,
            qtd_mesas, uso_piscina, uso_som, horario_entrega_bebidas, horario_recebimento_espaco,
            pula_pula, piscina_bolinha, valor_locacao, valor_entrada, valor_pago, forma_pagamento_entrada,
            data_vencimento_restante, aceite_funcionamento, aceite_uso_espaco,
            aceite_obrigacoes_contratado, aceite_obrigacoes_contratante, aceite_cancelamento,
            aceite_gerais, aceite_final_contrato, status_contrato
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            "Leandro Ruy Batista da Silva", "682.459.552-72",
            "Rua Isaura Parente, nº 100 - Rio Branco/AC", "(68) 99921-7686 / 99241-4341",
            dados['nome_contratante'], dados['cpf_contratante'],
            dados['endereco_contratante'], dados['telefone_contratante'], dados.get('email_contratante', ''),
            dados['tipo_evento'], dados.get('observacao_evento', ''),
            data_evento.strftime('%Y-%m-%d'), dados['horario_inicio'], dados['horario_termino'],
            dados['qtd_mesas'], dados['uso_piscina'], dados['uso_som'],
            dados['horario_entrega_bebidas'], dados['horario_recebimento_espaco'],
            dados['pula_pula'], dados['piscina_bolinha'],
            valor_base, valor_entrada, dados.get('valor_pago', 0), dados['forma_pagamento_entrada'],
            data_vencimento.strftime('%Y-%m-%d'),
            dados['aceite_funcionamento'], dados['aceite_uso_espaco'],
            dados['aceite_obrigacoes_contratado'], dados['aceite_obrigacoes_contratante'],
            dados['aceite_cancelamento'], dados['aceite_gerais'],
            dados['aceite_final_contrato'], 'pendente'
        )
        cursor.execute(sql, valores)
        conexao.commit()
        id_contrato = cursor.lastrowid
        cursor.close()
        conexao.close()

        # 📧 Enviar e-mail
        email_ok = enviar_email_contrato(
            dados.get('email_contratante'),
            dados['nome_contratante'],
            id_contrato,
            dados,
            valor_base,
            valor_entrada
        )

        mensagem = f"✅ Contrato salvo com sucesso! ID: {id_contrato}"
        if email_ok:
            mensagem += " | 📧 E-mail enviado!"

        return jsonify({
            "sucesso": True,
            "mensagem": mensagem,
            "id_contrato": id_contrato,
            "valor_total": round(valor_base, 2),
            "valor_entrada": round(valor_entrada, 2),
            "email_enviado": email_ok
        }), 201

    except Exception as erro:
        print(f"❌ ERRO GERAL: {erro}")
        return jsonify({"sucesso": False, "mensagem": f"❌ Erro: {str(erro)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
