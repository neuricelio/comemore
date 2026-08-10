document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formContrato");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const btn = document.getElementById("btnSalvar");
        btn.disabled = true;
        btn.textContent = "Enviando...";

        try {
            const formData = new FormData(form);

            // ✅ Define horário com base na opção escolhida
            let horario_inicio, horario_termino;
            const tipo_horario = formData.get("horario_tipo");

            if (tipo_horario === 'dia') {
                horario_inicio = "09:00";
                horario_termino = "17:00";
            } else if (tipo_horario === 'noite_semana') {
                horario_inicio = "17:00";
                horario_termino = "23:00";
            } else if (tipo_horario === 'noite_sabado') {
                horario_inicio = "17:00";
                horario_termino = "02:00";
            } else {
                horario_inicio = formData.get("horario_inicio");
                horario_termino = formData.get("horario_termino");
            }

            // ✅ Dados do formulário
            const dados = {
                nome_contratante: formData.get("nome_contratante"),
                cpf_contratante: formData.get("cpf_contratante"),
                endereco_contratante: formData.get("endereco_contratante"),
                telefone_contratante: formData.get("telefone_contratante"),
                email_contratante: formData.get("email_contratante"),
                tipo_evento: formData.get("tipo_evento"),
                observacao_evento: formData.get("observacao_evento") || "",
                data_evento: converterData(formData.get("data_evento")),
                horario_inicio: horario_inicio,
                horario_termino: horario_termino,
                qtd_mesas: parseInt(formData.get("qtd_mesas")),
                uso_piscina: formData.get("uso_piscina"),
                uso_som: formData.get("uso_som"),
                horario_entrega_bebidas: formData.get("horario_entrega_bebidas"),
                horario_recebimento_espaco: formData.get("horario_recebimento_espaco"),
                pula_pula: formData.get("pula_pula") === "true",
                piscina_bolinha: formData.get("piscina_bolinha") === "true",
                forma_pagamento_entrada: formData.get("forma_pagamento_entrada"),
                valor_pago: parseFloat(formData.get("valor_pago")) || 0,
                aceite_funcionamento: true,
                aceite_uso_espaco: true,
                aceite_obrigacoes_contratado: true,
                aceite_obrigacoes_contratante: true,
                aceite_cancelamento: true,
                aceite_gerais: true,
                aceite_final_contrato: true
            };

            // ✅ Validação
            if (!horario_inicio || !horario_termino) {
                alert("⚠️ Preencha os horários de início e término!");
                return;
            }

            console.log("📤 Enviando:", dados);

            // Envia para o servidor
            const resposta = await fetch("/salvar-contrato", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });

            const resultado = await resposta.json();
            console.log("📥 Resposta:", resultado);

            if (resultado.sucesso) {
                alert(`✅ ${resultado.mensagem}\nID: ${resultado.id_contrato}\nTotal: R$ ${resultado.valor_total}\nValor Pago: R$ ${dados.valor_pago}`);
                
                // 📄 Gera e baixa o contrato em PDF
                gerarPDF(dados, resultado);
                
                form.reset();
            } else {
                alert(`⚠️ ${resultado.mensagem}`);
            }

        } catch (erro) {
            console.error("❌ Erro:", erro);
            alert(`❌ Erro de conexão: ${erro.message || 'Não foi possível conectar ao servidor'}`);
        } finally {
            btn.disabled = false;
            btn.textContent = "✅ Salvar e Enviar Contrato";
        }
    });

    // Converte data
    function converterData(dataIso) {
        if (!dataIso) return "";
        const [ano, mes, dia] = dataIso.split("-");
        return `${dia}/${mes}/${ano}`;
    }

    // 📄 Gera PDF
    function gerarPDF(dados, res) {
        const dataHoje = new Date().toLocaleDateString('pt-BR');
        const valorRestante = (res.valor_total - dados.valor_pago).toFixed(2);
        
        const conteudo = `
====================================================================
                CONTRATO DE PRESTAÇÃO DE SERVIÇOS
               Espaço Comemore Festas e Eventos
====================================================================

CONTRATADO: Leandro Ruy Batista da Silva
CPF: 682.459.552-72
Endereço: Rua Isaura Parente, nº 100 - Rio Branco/AC
Telefone: (68) 99921-7686 / 99241-4341

--------------------------------------------------------------------

CONTRATANTE:
Nome: ${dados.nome_contratante}
CPF: ${dados.cpf_contratante}
Endereço: ${dados.endereco_contratante}
Telefone: ${dados.telefone_contratante}

--------------------------------------------------------------------

DADOS DO EVENTO:
Tipo: ${dados.tipo_evento}
Data: ${dados.data_evento}
Horário: ${dados.horario_inicio} às ${dados.horario_termino}
Mesas: ${dados.qtd_mesas}
Piscina: ${dados.uso_piscina}
Som: ${dados.uso_som}
Pula-Pula: ${dados.pula_pula ? 'SIM' : 'NÃO'}
Piscina de Bolinhas: ${dados.piscina_bolinha ? 'SIM' : 'NÃO'}

--------------------------------------------------------------------

VALORES:
Valor Total da Locação....: R$ ${res.valor_total}
Valor Pago pelo Cliente....: R$ ${dados.valor_pago.toFixed(2)}
Valor Restante a Pagar.....: R$ ${valorRestante}
Forma de Pagamento: ${dados.forma_pagamento_entrada}

--------------------------------------------------------------------

Declaro que li, conferi e concordo com todos os termos do contrato.

Rio Branco/AC, ${dataHoje}

__________________________________________________
Assinatura do Contratante

__________________________________________________
Assinatura do Contratado

====================================================================
Contrato nº ${res.id_contrato} - Gerado em ${dataHoje}
====================================================================
        `.trim();

        const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Contrato_${res.id_contrato}_${dados.data_evento.replace(/\//g,'-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        alert("✅ Contrato salvo com sucesso!\nO arquivo foi baixado no seu dispositivo!");
    }
});
