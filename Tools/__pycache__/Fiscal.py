import streamlit as st
import re

def render_removedor_caracteres():
    """
    Renderiza uma ferramenta rápida para limpar CNPJ, CPF, CEP, 
    Telefones ou Chaves de Acesso (NFe) para uso em ERPs.
    """
    st.subheader("🧹 Removedor de Pontos e Traços")
    st.markdown("Cole números formatados (CNPJ, CPF, Chave de NFe) para extrair apenas os dígitos e facilitar a colagem no ERP.")

    texto_bruto = st.text_area(
        "Insira o texto original aqui:", 
        placeholder="Ex: 12.345.678/0001-90 ou 3523 0112 3456...",
        key="removedor_input"
    )

    if st.button("Limpar Formatação", type="primary"):
        if texto_bruto:
            # O Regex '\D' encontra tudo que NÃO é número e remove
            texto_limpo = re.sub(r'\D', '', texto_bruto)
            
            if texto_limpo:
                st.success(f"✅ Encontrados {len(texto_limpo)} dígitos.")
                st.markdown("📋 **Clique no ícone de copiar no canto superior direito do bloco abaixo:**")
                st.code(texto_limpo, language="text")
            else:
                st.warning("Nenhum número foi encontrado no texto inserido.")
        else:
            st.warning("Por favor, insira algum texto para limpar.")


def render_simulador_impostos():
    """
    Renderiza um simulador básico de IPI e ICMS.
    Útil para o SAC entender a composição do valor final de uma nota de devolução.
    """
    st.subheader("🧮 Simulador de Impostos (IPI e ICMS)")
    st.markdown("Entenda rapidamente a composição de impostos de um item para auxiliar na conferência de Notas Fiscais ou dúvidas de clientes.")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_calculo = st.number_input(
            "Valor Base do Produto (R$)", 
            min_value=0.0, step=10.0, format="%.2f", key="tax_base"
        )
    with col2:
        aliquota_icms = st.number_input(
            "Alíquota ICMS (%)", 
            min_value=0.0, max_value=100.0, step=1.0, format="%.2f", key="tax_icms"
        )
    with col3:
        aliquota_ipi = st.number_input(
            "Alíquota IPI (%)", 
            min_value=0.0, max_value=100.0, step=1.0, format="%.2f", key="tax_ipi"
        )

    if st.button("Calcular Impostos", type="primary", use_container_width=True):
        if base_calculo > 0:
            # Cálculo padrão: ICMS geralmente está embutido na base (mas mostramos o valor nominal)
            # O IPI é somado por fora da base de cálculo para compor o Total da Nota.
            valor_icms = base_calculo * (aliquota_icms / 100)
            valor_ipi = base_calculo * (aliquota_ipi / 100)
            valor_total_nota = base_calculo + valor_ipi

            st.markdown("---")
            st.write("### 📊 Detalhamento da Operação")
            
            c_res1, c_res2, c_res3 = st.columns(3)
            c_res1.metric("Valor do ICMS", f"R$ {valor_icms:.2f}", help="Geralmente embutido no valor do produto")
            c_res2.metric("Valor do IPI", f"R$ {valor_ipi:.2f}", help="Somado por fora do valor do produto")
            c_res3.metric("Valor Total da NFe", f"R$ {valor_total_nota:.2f}", help="Base de Cálculo + Valor do IPI")

            st.info("💡 **Dica para o SAC:** Se o cliente questionar por que o valor da nota está maior que o preço do produto no site, geralmente a resposta é o **IPI**, que é somado ao final da operação.")
        else:
            st.warning("Insira o valor base do produto para realizar a simulação.")