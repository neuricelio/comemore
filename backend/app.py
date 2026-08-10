from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 📧 Importa bibliotecas para e-mail e PDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ==============================================
# 🔧 CONFIGURAÇÕES
# ==============================================
def conectar_banco():
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    database = os.environ.get("DB_NAME")
    try:
        return mysql.connector.connect(
            host=host, port=int(port), user=user, password=password, database=database
        )
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

# ==============================================
# 📧 FUNÇÃO ENVIAR E-MAIL COM ANEXO
# ==============================================
def enviar_email_com_pdf(destinatario, nome_contratante, id_contrato, dados, valor_total, valor_entrada):
    remetente = os.environ.get("EMAIL_REMETENTE")
    senha = os.environ.get("EMAIL_SENHA")
    smtp_servidor = os.environ.get("EMAIL_SMTP", "smtp.gmail.com")
    smtp_porta = int(os.environ.get("EMAIL_PORTA", 587))

    if not remetente or not senha:
        print("⚠️ E-mail não configurado — pulando envio")
        return False

    try:
        # Monta mensagem
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = f"Contrato nº {id_contrato} — Espaço Comemore"

        corpo = f"""
Olá {nome_contratante},

Seu contrato foi salvo com sucesso! 🎉

📋 Dados do Contrato:
• Número: {id_contrato}
• Data do Evento: {dados['data_evento']}
• Horário: {dados['horario_inicio']} às {dados['horario_termino']}
• Valor Total: R$ {valor_total:.2f}
• Valor de Entrada: R$ {valor_entrada:.2f}
• Valor Pago: R$ {dados.get('valor_pago', 0):.2f}

Atenciosamente,
Equipe Espaço Comemore Festas e Eventos
📞 (68) 99921-7686
        """
        msg.attach(MIMEText(corpo, "plain"))

        # 📄 Gerar PDF temporário
        nome_arquivo = f"/tmp/Contrato_{id_contrato}.pdf"
        gerar_pdf_contrato(nome_arquivo, id_contrato, dados, valor_total, valor_entrada)

        # Anexar PDF
        with open(nome_arquivo, "rb") as anexo:
            parte = MIMEBase("application", "octet-stream")
            parte.set_payload(anexo.read())
        encoders.encode_base64(parte)
        parte.add_header(
            "Content-Disposition",
            f"attachment; filename=Contrato_{id_contrato}.pdf",
        )
        msg.attach(parte)

        # 📤 Enviar
        servidor = smtplib.SMTP(smtp_servidor, smtp_porta)
        servidor.starttls()
        servidor.login(remetente, senha)
        texto = servidor.as_string()
        servidor.sendmail(remetente, destinatario, texto)
        servidor.quit()

        print(f"✅ E-mail enviado para {destinatario}")
        os.remove(nome_arquivo)  # Apaga arquivo temporário
        return True

    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False

