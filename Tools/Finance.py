import streamlit as st
import streamlit.components.v1 as components


def render_calculadora_desconto():
    """
    Renderiza a ferramenta de cálculo de descontos para avarias,
    com validação de teto (30%) e geração de texto para o client.
    """
    st.subheader("📉 Calculadora de Desconto (Avarias)")
    st.markdown("Calcule rapidamente o valor do reembolso. Lembre-se: o limite recomendado é de **30%**.")

    # Uso do parâmetro 'key' para evitar conflitos de variáveis no Streamlit
    valor_item = st.number_input("Valor Original do Item (R$)", min_value=0.0, step=10.0, format="%.2f", key="calc_desc_valor")

    st.write("Selecione a porcentagem do desconto:")
    pct_escolhida = st.radio(
        "Porcentagem", 
        [5, 10, 15, 20, 25, 30, "Personalizado"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

    if pct_escolhida == "Personalizado":
        pct_calc = st.number_input("Digite a %", min_value=0.0, max_value=100.0, step=1.0, key="calc_desc_pct")
    else:
        pct_calc = float(pct_escolhida)

    if st.button("Calcular Desconto", type="primary", use_container_width=True):
        if valor_item > 0:
            desconto_reais = valor_item * (pct_calc / 100)
            valor_final = valor_item - desconto_reais
        

            # Exibição visual com colunas e métricas nativas
            col1, col2 = st.columns(2)
            col1.metric("Valor a Reembolsar (Cliente)", f"R$ {desconto_reais:.2f}")
            col2.metric("Valor Líquido (Retido)", f"R$ {valor_final:.2f}")


            # Validação da Regra de Negócio (Teto de 30%)
            if pct_calc > 30:
                st.error("⚠️ **Atenção:** O desconto supera o teto de 30%. Avalie se a devolução completa não é mais viável para a empresa.")
            else:
                st.success("✅ Desconto dentro da margem permitida.")

            # UX: Texto pronto para o operador ganhar tempo no atendimento
            st.markdown("📋 **Copie para enviar ao cliente:**")
            texto_copia = f"Olá! Analisamos o seu caso. Como forma de compensação pela avaria, estamos disponibilizando um desconto de {pct_calc}%. O valor a ser reembolsado será de R$ {desconto_reais:.2f}, e o valor final do seu item passa a ser R$ {valor_final:.2f}. Podemos seguir com o acordo?"
            st.code(texto_copia, language="text")
        else:
            st.warning("Insira um valor maior que zero para calcular.")


def render_viabilidade_conserto():
    """
    Renderiza a ferramenta que cruza o valor do item com o orçamento 
    de conserto para decidir se o reparo é viável (limite de 50%).
    """
    st.subheader("🛠️ Avaliação: Devolver ou Consertar?")
    st.markdown("Descubra se vale a pena aprovar um orçamento de conserto (como vidraçarias para espelhos) ou seguir com o descarte/devolução.")

    col1, col2 = st.columns(2)
    with col1:
        valor_item = st.number_input("Valor Original do Item (R$)", min_value=0.0, step=50.0, format="%.2f", key="viab_valor_item")
    with col2:
        valor_orcamento = st.number_input("Valor do Orçamento (R$)", min_value=0.0, step=50.0, format="%.2f", key="viab_valor_orcamento")

    if st.button("Analisar Viabilidade", type="primary", use_container_width=True):
        if valor_item > 0 and valor_orcamento > 0:
            percentual = (valor_orcamento / valor_item) * 100
            
            st.markdown("---")
            st.write(f"**Impacto do Conserto:** {percentual:.1f}% do valor total do item.")

            # Validação da Regra de Negócio (Teto de 50%)
            if percentual > 50:
                st.error(f"🔴 **NÃO COMPENSA.** O orçamento ultrapassou o limite de 50%. A recomendação do sistema é seguir com a devolução ou descarte do item.")
            else:
                st.success(f"🟢 **COMPENSA CONSERTAR.** O orçamento está dentro da margem aceitável. É financeiramente melhor consertar do que perder o item inteiro.")
        else:
            st.warning("Preencha ambos os valores com números maiores que zero.")