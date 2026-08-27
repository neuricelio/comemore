// =========================================================
// ✅ VARIÁVEIS GLOBAIS
// =========================================================
const campoEmail = document.getElementById('email_contratante');
const campoReplyto = document.getElementById('campo_email_resposta');
const campoCopia = document.getElementById('campo_copia_cliente');
const form = document.getElementById('formContrato');
const statusDiv = document.getElementById('mensagem-status');

// =========================================================
// ✅ PREENCHE E-MAIL DE RESPOSTA E CÓPIA AUTOMATICAMENTE
// =========================================================
if (campoEmail && campoReplyto && campoCopia) {
    campoEmail.addEventListener('input', function () {
        campoReplyto.value = this.value;
        campoCopia.value = this.value;
    });
}

// =========================================================
// ✅ HORÁRIOS PERSONALIZADOS
// =========================================================
function mostrarHorariosPersonalizados() {
    const select = document.getElementById('horario_tipo');
    const div = document.getElementById('horarios_personalizados');
    const hInicio = document.getElementById('horario_inicio_personalizado');
    const hTermino = document.getElementById('horario_termino_personalizado');

    if (select && div) {
        if (select.value === 'outros') {
            div.style.display = 'block';
            if (hInicio) hInicio.required = true;
            if (hTermino) hTermino.required = true;
        } else {
            div.style.display = 'none';
            if (hInicio) { hInicio.required = false; hInicio.value = ''; }
            if (hTermino) { hTermino.required = false; hTermino.value = ''; }
        }
    }
}

// =========================================================
// ✅ PROMOÇÃO — marca/desmarca itens juntos
// =========================================================
function atualizarPromocao() {
    const promocao = document.getElementById('chk_promocao');
    const pula = document.getElementById('chk_pula_pula');
    const bolinha = document.getElementById('chk_piscina_bolinha');

    if (promocao && pula && bolinha) {
        if (promocao.checked) {
            pula.checked = true;
            bolinha.checked = true;
            pula.disabled = true;
            bolinha.disabled = true;
        } else {
            pula.checked = false;
            bolinha.checked = false;
            pula.disabled = false;
            bolinha.disabled = false;
        }
    }
}

// =========================================================
// ✅ MÁSCARA PARA CPF — 000.000.000-00
// =========================================================
function aplicarMascaraCPF(valor) {
    valor = valor.replace(/\D/g, '');
    if (valor.length <= 3) return valor;
    if (valor.length <= 6) return `${valor.slice(0, 3)}.${valor.slice(3)}`;
    if (valor.length <= 9) return `${valor.slice(0, 3)}.${valor.slice(3, 6)}.${valor.slice(6)}`;
    return `${valor.slice(0, 3)}.${valor.slice(3, 6)}.${valor.slice(6, 9)}-${valor.slice(9, 11)}`;
}