# ==============================================
# 📄 GERAR PDF COM O CONTRATO
# ==============================================
def gerar_pdf_contrato(caminho_arquivo, id_contrato, dados, valor_total, valor_entrada):
    pagina = canvas.Canvas(caminho_arquivo, pagesize=A4)
    largura, altura = A4
    y = altura - 50

    def linha(texto, deslocamento=0):
        nonlocal y
        pagina.drawString(50 + deslocamento, y, texto)
        y -= 22

    # Cabeçalho
    pagina.setFont("Helvetica-Bold", 18)
    linha("CONTRATO DE LOCAÇÃO DE ESPAÇO", 100)
    pagina.setFont("Helvetica", 12)
    linha("Espaço Comemore Festas e Eventos", 130)
    linha("-" * 80, 50)
    y -= 10

    # Dados do Contratado
    pagina.setFont("Helvetica-Bold", 12)
    linha("CONTRATADO:")
    pagina.setFont("Helvetica", 11)
    linha("Leandro Ruy Batista da Silva")
    linha("CPF: 682.459.552-72")
    linha("Telefone: (68) 99921-7686 / 99241-4341")
    linha("")

    # Dados do Contratante
    pagina.setFont("Helvetica-Bold", 12)
    linha("CONTRATANTE:")
    pagina.setFont("Helvetica", 11)
    linha(f"Nome: {dados['nome_contratante']}")
    linha(f"CPF: {dados['cpf_contratante']}")
    linha(f"Endereço: {dados['endereco_contratante']}")
    linha(f"Telefone: {dados['telefone_contratante']}")
    linha("")

    # Dados do Evento
    pagina.setFont("Helvetica-Bold", 12)
    linha("DADOS DO EVENTO:")
    pagina.setFont("Helvetica", 11)
    linha(f"Tipo: {dados['tipo_evento']}")
    linha(f"Data: {dados['data_evento']}")
    linha(f"Horário: {dados['horario_inicio']} às {dados['horario_termino']}")
    linha(f"Mesas: {dados['qtd_mesas']}")
    linha(f"Piscina: {dados['uso_piscina']}")
    linha(f"Som: {dados['uso_som']}")
    linha(f"Pula-Pula: {'SIM' if dados.get('pula_pula') else 'NÃO'}")
    linha(f"Piscina de Bolinhas: {'SIM' if dados.get('piscina_bolinha') else 'NÃO'}")
    linha("")

    # Valores
    valor_pago = dados.get('valor_pago', 0)
    restante = valor_total - valor_pago
    pagina.setFont("Helvetica-Bold", 12)
    linha("VALORES:")
    pagina.setFont("Helvetica", 11)
    linha(f"Valor Total da Locação: R$ {valor_total:.2f}")
    linha(f"Valor de Entrada: R$ {valor_entrada:.2f}")
    linha(f"Valor Pago: R$ {valor_pago:.2f}")
    linha(f"Valor Restante: R$ {restante:.2f}")
    linha(f"Forma de Pagamento: {dados['forma_pagamento_entrada']}")
    linha("")
    linha("")

    # Assinaturas
    linha("Declaro que li, conferi e concordo com todos os termos.")
    linha("")
    linha("__________________________________________________")
    linha(f"{dados['nome_contratante']} — Contratante")
    linha("")
    linha("__________________________________________________")
    linha("Leandro Ruy Batista da Silva — Contratado")
    linha("")
    linha("")
    linha(f"Contrato nº {id_contrato} — Rio Branco/AC, {datetime.now().strftime('%d/%m/%Y')}")

    pagina.save()

# ==============================================
# 🌐 ROTAS
# ==============================================
@app.route('/')
def home():
    return send_from_directory('static', 'contrato.html')

@app.route('/verificar-config')
def verificar():
    return f"DB_HOST: {os.environ.get('DB_HOST')}<br>DB_PORT: {os.environ.get('DB_PORT')}"

@app.route('/salvar-contrato', methods=['POST'])
def salvar_contrato():
    try:
        dados = request.get_json(force=True)
        print("📥 DADOS RECEBIDOS:", dados)

        # Converter data
        dia, mes, ano = map(int, dados['data_evento'].split('/'))
        data_evento = datetime(ano, mes, dia)
        dia_semana = data_evento.weekday()

        # Calcular valores
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

        # Promoção: os dois juntos = R$ 200 (economiza R$20)
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
            nome_contratante, cpf_contratante, endereco_contratante, telefone_contratante,
            tipo_evento, observacao_evento, data_evento, horario_inicio, horario_termino,
            qtd_mesas, uso_piscina, uso_som, horario_entrega_bebidas, horario_recebimento_espaco,
            pula_pula, piscina_bolinha, valor_locacao, valor_entrada, valor_pago, forma_pagamento_entrada,
            data_vencimento_restante, aceite_funcionamento, aceite_uso_espaco,
            aceite_obrigacoes_contratado, aceite_obrigacoes_contratante, aceite_cancelamento,
            aceite_gerais, aceite_final_contrato, status_contrato
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            "Leandro Ruy Batista da Silva", "682.459.552-72",
            "Rua Isaura Parente, esquina com a Rua Veneza, nº 100 - Rio Branco/AC",
            "(68) 99921-7686 / 99241-4341",
            dados['nome_contratante'], dados['cpf_contratante'],
            dados['endereco_contratante'], dados['telefone_contratante'],
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

        # 📧 ENVIAR E-MAIL (se tiver campo e-mail, senão avisa)
        email_enviado = False
        email_destinatario = dados.get('email_contratante')  # ← vamos adicionar esse campo
        if email_destinatario:
            email_enviado = enviar_email_com_pdf(
                email_destinatario,
                dados['nome_contratante'],
                id_contrato,
                dados,
                valor_base,
                valor_entrada
            )

        return jsonify({
            "sucesso": True,
            "mensagem": f"✅ Contrato salvo!{' E-mail enviado!' if email_enviado else ''}",
            "id_contrato": id_contrato,
            "valor_total": round(valor_base, 2),
            "valor_entrada": round(valor_entrada, 2),
            "email_enviado": email_enviado
        }), 201

    except Exception as erro:
        print(f"❌ ERRO: {erro}")
        return jsonify({"sucesso": False, "mensagem": f"❌ Erro: {str(erro)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
