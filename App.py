import streamlit as st
import pandas as pd
import os
import re

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
    st.session_state.tema = "Escuro" # Padrão

def aplicar_tema():
    # Cores Escuras (seu padrão)
    if st.session_state.tema == "Escuro":
        bg_sidebar = "#2A3B37"
        text_color = "#FFFFFF"
        btn_bg = "#2A3B37"
        h_color = "#2A3B37"
    # Cores Claras (Inversão)
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

# Aplica a função de tema
aplicar_tema()

# ==========================================
# FUNÇÕES MODULARES DAS FERRAMENTAS
# ==========================================

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
    st.markdown("Estime o custo do PAC Reverso entre os estados.")

    # --- ENDEREÇO DE DESTINO FIXO (CENTRAL DE DEVOLUÇÕES) ---
    DESTINO_FIXO = {
        "endereco": "Estrada Velha Guarulhos São Miguel, 3241",
        "bairro": "Jardim Arapongas",
        "cep": "07210-250",
        "municipio": "Guarulhos",
        "uf": "SP"
    }

    # Bloco Informativo com o Destino Fixo
    with st.expander("🏢 Endereço de Destino (Central de Recebimento)", expanded=False):
        st.markdown(f"""
        **Logradouro:** {DESTINO_FIXO['endereco']}  
        **Bairro:** {DESTINO_FIXO['bairro']} | **CEP:** {DESTINO_FIXO['cep']}  
        **Cidade/UF:** {DESTINO_FIXO['municipio']} - {DESTINO_FIXO['uf']}
        """)

    # 1. Entrada de Dados da Caixa (Origem e Dimensões)
    st.markdown("### 📥 Dados do Pacote e Origem")
    col_dim1, col_dim2 = st.columns(2)
    with col_dim1:
        peso_fisico = st.number_input("Peso Físico Real (kg)", min_value=0.0, step=0.1, key="pac_peso")
        comprimento = st.number_input("Comprimento (cm)", min_value=0.0, step=1.0, key="pac_comp")
    with col_dim2:
        largura = st.number_input("Largura (cm)", min_value=0.0, step=1.0, key="pac_larg")
        altura = st.number_input("Altura (cm)", min_value=0.0, step=1.0, key="pac_alt")

    # Região de Origem (Onde o cliente está para calcular o frete vindo para SP)
    regiao_origem = st.selectbox(
        "Origem do Cliente (De onde o pacote está vindo?):",
        ["São Paulo (Capital/Interior)", "Sudeste (RJ, MG, ES)", "Sul (PR, SC, RS)", "Centro-Oeste (MS, MT, GO, DF)", "Nordeste (BA, PE, CE, etc.)", "Norte (AM, PA, TO, etc.)"]
    )

    if st.button("Calcular Estimativa e Gerar Etiqueta", type="primary", use_container_width=True):
        if peso_fisico > 0 and comprimento > 0 and largura > 0 and altura > 0:
            
            # --- VALIDAÇÃO DE LIMITES REAIS DOS CORREIOS ---
            soma_dimensoes = comprimento + largura + altura
            if comprimento > 100 or largura > 100 or altura > 100 or peso_fisico > 30 or soma_dimensoes > 200:
                st.error("❌ **NÃO SEGUE POR CORREIOS!** O pacote ultrapassa os limites permitidos pelo PAC (Máx: 30kg, 100cm por lado ou 200cm na soma total). **Acione coleta por Transportadora.**")
                return

            # --- CÁLCULO DE CUBAGEM ---
            peso_cubado = (comprimento * largura * altura) / 6000
            
            # 1. Se o peso físico for até 5kg, a cubagem é totalmente ignorada
            # 2. Se a cubagem calculada for até 10kg, os Correios também perdoam a cubagem
            if peso_cubado <= 5.0 or peso_cubado <= 10.0:
                peso_considerado = peso_fisico
            else:
                peso_considerado = max(peso_fisico, peso_cubado)

            # --- MATRIZ DE TARIFAS MÉDIAS (Destino SP) ---
            matriz_tarifas = {
                "São Paulo (Capital/Interior)": [15.50, 22.00, 38.00, 55.00],
                "Sudeste (RJ, MG, ES)": [24.00, 32.50, 54.00, 78.00],
                "Sul (PR, SC, RS)": [26.00, 36.00, 59.00, 88.00],
                "Centro-Oeste (MS, MT, GO, DF)": [29.00, 42.00, 68.00, 98.00],
                "Nordeste (BA, PE, CE, etc.)": [36.00, 55.00, 92.00, 140.00],
                "Norte (AM, PA, TO, etc.)": [42.00, 68.00, 120.00, 185.00]
            }

            faixas = matriz_tarifas[regiao_origem]
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
            col_res2.metric("Peso Precificado", f"{peso_considerado:.2f} kg")
            col_res3.metric("Média do Custo Estimado", f"R$ {custo_estimado:.2f}")

            # --- UX: TEXTO PRONTO PARA ETIQUETA / INSTRUÇÃO AO CLIENTE ---
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
# --- SIDEBAR NAVEGAÇÃO ---
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
        
    st.sidebar.markdown(f"**Operador:** `{st.session_state.usuario_atual}`")
    st.sidebar.markdown("---")
    
    # Botão de Troca de Tema
    novo_tema = st.sidebar.radio("Tema:", ["Escuro", "Claro"], horizontal=True)
    if novo_tema != st.session_state.tema:
        st.session_state.tema = novo_tema
        st.rerun() # Recarrega a página para aplicar a cor na hora

    menu_principal = st.sidebar.radio(
        "Selecione o Módulo:",
        ["🏠 Dashboard", "📦 Logística", "💰 Financeiro", "📄 Fiscal", "📊 BI (Métricas)"]
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Efetuar Logout"):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()

    # --- ENGENHARIA DE ROTEAMENTO (IF/ELIF ALINHADOS) ---
    if menu_principal == "🏠 Dashboard":
        st.title("🏠 Início - CSTools")
        st.markdown("Selecione uma ferramenta no menu lateral para iniciar as atividades de suporte.")

    elif menu_principal == "📦 Logística":
        st.title("📦 Ferramentas de Logística")
        st.markdown("---")
        
        tool_logistica = st.selectbox(
            "Selecione a ferramenta:", 
            ["Calculadora PAC Reverso", "Calculadora de Cubagem"]
        )
        
        if tool_logistica == "Calculadora PAC Reverso":
            render_calculadora_pac_reverso()
            
        elif tool_logistica == "Calculadora de Cubagem":
            st.info("Módulo de cubagem geral em desenvolvimento.")

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