// =========================================================
// ✅ MÁSCARA PARA TELEFONE — (00) 00000-0000
// =========================================================
function aplicarMascaraTelefone(valor) {
    valor = valor.replace(/\D/g, '');
    if (valor.length <= 2) return `(${valor}`;
    if (valor.length <= 7) return `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
    return `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7, 11)}`;
}

// =========================================================
// ✅ CONVERSÃO DE DATA ISO → BR
// =========================================================
function converterData(dataIso) {
    if (!dataIso) return "";
    const [ano, mes, dia] = dataIso.split("-");
    return `${dia}/${mes}/${ano}`;
}

// =========================================================
// ✅ GERA ARQUIVO DE CONTRATO (.txt)
// =========================================================
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
    a.download = `Contrato_${res.id_contrato}_${dados.data_evento.replace(/\//g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// =========================================================
// ✅ INICIALIZAÇÃO GERAL AO CARREGAR PÁGINA
// =========================================================
document.addEventListener("DOMContentLoaded", () => {

    const campoCPF = document.getElementById('cpf_contratante');
    const campoTel = document.getElementById('telefone_contratante');
    const campoNome = document.getElementById('nome_contratante');
    const selectHorario = document.getElementById('horario_tipo');
    const chkPromocao = document.getElementById('chk_promocao');
    const aceiteFinal = document.getElementById('aceite_final_contrato');
    // =========================================================
    // ✅ ÚLTIMA DECLARAÇÃO — Marca TODOS os checkbox ao clicar
    // =========================================================
    if (aceiteFinal) {
        aceiteFinal.addEventListener('change', function () {
            const marcar = this.checked;
            
            // Seleciona TODOS os checkbox do formulário
            const todosCheckbox = form.querySelectorAll('input[type="checkbox"]');
            
            todosCheckbox.forEach(checkbox => {
                // Não altera a própria última declaração (ela controla)
                if (checkbox.id !== 'aceite_final_contrato') {
                    checkbox.checked = marcar;
                    // Se tiver promoção, mantém regra especial
                    if (checkbox.id === 'chk_pula_pula' || checkbox.id === 'chk_piscina_bolinha') {
                        const promocao = document.getElementById('chk_promocao');
                        if (promocao && promocao.checked) {
                            checkbox.checked = true;
                            checkbox.disabled = true;
                        }
                    }
                }
            });
        });
    }
    // Marca a declaração final se TODOS os outros estiverem marcados
    form.addEventListener('change', function (e) {
        if (e.target.type === 'checkbox' && e.target.id !== 'aceite_final_contrato') {
            const todos = form.querySelectorAll('input[type="checkbox"]:checked');
            const total = form.querySelectorAll('input[type="checkbox"]').length - 1; // -1 = exclui o final
            if (todos.length === total && aceiteFinal) {
                aceiteFinal.checked = true;
            } else if (aceiteFinal && e.target.checked === false) {
                aceiteFinal.checked = false;
            }
        }
    });    
    // ✅ MÁSCARA CPF
    if (campoCPF) {
        campoCPF.addEventListener('input', e => {
            e.target.value = aplicarMascaraCPF(e.target.value);
        });
    }

    // ✅ MÁSCARA TELEFONE
    if (campoTel) {
        campoTel.addEventListener('input', e => {
            e.target.value = aplicarMascaraTelefone(e.target.value);
        });
    }

    // ✅ NOME — Cada palavra com inicial maiúscula
    if (campoNome) {
        campoNome.addEventListener('input', e => {
            e.target.value = e.target.value
                .split(' ')
                .map(palavra => palavra.length ? palavra[0].toUpperCase() + palavra.slice(1).toLowerCase() : '')
                .join(' ');
        });
    }

    // ⚠️ CAMPO ENDEREÇO — SEM NENHUMA MÁSCARA / SEM FORMATAÇÃO
    // O cliente digita livremente — espaços preservados!

    // ✅ Inicializa horários e promoção
    if (selectHorario) {
        selectHorario.addEventListener('change', mostrarHorariosPersonalizados);
        mostrarHorariosPersonalizados();
    }
    if (chkPromocao) {
        chkPromocao.addEventListener('change', atualizarPromocao);
    }

    // ✅ Mensagem de sucesso ao voltar do redirecionamento
    if (window.location.search.includes('sucesso=1') && statusDiv) {
        statusDiv.style.display = 'block';
        statusDiv.style.background = '#dcfce7';
        statusDiv.style.color = '#166534';
        statusDiv.innerHTML = '✅ <strong>Contrato enviado com sucesso!</strong><br>Verifique seu e-mail e também a caixa de spam/lixo eletrônico.';
        history.replaceState({}, document.title, window.location.pathname);
    }

    // =========================================================
    // ✅ ENVIO DO FORMULÁRIO — SEM fetch → ACABA O ERRO!
    // =========================================================
    if (form) {
        form.addEventListener("submit", (e) => {
            const btn = document.getElementById("btnSalvar");
            if (btn) {
                btn.disabled = true;
                btn.textContent = "Enviando...";
            }

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
                    horario_inicio = formData.get("horario_inicio_personalizado");
                    horario_termino = formData.get("horario_termino_personalizado");
                }

                // ✅ Validação de horários ANTES de enviar
                if (!horario_inicio || !horario_termino) {
                    alert("⚠️ Preencha os horários de início e término!");
                    if (btn) { btn.disabled = false; btn.textContent = "✅ Salvar e Enviar Contrato"; }
                    e.preventDefault();
                    return;
                }

                // ✅ Reúne os dados para gerar o contrato
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
                    valor_pago: parseFloat(formData.get("valor_pago")) || 0
                };

                // ✅ Cálculo de valores
                const valorMesas = { "15": 0, "20": 60, "25": 120 }[dados.qtd_mesas] || 0;
                const valorPula = dados.pula_pula ? 110 : 0;
                const valorBolinha = dados.piscina_bolinha ? 110 : 0;
                const somMicrofone = dados.uso_som === "sim_microfone" ? 30 : 0;
                const promocao = dados.pula_pula && dados.piscina_bolinha ? 20 : 0;
                const valorTotal = (valorMesas + valorPula + valorBolinha + somMicrofone - promocao).toFixed(2);

                const resultado = {
                    id_contrato: Date.now(),
                    valor_total: valorTotal
                };

                // 📄 GERA E BAIXA O CONTRATO ANTES DE ENVIAR
                gerarPDF(dados, resultado);

                // ✅ MOSTRA MENSAGEM DE SUCESSO APÓS ENVIO
                setTimeout(() => {
                    alert(`✅ Contrato enviado!\nID: ${resultado.id_contrato}\nTotal: R$ ${valorTotal}\nVerifique seu e-mail (caixa de spam também).`);
                    if (statusDiv) {
                        statusDiv.style.display = 'block';
                        statusDiv.style.background = '#dcfce7';
                        statusDiv.style.color = '#166534';
                        statusDiv.innerHTML = '✅ <strong>Contrato enviado com sucesso!</strong><br>Verifique seu e-mail e também a caixa de spam/lixo eletrônico.';
                    }
                    form.reset();
                    if (btn) { btn.disabled = false; btn.textContent = "✅ Salvar e Enviar Contrato"; }
                }, 800);

                // ✅ DEIXA O FORMULÁRIO ENVIAR DIRETO AO FORMSPREE — SEM fetch()!
                // Removemos e.preventDefault() → o formulário envia naturalmente!

            } catch (erro) {
                console.error("❌ Erro:", erro);
                alert(`⚠️ Verifique se todos os campos estão preenchidos!`);
                if (btn) { btn.disabled = false; btn.textContent = "✅ Salvar e Enviar Contrato"; }
                e.preventDefault();
            }
        });
    }
});
