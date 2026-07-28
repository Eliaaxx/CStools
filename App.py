import streamlit as st
import pandas as pd
import os
import re
import datetime
import requests

from users import USUARIOS

# ==========================================
# IDENTIDADE VISUAL & CSS CUSTOMIZADO
# ==========================================
st.set_page_config(page_title="CSTools - SAC", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #2A3B37 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    .stButton>button {
        background-color: #2A3B37 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #3d544f !important;
        color: #FFFFFF !important;
    }
    h1, h2, h3 {
        color: #2A3B37 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização de Estados do Sistema
if "logado" not in st.session_state:
    st.session_state.logado = False
if "tema" not in st.session_state:
    st.session_state.tema = "Escuro"

def aplicar_tema():
    if st.session_state.tema == "Escuro":
        bg_sidebar = "#2A3B37"
        text_color = "#FFFFFF"
        btn_bg = "#2A3B37"
        h_color = "#2A3B37"
    else:
        bg_sidebar = "#F0F2F6"
        text_color = "#999999"
        btn_bg = "#E0E0E0"
        h_color = "#999999"

    st.markdown(f"""
        <style>
        [data-testid="stSidebar"] {{ background-color: {bg_sidebar} !important; }}
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{ color: {text_color} !important; }}
        .stButton>button {{ background-color: {btn_bg} !important; color: {text_color} !important; }}
        h1, h2, h3 {{ color: {h_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

aplicar_tema()

# ==========================================
# FUNÇÕES MODULARES DAS FERRAMENTAS
# ==========================================
# --- DASHBOARD DE CLIMA (LOGÍSTICA PREVENTIVA) ---
# --- DASHBOARD DE CLIMA (LOGÍSTICA PREVENTIVA) ---
@st.cache_data(ttl=3600) # Atualização de 1 hora
def buscar_dados_clima():
    # Coordenadas geográficas dos estados brasileiros
    ESTADOS_BR = {
        "AC": {"lat": -9.974, "lon": -67.807}, "AL": {"lat": -9.665, "lon": -35.735},
        "AP": {"lat": 0.034, "lon": -51.066}, "AM": {"lat": -3.101, "lon": -60.025},
        "BA": {"lat": -12.971, "lon": -38.510}, "CE": {"lat": -3.717, "lon": -38.543},
        "DF": {"lat": -15.779, "lon": -47.929}, "ES": {"lat": -20.315, "lon": -40.312},
        "GO": {"lat": -16.686, "lon": -49.264}, "MA": {"lat": -2.529, "lon": -44.302},
        "MT": {"lat": -15.596, "lon": -56.096}, "MS": {"lat": -20.442, "lon": -54.646},
        "MG": {"lat": -19.920, "lon": -43.937}, "PA": {"lat": -1.455, "lon": -48.502},
        "PB": {"lat": -7.115, "lon": -34.863}, "PR": {"lat": -25.428, "lon": -49.273},
        "PE": {"lat": -8.047, "lon": -34.877}, "PI": {"lat": -5.089, "lon": -42.801},
        "RJ": {"lat": -22.906, "lon": -43.172}, "RN": {"lat": -5.794, "lon": -35.211},
        "RS": {"lat": -30.027, "lon": -51.228}, "RO": {"lat": -8.761, "lon": -63.903},
        "RR": {"lat": 2.819, "lon": -60.671}, "SC": {"lat": -27.596, "lon": -48.549},
        "SP": {"lat": -23.548, "lon": -46.636}, "SE": {"lat": -10.947, "lon": -37.073},
        "TO": {"lat": -10.184, "lon": -48.333}
    }
    
    # Formata a URL para consultar todos os dados relevantes na mesma requisição
    lats = ",".join([str(v["lat"]) for v in ESTADOS_BR.values()])
    lons = ",".join([str(v["lon"]) for v in ESTADOS_BR.values()])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&daily=precipitation_sum,wind_gusts_10m_max,weather_code,precipitation_probability_max&timezone=America%2FSao_Paulo&forecast_days=1"
    
    try:
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
        
        resultados = []
        estados_siglas = list(ESTADOS_BR.keys())
        
        for i, info in enumerate(dados):
            diario = info.get("daily", {})
            
            # Extração segura das variáveis
            chuva = float(diario.get("precipitation_sum", [0])[0] or 0.0)
            vento = float(diario.get("wind_gusts_10m_max", [0])[0] or 0.0)
            wcode = int(diario.get("weather_code", [0])[0] or 0)
            prob_chuva = int(diario.get("precipitation_probability_max", [0])[0] or 0)
            
            # --- 1. Classificação da Chance de Chuva ---
            if prob_chuva >= 70:
                chance_texto = "Chance alta"
            elif prob_chuva >= 30:
                chance_texto = "Chance média"
            else:
                chance_texto = "Chance baixa"

            # --- 2. Análise de Risco Operacional ---
            risco_chuva = 0
            motivo_chuva = ""
            if chuva > 50:
                risco_chuva = 2
                motivo_chuva = "chuva alta"
            elif chuva > 20:
                risco_chuva = 1
                motivo_chuva = "chuva moderada"
            
            risco_vento = 0
            motivo_vento = ""
            if vento > 80:
                risco_vento = 2
                motivo_vento = "rajada forte"
            elif vento > 50:
                risco_vento = 1
                motivo_vento = "vento forte"
                
            risco_wcode = 0
            motivo_wcode = ""
            # Códigos WMO Severos: 95,96,99 (Tempestades). 65,67,82 (Chuvas Intensas).
            if wcode in [95, 96, 99]:
                risco_wcode = 2
                motivo_wcode = "tempestade"
            elif wcode in [65, 67, 82]:
                risco_wcode = 1
                motivo_wcode = "clima severo"

            # --- 3. Definição do Nível Final ---
            risco_max = max(risco_chuva, risco_vento, risco_wcode)
            
            if risco_max == 2:
                cor = "#FF0000" # Vermelho
                risco_nome = "ALTO"
            elif risco_max == 1:
                cor = "#FFA500" # Laranja
                risco_nome = "MÉDIO"
            elif chuva > 5 or vento > 35 or prob_chuva > 60:
                cor = "#FFFF00" # Amarelo
                risco_nome = "BAIXO"
            else:
                cor = "#00FF00" # Verde
                risco_nome = "MÍNIMO"
                
            # --- 4. Construção da Coluna "Motivo" ---
            motivos_lista = [m for m in [motivo_chuva, motivo_vento, motivo_wcode] if m]
            if not motivos_lista:
                motivo_final = "Condições Normais"
            else:
                motivo_final = " + ".join(motivos_lista)

            # Tamanho da bolha no mapa considerando os novos fatores
            tamanho_bolha = max(chuva * 80, vento * 25, 500)
            
            estado = estados_siglas[i]
            resultados.append({
                "Estado": estado,
                "Precipitação (mm)": chuva,
                "Probabilidade (%)": prob_chuva,
                "Chuva": chance_texto,
                "Rajada (km/h)": vento,
                "Nível de Risco": risco_nome,
                "Motivo": motivo_final,
                "latitude": ESTADOS_BR[estado]["lat"],
                "longitude": ESTADOS_BR[estado]["lon"],
                "cor": cor,
                "tamanho": tamanho_bolha
            })
            
        return pd.DataFrame(resultados)
    except Exception as e:
        return pd.DataFrame()

def render_dashboard_inicio():
    st.title("🏠 Início - Dashboard Operacional")
    st.markdown("Acompanhe zonas de risco meteorológico para antecipar atrasos logísticos.")
    st.markdown("---")
    
    with st.spinner("Atualizando radares meteorológicos..."):
        df_clima = buscar_dados_clima()
        
    if not df_clima.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Mapa Indicador de Risco Climatico")
            st.map(df_clima, latitude="latitude", longitude="longitude", size="tamanho", color="cor")
            
        with col2:
            st.subheader("🚨 Ranking de Riscos Hoje")
            # Ordena com base na gravidade do alerta antes do volume de chuva
            ordem_risco = {"ALTO": 4, "MÉDIO": 3, "BAIXO": 2, "MÍNIMO": 1}
            df_clima["Peso"] = df_clima["Nível de Risco"].map(ordem_risco)
            df_ranking = df_clima.sort_values(by=["Peso", "Precipitação (mm)"], ascending=[False, False]).head(5)
            
            # Tabela atualizada com o motivo e a chance de chuva
            st.dataframe(
                df_ranking[["Estado", "Nível de Risco", "Motivo", "Chuva"]], 
                hide_index=True, 
                use_container_width=True
            )
            # Mensagem mais curta e acionável
            st.info("💡 **Dica:** Estados em vermelho exigem acompanhamento imediato.")

        st.markdown("---")
        st.subheader("📊 Indicadores de Chuva por Estado")
        
        # Gráficos divididos lado a lado para não misturar escalas (mm vs %)
        dados_grafico = df_clima.sort_values(by="Precipitação (mm)", ascending=True).set_index("Estado")
        
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.markdown("**Volume Estimado (mm)**")
            st.bar_chart(dados_grafico["Precipitação (mm)"])
            
        with col_graf2:
            st.markdown("**Probabilidade de Ocorrência (%)**")
            st.bar_chart(dados_grafico["Probabilidade (%)"], color="#1f77b4")
            
    else:
        st.error("Não foi possível carregar os dados climáticos. Verifique sua conexão.")

# --- MÓDULO FISCAL ---
def render_removedor_caracteres():
    st.subheader("🧹 Removedor de Pontos e Traços")
    st.markdown("Cole números formatados (CNPJ, CPF, Chave de NFe) para extrair apenas os dígitos.")
    
    texto_bruto = st.text_area(
        "Insira o texto original aqui:", 
        placeholder="Ex: 12.345.678/0001-90",
        key="removedor_input"
    )
    if st.button("Limpar Formatação", type="primary"):
        if texto_bruto:
            texto_limpo = re.sub(r'\D', '', texto_bruto)
            if texto_limpo:
                st.success(f"✅ Encontrados {len(texto_limpo)} dígitos.")
                st.code(texto_limpo, language="text")
            else:
                st.warning("Nenhum número foi encontrado no texto.")
        else:
            st.warning("Por favor, insira algum texto.")

def render_simulador_impostos():
    st.subheader("🧮 Simulador de Impostos (IPI e ICMS)")
    col1, col2, col3 = st.columns(3)
    with col1:
        base_calculo = st.number_input("Valor Base do Produto (R$)", min_value=0.0, step=10.0, format="%.2f", key="tax_base")
    with col2:
        aliquota_icms = st.number_input("Alíquota ICMS (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f", key="tax_icms")
    with col3:
        aliquota_ipi = st.number_input("Alíquota IPI (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f", key="tax_ipi")

    if st.button("Calcular Impostos", type="primary", use_container_width=True):
        if base_calculo > 0:
            valor_icms = base_calculo * (aliquota_icms / 100)
            valor_ipi = base_calculo * (aliquota_ipi / 100)
            valor_total_nota = base_calculo + valor_ipi
            
            st.markdown("---")
            c_res1, c_res2, c_res3 = st.columns(3)
            c_res1.metric("Valor do ICMS", f"R$ {valor_icms:.2f}")
            c_res2.metric("Valor do IPI", f"R$ {valor_ipi:.2f}")
            c_res3.metric("Valor Total da NFe", f"R$ {valor_total_nota:.2f}")
        else:
            st.warning("Insira o valor base.")

# --- MÓDULO LOGISTICO ---
def render_calculadora_pac_reverso():
    st.subheader("📦 Calculadora Estimativa de PAC Reverso")
    st.info("💡 **Dica:** Quanto mais pesado, maior o custo.")
    st.markdown("Estime o custo do PAC Reverso entre os estados.")

    DESTINO_FIXO = {
        "endereco": "Estrada Velha Guarulhos São Miguel, 3241",
        "bairro": "Jardim Arapongas",
        "cep": "07210-250",
        "municipio": "Guarulhos",
        "uf": "SP"
    }

    with st.expander("🏢 Endereço de Destino (Central de Recebimento)", expanded=False):
        st.markdown(f"""
        **Logradouro:** {DESTINO_FIXO['endereco']}  
        **Bairro:** {DESTINO_FIXO['bairro']} | **CEP:** {DESTINO_FIXO['cep']}  
        **Cidade/UF:** {DESTINO_FIXO['municipio']} - {DESTINO_FIXO['uf']}
        """)

    st.markdown("### 📥 Dados do Pacote e Origem")
    col_dim1, col_dim2 = st.columns(2)
    with col_dim1:
        peso_fisico = st.number_input("Peso Físico Real (kg)", min_value=0.0, step=0.1, key="pac_peso")
        # Alterado para aceitar Metros (m) mantendo a formatação e limite livre
        comprimento_m = st.number_input("Comprimento (m)", min_value=0.0, step=0.01, format="%.2f", key="pac_comp")
    with col_dim2:
        largura_m = st.number_input("Largura (m)", min_value=0.0, step=0.01, format="%.2f", key="pac_larg")
        altura_m = st.number_input("Altura (m)", min_value=0.0, step=0.01, format="%.2f", key="pac_alt")

    regiao_origem = st.selectbox(
        "Origem do Cliente (De onde o pacote está vindo?):",
    ["SP (Capital)", "SP (Interior)", "RJ", "MG", "ES", "PR", "SC", "RS", "MS", "MT", "GO", "DF", "BA", "AL", "PB", "PE", "CE", "AM", "PA", "TO", "MA", "PI", "RN", "SE", "RO", "RR", "AC", "AP"]
    )

    if st.button("Calcular Estimativa", type="primary", use_container_width=True):
        if peso_fisico > 0 and comprimento_m > 0 and largura_m > 0 and altura_m > 0:
            
            # Conversão invisível para CM para manter a regra rigorosa dos Correios funcionando sem erros matemáticos
            comprimento = comprimento_m * 100
            largura = largura_m * 100
            altura = altura_m * 100
            
            soma_dimensoes = comprimento + largura + altura
            if comprimento > 100 or largura > 100 or altura > 100 or peso_fisico > 30 or soma_dimensoes > 200:
                st.error("❌ **NÃO SEGUE POR CORREIOS!** O pacote ultrapassa os limites permitidos pelo PAC (Máx: 30kg, 1m por lado ou 2m na soma total). **Acione coleta por Transportadora.**")
                return
            st.info("💡 **Dica:** Após o resultado, arredonde mentalmente para mais 5 reais e para menos 5 reais.")
            peso_cubado = (comprimento * largura * altura) / 6000
            
            if peso_cubado <= 5.0 or peso_cubado <= 10.0:
                peso_considerado = peso_fisico
            else:
                peso_considerado = max(peso_fisico, peso_cubado)
            # Estrutura: {Região: [Preço até 1kg, Preço até 5kg, Preço até 15kg, Preço até 30kg]}
            matriz_tarifas = {
                "SP (Capital)": [25.80, 35.50, 80.50, 120.40],
                "SP (Interior)": [35.80, 54.90, 118.90, 130.80],
                "RJ": [30.50, 82.60, 159.10, 150.90],
                "MG": [30.50, 82.60, 159.10, 246.79],
                "ES": [30.50, 90.50, 159.10, 256.50],
                "PR": [30.50, 45.50, 132.90, 225.60],
                "SC": [30.50, 55.50, 159.10, 235.60],
                "RS": [34.50, 55.60, 159.10, 235.60],
                "MS": [30.50, 51.10, 132.90, 225.30],
                "MT": [45.50, 68.10, 188.40, 270.20],
                "GO": [45.50, 68.10, 188.40, 280.20],
                "DF": [40.50, 51.10, 170.30, 267.30],
                "BA": [45.50, 68.10, 174.70, 380.20],
                "AL": [45.50, 81.70, 192.70, 380.20],
                "PB": [54.70, 67.50, 126.70, 380.20],
                "PE": [45.50, 55.00, 92.00, 380.20],
                "CE": [45.50, 55.00, 92.00, 380.20],
                "AM": [54.70, 230.30, 280.10, 462.70]
            }

            faixas = matriz_tarifas[regiao_origem]
            if peso_considerado <= 1.0:
                custo_estimado = faixas[1]
            elif peso_considerado <= 15.0:
                custo_estimado = faixas[2]
            else:
                custo_estimado = faixas[3]

            st.markdown("---")
            col_res1, col_res2, col_res3 = st.columns(3)
            
            col_res1.metric("Peso Cubado", f"{peso_cubado:.2f} kg")
            col_res2.metric("Peso Precificado", f"{peso_considerado:.2f} kg")
            col_res3.metric("Média do Custo Estimado", f"R$ {custo_estimado:.2f}")

            st.success("✅ **PAC Reverso Viável.** Dados de postagem gerados com sucesso:")
            
            st.markdown("📋 **Dados de Destinatário**")
            texto_etiqueta = (
                f"DESTINATÁRIO:\n"
                f"Endereço: {DESTINO_FIXO['endereco']}\n"
                f"Bairro: {DESTINO_FIXO['bairro']}\n"
                f"CEP: {DESTINO_FIXO['cep']}\n"
                f"Município: {DESTINO_FIXO['municipio']} - {DESTINO_FIXO['uf']}\n"
            )
            st.code(texto_etiqueta, language="text")
            
            if peso_cubado > peso_fisico * 1.5:
                st.warning("⚠️ **Nota de Cubagem:** A caixa informada possui grande volume em relação ao peso físico. Certifique-se de que o cliente não está utilizando uma embalagem excessivamente maior do que o produto exige.")
        else:
            st.warning("Preencha todas as dimensões e peso com valores maiores que zero.")


# --- MÓDULO FINANCEIRO ---
def render_calculadora_desconto():
    st.subheader("📉 Calculadora de Desconto (Avarias)")
    valor_item = st.number_input("Valor Original do Item (R$)", min_value=0.0, step=10.0, format="%.2f", key="calc_desc_valor")
    pct_escolhida = st.radio("Porcentagem", [5, 10, 15, 20, 25, 30, "Personalizado"], horizontal=True)
    
    if pct_escolhida == "Personalizado":
        pct_calc = st.number_input("Digite a %", min_value=0.0, max_value=100.0, step=1.0, key="calc_desc_pct")
    else:
        pct_calc = float(pct_escolhida)

    if st.button("Calcular Desconto", type="primary", use_container_width=True):
        if valor_item > 0:
            desconto_reais = valor_item * (pct_calc / 100)
            valor_final = valor_item - desconto_reais
            col1, col2 = st.columns(2)
            col1.metric("Valor a Reembolsar", f"R$ {desconto_reais:.2f}")
            col2.metric("Valor Líquido (Retido)", f"R$ {valor_final:.2f}")
            
            if pct_calc > 30:
                st.error("⚠️ O desconto supera o teto sugerido de 30%.")
            else:
                st.success("✅ Desconto dentro do limite permitido.")

def render_viabilidade_conserto():
    st.subheader("🛠️ Avaliação: Devolver ou Consertar?")
    col1, col2 = st.columns(2)
    with col1:
        valor_item = st.number_input("Valor Original do Item (R$)", min_value=0.0, step=50.0, format="%.2f", key="viab_valor_item")
    with col2:
        valor_orcamento = st.number_input("Valor do Orçamento (R$)", min_value=0.0, step=50.0, format="%.2f", key="viab_valor_orcamento")

    if st.button("Analisar Viabilidade", type="primary", use_container_width=True):
        if valor_item > 0 and valor_orcamento > 0:
            percentual = (valor_orcamento / valor_item) * 100
            st.write(f"**Impacto do Conserto:** {percentual:.1f}% do valor do item.")
            if percentual > 50:
                st.error("🔴 **NÃO COMPENSA.** Passou do limite de 50%. Siga com devolução/descarte.")
            else:
                st.success("🟢 **COMPENSA CONSERTAR.** Está dentro do limite aceitável.")


# ==========================================
# FLUXO 1: PAINEL DE AUTENTICAÇÃO
# ==========================================
if not st.session_state.logado:
    st.title("🔒 CSTools")
    col_login, _ = st.columns([1, 2])
    with col_login:
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if usuario_input in USUARIOS and USUARIOS[usuario_input] == senha_input:
                st.session_state.logado = True
                st.session_state.usuario_atual = usuario_input
                st.success("Acesso autorizado!")
                st.rerun()
            else:
                st.error("Credenciais inválidas. Tente novamente.")

# ==========================================
# FLUXO 2: APLICAÇÃO LOGADA
# ==========================================
else:
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
        
    st.sidebar.markdown(f"**Operador:** `{st.session_state.usuario_atual}`")
    st.sidebar.markdown("---")
    
    novo_tema = st.sidebar.radio("Tema:", ["Escuro", "Claro"], horizontal=True)
    if novo_tema != st.session_state.tema:
        st.session_state.tema = novo_tema
        st.rerun() 

    menu_principal = st.sidebar.radio(
        "Selecione o Módulo:",
        ["🏠 Dashboard", "📦 Logística", "💰 Financeiro", "📄 Fiscal"]
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Efetuar Logout"):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()

    # --- ENGENHARIA DE ROTEAMENTO ---
    if menu_principal == "🏠 Dashboard":
        render_dashboard_inicio()

    elif menu_principal == "📦 Logística":
        st.title("📦 Ferramentas de Logística")
        st.markdown("---")
        
        tool_logistica = st.selectbox(
            "Selecione a ferramenta:", 
            ["Calculadora PAC Reverso"]
        )
        
        if tool_logistica == "Calculadora PAC Reverso":
            render_calculadora_pac_reverso()

    elif menu_principal == "💰 Financeiro":
        st.title("💰 Acordos e Financeiro")
        st.markdown("---")
        tool_fin = st.selectbox(
            "Selecione a ferramenta:", 
            ["Calculadora de Desconto (Avarias)", "Vale mais devolver ou consertar?"]
        )
        if tool_fin == "Calculadora de Desconto (Avarias)":
            render_calculadora_desconto()
        elif tool_fin == "Vale mais devolver ou consertar?":
            render_viabilidade_conserto()

    elif menu_principal == "📄 Fiscal":
        st.title("📄 Ferramentas Fiscais")
        st.markdown("---")
        tool_fiscal = st.selectbox(
            "Selecione a ferramenta:", 
            ["Removedor de pontos e traços", "Simulador de Impostos"]
        )
        if tool_fiscal == "Removedor de pontos e traços":
            render_removedor_caracteres()
        elif tool_fiscal == "Simulador de Impostos":
            render_simulador_impostos()