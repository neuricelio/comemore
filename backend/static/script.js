document.addEventListener("DOMContentLoaded", () => {
    // Cria o botão dinamicamente
    const botaoEnviar = document.createElement("button");
    botaoEnviar.id = "btnSalvar";
    botaoEnviar.textContent = "Salvar Contrato";
    document.body.appendChild(botaoEnviar);

    // Ação ao clicar
    botaoEnviar.addEventListener("click", async () => {
        const dados = {
            nome_contratante: "Liz Gardênia Pereira Braga",
            cpf_contratante: "033.823.732-11",
            endereco_contratante: "Rua Nabuco de Araujo 267, conjunto Esperança",
            telefone_contratante: "(68) 99932-1157",
            tipo_evento: "Festa Aniversário ADULTO",
            observacao_evento: "",
            data_evento: "05/07/2026",
            horario_inicio: "15:00",
            horario_termino: "22:00",
            qtd_mesas: 15,
            uso_piscina: "sim",
            uso_som: "sim",
            horario_entrega_bebidas: "15:00",
            horario_recebimento_espaco: "15:00",
            pula_pula: false,
            piscina_bolinha: false,
            forma_pagamento_entrada: "pix",
            aceite_funcionamento: true,
            aceite_uso_espaco: true,
            aceite_obrigacoes_contratado: true,
            aceite_obrigacoes_contratante: true,
            aceite_cancelamento: true,
            aceite_gerais: true,
            aceite_final_contrato: true
        };

        try {
            // ✅ Caminho relativo — funciona local e no Render
            const resposta = await fetch("/salvar-contrato", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });

            const resultado = await resposta.json();
            alert(resultado.mensagem || resultado.erro);

        } catch (erro) {
            alert("❌ Erro de conexão: " + erro.message);
        }
    });
});
