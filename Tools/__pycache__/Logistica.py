import streamlit as st

def render_calculadora_pac_reverso():
    st.subheader("📦 Calculadora Estimativa de PAC Reverso (Sem API)")
    st.markdown("Estime o custo e viabilidade do PAC Reverso calculando o peso cubado e cruzando com uma matriz de tarifas médias regionais.")

    # 1. Entrada de Dados da Caixa
    col_dim1, col_dim2 = st.columns(2)
    with col_dim1:
        peso_fisico = st.number_input("Peso Físico Real (kg)", min_value=0.0, step=0.1, key="pac_peso")
        comprimento = st.number_input("Comprimento (cm)", min_value=0.0, step=1.0, key="pac_comp")
    with col_dim2:
        largura = st.number_input("Largura (cm)", min_value=0.0, step=1.0, key="pac_larg")
        altura = st.number_input("Altura (cm)", min_value=0.0, step=1.0, key="pac_alt")

    # Região de Destino/Origem do Cliente
    regiao_cliente = st.selectbox(
        "Destino/Origem do Cliente (Região):",
        ["São Paulo (Capital/Interior)", "Sudeste (RJ, MG, ES)", "Sul (PR, SC, RS)", "Centro-Oeste (MS, MT, GO, DF)", "Nordeste (BA, PE, CE, etc.)", "Norte (AM, PA, TO, etc.)"]
    )

    if st.button("Calcular Estimativa de Frete", type="primary", use_container_width=True):
        if peso_fisico > 0 and comprimento > 0 and largura > 0 and altura > 0:
            
            # --- VALIDAÇÃO DE LIMITES REAIS DOS CORREIOS ---
            soma_dimensoes = comprimento + largura + altura
            if comprimento > 100 or largura > 100 or altura > 100 or peso_fisico > 30 or soma_dimensoes > 200:
                st.error("❌ **NÃO SEGUE POR CORREIOS!** O pacote ultrapassa os limites permitidos pelo PAC (Máx: 30kg, 100cm por lado ou 200cm na soma total). **Acione coleta por Transportadora.**")
                return

            # --- CÁLCULO DE CUBAGEM ---
            # Fórmula padrão Correios: (C x L x A) / 6000
            peso_cubado = (comprimento * largura * altura) / 6000
            
            # Regra de cobrança dos Correios:
            # Se o peso cubado for menor ou igual a 5kg, considera-se o peso físico.
            # Se for maior que 5kg, vale o maior entre peso físico e cubado.
            if peso_cubado <= 5.0:
                peso_considerado = peso_fisico
            else:
                peso_considerado = max(peso_fisico, peso_cubado)

            # --- MATRIZ INTELIGENTE DE TARIFAS (Valores médios aproximados de mercado para e-commerce) ---
            # Estrutura: {Região: [Preço até 1kg, Preço até 5kg, Preço até 15kg, Preço até 30kg]}
            matriz_tarifas = {
                "São Paulo (Capital/Interior)": [15.50, 22.00, 38.00, 55.00],
                "Sudeste (RJ, MG, ES)": [24.00, 32.50, 54.00, 78.00],
                "Sul (PR, SC, RS)": [26.00, 36.00, 59.00, 88.00],
                "Centro-Oeste (MS, MT, GO, DF)": [29.00, 42.00, 68.00, 98.00],
                "Nordeste (BA, PE, CE, etc.)": [36.00, 55.00, 92.00, 140.00],
                "Norte (AM, PA, TO, etc.)": [42.00, 68.00, 120.00, 185.00]
            }

            # Identificar a faixa de preço por peso considerado
            faixas = matriz_tarifas[regiao_cliente]
            if peso_considerado <= 1.0:
                custo_estimado = faixas[0]
            elif peso_considerado <= 5.0:
                custo_estimado = faixas[1]
            elif peso_considerado <= 15.0:
                custo_estimado = faixas[2]
            else:
                custo_estimado = faixas[3]

            # --- EXIBIÇÃO DOS RESULTADOS ---
            st.markdown("---")
            col_res1, col_res2, col_res3 = st.columns(3)
            
            col_res1.metric("Peso Cubado", f"{peso_cubado:.2f} kg")
            col_res2.metric("Peso Precificado", f"{peso_considerado:.2f} kg", help="Maior valor entre físico e cubado (aplicando regra de corte de 5kg)")
            col_res3.metric("Custo Estimado", f"R$ {custo_estimado:.2f}")

            st.success("✅ **Viável por PAC Reverso.** O pacote atende aos requisitos operacionais dos Correios.")
            
            # UX para o setor de decoração (ex: espelhos, vasos)
            if peso_cubado > peso_fisico * 1.5:
                st.warning("⚠️ **Alerta de Volumetria:** Esta peça ocupa muito espaço para o peso que tem (caixa grande com muito vento/plástico bolha). O frete ficou mais caro devido ao tamanho da caixa.")
        else:
            st.warning("Preencha todas as dimensões e peso com valores maiores que zero.")