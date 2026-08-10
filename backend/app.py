from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
import os
import traceback

# 🛡️ Tenta importar ReportLab — se falhar, NÃO quebra o sistema
try:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    PDF_DISPONIVEL = True
except Exception as e:
    print(f"⚠️ ReportLab não disponível: {e}")
    PDF_DISPONIVEL = False

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
# 📄 GERAR PDF (com proteção)
# ==============================================
def gerar_pdf_contrato(caminho, id_contrato, dados, valor_total, valor_entrada):
    if not PDF_DISPONIVEL:
        return False
    try:
        pagina = canvas.Canvas(caminho, pagesize=A4)
        largura, altura = A4
        y = altura - 50

        def linha(texto, desl=0):
            nonlocal y
            pagina.drawString(50 + desl, y, texto)
            y -= 22

        pagina.setFont("Helvetica-Bold", 18)
        linha("CONTRATO DE LOCAÇÃO DE ESPAÇO", 100)
        pagina.setFont("Helvetica", 12)
        linha("Espaco Comemore Festas e Eventos", 130)
        linha("-" * 70, 50)
        y -= 10

        pagina.setFont("Helvetica-Bold", 12)
        linha("CONTRATADO:")
        pagina.setFont("Helvetica", 11)
        linha("Leandro Ruy Batista da Silva")
        linha("CPF: 682.459.552-72")
        linha("Telefone: (68) 99921-7686")
        linha("")

        pagina.setFont("Helvetica-Bold", 12)
        linha("CONTRATANTE:")
        pagina.setFont("Helvetica", 11)
        linha(f"Nome: {dados['nome_contratante']}")
        linha(f"CPF: {dados['cpf_contratante']}")
        linha(f"Telefone: {dados['telefone_contratante']}")
        linha("")

        pagina.setFont("Helvetica-Bold", 12)
        linha("DADOS DO EVENTO:")
        pagina.setFont("Helvetica", 11)
        linha(f"Data: {dados['data_evento']} — {dados['horario_inicio']} as {dados['horario_termino']}")
        linha(f"Mesas: {dados['qtd_mesas']}")
        linha(f"Piscina: {dados['uso_piscina']}")
        linha(f"Som: {dados['uso_som']}")
        linha("")

        valor_pago = dados.get('valor_pago', 0)
        restante = valor_total - valor_pago
        linha(f"Valor Total: R$ {valor_total:.2f}")
        linha(f"Pago: R$ {valor_pago:.2f} | Restante: R$ {restante:.2f}")
        linha("")
        linha("Assinaturas:")
        linha("_" * 50)
        linha("Contratante")
        linha("_" * 50)
        linha("Contratado")

        pagina.save()
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return False

# ==============================================
# 📧 ENVIAR E-MAIL
# ==============================================
def enviar_email(destinatario, nome, id_contrato, dados, valor_total, valor_entrada):
    if not PDF_DISPONIVEL:
        return False
    remetente = os.environ.get("EMAIL_REMETENTE")
    senha = os.environ.get("EMAIL_SENHA")
    if not remetente or not senha:
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = f"Contrato n° {id_contrato} — Espaco Comemore"
        msg.attach(MIMEText(f"""Olá {nome}, seu contrato foi salvo com sucesso! Valor total: R$ {valor_total:.2f}. Em anexo o contrato em PDF.""", "plain"))

        caminho = f"/tmp/Contrato_{id_contrato}.pdf"
        if gerar_pdf_contrato(caminho, id_contrato, dados, valor_total, valor_entrada):
            with open(caminho, "rb") as f:
                parte = MIMEBase("application", "pdf")
                parte.set_payload(f.read())
            encoders.encode_base64(parte)
            parte.add_header("Content-Disposition", f"attachment; filename=Contrato_{id_contrato}.pdf")
            msg.attach(parte)
            os.remove(caminho)

        with smtplib.SMTP(os.environ.get("EMAIL_SMTP", "smtp.gmail.com"), int(os.environ.get("EMAIL_PORTA", 587))) as serv:
            serv.starttls()
            serv.login(remetente, senha)
            serv.send_message(msg)
        return True
    except Exception as e:
        print(f"❌ Erro e-mail: {e}")
        return False

