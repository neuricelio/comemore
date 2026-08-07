document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formContrato");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const btn = document.getElementById("btnSalvar");
        btn.disabled = true;
        btn.textContent = "Enviando...";

        try {
            // Coleta TODOS os dados preenchidos automaticamente
            const formData = new FormData(form);

            // Converte para objeto
            const dados = {
                nome_contratante: formData.get("nome_contratante"),
                cpf_contratante: formData.get("cpf_contratante"),
                endereco_contratante: formData.get("endereco_contratante"),
                telefone_contratante: formData.get("telefone_contratante"),
                tipo_evento: formData.get("tipo_evento"),
                observacao_evento: formData.get("observacao_evento") || "",
                data_evento: converterData(formData.get("data_evento")),
                horario_inicio: formData.get("horario_inicio"),
                horario_termino: formData.get("horario_termino"),
                qtd_mesas: parseInt(formData.get("qtd_mesas")),
                uso_piscina: formData.get("uso_piscina"),
                uso_som: formData.get("uso_som"),
                horario_entrega_bebidas: formData.get("horario_entrega_bebidas"),
                horario_recebimento_espaco: formData.get("horario_recebimento_espaco"),
                pula_pula: formData.get("pula_pula") === "true",
                piscina_bolinha: formData.get("piscina_bolinha") === "true",
                forma_pagamento_entrada: formData.get("forma_pagamento_entrada"),
                aceite_funcionamento: !!formData.get("aceite_funcionamento"),
                aceite_uso_espaco: !!formData.get("aceite_uso_espaco"),
                aceite_obrigacoes_contratado: !!formData.get("aceite_obrigacoes_contratado"),
                aceite_obrigacoes_contratante: !!formData.get("aceite_obrigacoes_contratante"),
                aceite_cancelamento: !!formData.get("aceite_cancelamento"),
                aceite_gerais: !!formData.get("aceite_gerais"),
                aceite_final_contrato: !!formData.get("aceite_final_contrato")
            };

            // Envia para o servidor
            const resposta = await fetch("/salvar-contrato", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });

            const resultado = await resposta.json();

            if (resultado.sucesso) {
                alert(`✅ ${resultado.mensagem}\nID do Contrato: ${resultado.id_contrato}\nValor Total: R$ ${resultado.valor_total}`);
                form.reset();
            } else {
                alert(`⚠️ ${resultado.mensagem}`);
            }

        } catch (erro) {
            alert(`❌ Erro: ${erro.message}\nVerifique sua conexão e tente novamente.`);
        } finally {
            btn.disabled = false;
            btn.textContent = "✅ Salvar e Enviar Contrato";
        }
    });

    // Converte data do formato HTML (YYYY-MM-DD) para DD/MM/YYYY
    function converterData(dataIso) {
        if (!dataIso) return "";
        const [ano, mes, dia] = dataIso.split("-");
        return `${dia}/${mes}/${ano}`;
    }
});