# ==============================================
# 🌐 ROTAS
# ==============================================
@app.route('/')
def home():
    return send_from_directory('static', 'contrato.html')

@app.route('/salvar-contrato', methods=['POST'])
def salvar():
    try:
        dados = request.get_json(force=True)
        print("📥 DADOS RECEBIDOS:", dados)

        # Data e valores
        dia, mes, ano = map(int, dados['data_evento'].split('/'))
        data_evento = datetime(ano, mes, dia)
        dia_semana = data_evento.weekday()

        # Valores base por dia da semana
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

        pula = dados.get('pula_pula')
        bolinha = dados.get('piscina_bolinha')

        # Promoção
        if pula and bolinha:
            valor_base += 180.00  # 200 - 20 de desconto
        else:
            if pula: valor_base += 110.00
            if bolinha: valor_base += 110.00

        data_venc = data_evento - timedelta(days=5)

        # 🛡️ SALVAR NO BANCO
        conn = conectar_banco()
        if not conn:
            return jsonify({"sucesso": False, "mensagem": "❌ Sem conexão com o banco"}), 500

        cur = conn.cursor()
        sql = """
        INSERT INTO contratos (
            nome_contratado, cpf_contratado, endereco_contratado, telefone_contratado,
            nome_contratante, cpf_contratante, endereco_contratante, telefone_contratante,
            email_contratante, tipo_evento, observacao_evento, data_evento,
            horario_inicio, horario_termino, qtd_mesas, uso_piscina, uso_som,
            horario_entrega_bebidas, horario_recebimento_espaco, pula_pula, piscina_bolinha,
            valor_locacao, valor_entrada, valor_pago, forma_pagamento_entrada,
            data_vencimento_restante, status_contrato,
            aceite_funcionamento, aceite_uso_espaco,
            aceite_obrigacoes_contratado, aceite_obrigacoes_contratante,
            aceite_cancelamento, aceite_gerais, aceite_final_contrato
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        vals = (
            "Leandro Ruy Batista da Silva", "682.459.552-72",
            "Rua Isaura Parente, n° 100 — Rio Branco/AC", "(68) 99921-7686",
            dados['nome_contratante'], dados['cpf_contratante'],
            dados['endereco_contratante'], dados['telefone_contratante'],
            dados.get('email_contratante'), dados['tipo_evento'],
            dados.get('observacao_evento', ''), data_evento.strftime('%Y-%m-%d'),
            dados['horario_inicio'], dados['horario_termino'], dados['qtd_mesas'],
            dados['uso_piscina'], dados['uso_som'], dados['horario_entrega_bebidas'],
            dados['horario_recebimento_espaco'], pula, bolinha,
            valor_base, valor_entrada, dados.get('valor_pago', 0),
            dados['forma_pagamento_entrada'], data_venc.strftime('%Y-%m-%d'),
            'pendente',
            True, True, True, True, True, True, True
        )
        cur.execute(sql, vals)
        conn.commit()
        id_cont = cur.lastrowid
        cur.close()
        conn.close()

        # 📧 Tenta enviar e-mail (opcional)
        email_ok = False
        if dados.get('email_contratante') and PDF_DISPONIVEL:
            email_ok = enviar_email(dados['email_contratante'], dados['nome_contratante'], id_cont, dados, valor_base, valor_entrada)

        # ✅ SEMPRE retorna JSON
        return jsonify({
            "sucesso": True,
            "mensagem": f"✅ Contrato salvo! ID: {id_cont}" + (" | E-mail enviado" if email_ok else ""),
            "id_contrato": id_cont,
            "valor_total": round(valor_base, 2),
            "valor_entrada": round(valor_entrada, 2),
            "email_enviado": email_ok
        }), 201

    except Exception as e:
        print("❌ ERRO:", str(e))
        print(traceback.format_exc())
        # 🛡️ SEMPRE retorna JSON — NÃO retorna mais página HTML!
        return jsonify({
            "sucesso": False,
            "mensagem": f"❌ Erro: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
