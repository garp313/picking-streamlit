import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Picking & Arrumação Hub",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJEÇÃO DE CSS CUSTOMIZADO (Design Premium e Glassmorphism) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Gradient */
    .header-container {
        background: linear-gradient(135deg, rgba(20, 20, 35, 0.95) 0%, rgba(35, 25, 60, 0.95) 100%);
        border: 1px solid rgba(168, 85, 247, 0.2);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(12px);
    }
    
    .header-title {
        background: linear-gradient(90deg, #a855f7 0%, #3b82f6 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #9ca3af;
        font-size: 1.1rem;
        font-weight: 300;
    }

    /* Cards de Métricas Estilizados */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        border-color: rgba(168, 85, 247, 0.4);
        box-shadow: 0 8px 30px rgba(168, 85, 247, 0.15);
        background: rgba(255, 255, 255, 0.06);
    }
    
    /* Tabelas e Dataframes */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Customização dos botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Estilo do API Log */
    .api-log-box {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', Courier, monospace;
        color: #34d399;
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ID FIXO DA PLANILHA PADRÃO
DEFAULT_SHEET_ID = "1DmmBbprkeVmd5iHLOCigxXK7ttX0CAoGqcfpyJljuHI"

# Inicialização de Estados da Sessão (Session State)
if 'df_raw' not in st.session_state:
    st.session_state['df_raw'] = None
if 'df_cleaned' not in st.session_state:
    st.session_state['df_cleaned'] = None
if 'api_history' not in st.session_state:
    st.session_state['api_history'] = []

# --- HEADER DA APLICAÇÃO ---
st.markdown("""
<div class="header-container">
    <div class="header-title">📦 Picking & Arrumação Hub</div>
    <div class="header-subtitle">Carregue dados do seu inventário, limpe e organize as colunas, visualize insights gráficos e faça integrações diretas via API.</div>
    <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <span style="color: #a855f7; font-weight: 600;">Planilha Oficial:</span> 
        <a href="https://docs.google.com/spreadsheets/d/1DmmBbprkeVmd5iHLOCigxXK7ttX0CAoGqcfpyJljuHI/edit?gid=0#gid=0" target="_blank" style="color: #3b82f6; text-decoration: none; font-weight: 500; hover-color: #60a5fa;">
            Abrir Planilha Google Sheets 🔗
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURAÇÃO DE ENTRADA ---
st.sidebar.markdown("### ⚙️ Origem dos Dados")
data_source = st.sidebar.radio(
    "Escolha a fonte dos dados:",
    ["Google Sheets (Planilha Nuvem)", "Carregar Arquivo Local (CSV/Excel)"]
)

loaded_successfully = False

if data_source == "Google Sheets (Planilha Nuvem)":
    use_default = st.sidebar.checkbox("Usar planilha padrão oficial", value=True)
    if use_default:
        sheet_id = DEFAULT_SHEET_ID
        st.sidebar.info("Planilha ativa: **Oficial de Arrumação**")
    else:
        sheet_id = st.sidebar.text_input("ID ou URL da Planilha Google Sheets:", value=DEFAULT_SHEET_ID)
        if not sheet_id:
            st.sidebar.warning("Por favor, insira o ID da planilha.")

    if st.sidebar.button("🔍 Importar da Nuvem", use_container_width=True):
        # Limpar o ID se o usuário colar a URL inteira
        extracted_id = sheet_id
        if "spreadsheets/d/" in sheet_id:
            try:
                extracted_id = sheet_id.split("spreadsheets/d/")[1].split("/")[0]
            except Exception:
                pass
        
        url_csv = f"https://docs.google.com/spreadsheets/d/{extracted_id}/export?format=csv"
        
        try:
            with st.spinner("Conectando ao Google Sheets..."):
                # Lê todas as colunas como string para proteger formatos (como zeros à esquerda em códigos)
                df = pd.read_csv(url_csv, dtype=str)
                df.columns = df.columns.str.strip()
                st.session_state['df_raw'] = df
                st.sidebar.success("✅ Importado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao ler planilha. Verifique se o link está público para compartilhamento. Erro: {e}")

else:
    uploaded_file = st.sidebar.file_uploader("Selecione um arquivo CSV ou Excel:", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            with st.spinner("Carregando arquivo..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, dtype=str)
                else:
                    df = pd.read_excel(uploaded_file, dtype=str)
                df.columns = df.columns.str.strip()
                st.session_state['df_raw'] = df
                st.sidebar.success("✅ Arquivo carregado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao ler o arquivo: {e}")

# Botão para resetar os dados carregados
if st.sidebar.button("🗑️ Limpar Todos os Dados", use_container_width=True):
    st.session_state['df_raw'] = None
    st.session_state['df_cleaned'] = None
    st.rerun()

# --- FLUXO PRINCIPAL DE PROCESSAMENTO ---
if st.session_state['df_raw'] is not None:
    df_raw = st.session_state['df_raw'].copy()
    
    # --- PROCESSAMENTO AUTOMÁTICO DE COLUNAS (Sem UI) ---
    all_cols = list(df_raw.columns)
    default_order = ["Produto", "Cor", "Tamanho", "desc_produto", "Grade", "Quantidade"]
    
    # Reordenação automática: coloca colunas padrão primeiro, seguidas por adicionais
    ordered_cols = [col for col in default_order if col in all_cols]
    remaining_cols = [col for col in all_cols if col not in ordered_cols]
    df_ordered = df_raw[ordered_cols + remaining_cols]
    
    # Identifica colunas contendo 'desc' para ocultar automaticamente no JSON
    cols_to_drop = [c for c in df_ordered.columns if 'desc' in c.lower()]
    
    # Abas principais
    tab_data, tab_analytics, tab_pipeline = st.tabs([
        "📊 Dados & Filtros", 
        "📈 Dashboard Analítico", 
        "🚀 Pipeline de Exportação & API"
    ])
    
    # --- ABA 1: DADOS E FILTROS ---
    with tab_data:
        # Filtros Dinâmicos
        st.markdown("### 🔍 Filtros Interativos")
        
        f_cols = st.columns(3)
        
        # Filtro de Produto
        with f_cols[0]:
            col_prod = next((c for c in df_ordered.columns if c.lower() == 'produto'), None)
            if col_prod:
                unique_prods = ["Todos"] + sorted(list(df_ordered[col_prod].dropna().unique()))
                filter_prod = st.selectbox("Filtrar por Produto:", unique_prods)
            else:
                filter_prod = "Todos"
                
        # Filtro de Cor
        with f_cols[1]:
            col_cor = next((c for c in df_ordered.columns if c.lower() == 'cor'), None)
            if col_cor:
                unique_cors = ["Todas"] + sorted(list(df_ordered[col_cor].dropna().unique()))
                filter_cor = st.selectbox("Filtrar por Cor:", unique_cors)
            else:
                filter_cor = "Todas"
                
        # Filtro de Grade / Tamanho
        with f_cols[2]:
            col_grade = next((c for c in df_ordered.columns if c.lower() in ['grade', 'tamanho']), None)
            if col_grade:
                unique_grades = ["Todas"] + sorted(list(df_ordered[col_grade].dropna().unique()))
                filter_grade = st.selectbox("Filtrar por Grade/Tamanho:", unique_grades)
            else:
                filter_grade = "Todas"

        # Aplicar filtros no dataframe exibido
        df_filtered = df_ordered.copy()
        if col_prod and filter_prod != "Todos":
            df_filtered = df_filtered[df_filtered[col_prod] == filter_prod]
        if col_cor and filter_cor != "Todas":
            df_filtered = df_filtered[df_filtered[col_cor] == filter_cor]
        if col_grade and filter_grade != "Todas":
            df_filtered = df_filtered[df_filtered[col_grade] == filter_grade]

        st.markdown(f"Exibindo **{len(df_filtered)}** registros de **{len(df_ordered)}** após filtros.")
        st.dataframe(df_filtered, use_container_width=True)
        
        # Salva o dataframe final filtrado e processado no state
        st.session_state['df_cleaned'] = df_filtered
        st.session_state['cols_to_drop'] = cols_to_drop

    # --- ABA 2: DASHBOARD ANALÍTICO ---
    with tab_analytics:
        st.markdown("### 📊 Insights & Estatísticas do Inventário")
        
        # Extrair e sanitizar coluna de Quantidade
        col_qtd = next((c for c in df_filtered.columns if 'qtd' in c.lower() or 'quantidade' in c.lower()), None)
        
        if col_qtd:
            df_filtered[col_qtd] = pd.to_numeric(df_filtered[col_qtd], errors='coerce').fillna(0).astype(int)
            total_pecas = df_filtered[col_qtd].sum()
            avg_pecas = df_filtered[col_qtd].mean() if len(df_filtered) > 0 else 0
        else:
            total_pecas = 0
            avg_pecas = 0
            
        total_skus = len(df_filtered)
        
        # Contagem de valores únicos
        col_p = next((c for c in df_filtered.columns if c.lower() == 'produto'), None)
        col_c = next((c for c in df_filtered.columns if c.lower() == 'cor'), None)
        
        unique_products_count = df_filtered[col_p].nunique() if col_p else 0
        unique_colors_count = df_filtered[col_c].nunique() if col_c else 0
        
        # Cards de Métricas Grid
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.metric("🛒 SKUs Únicos", total_skus)
        with m_col2:
            st.metric("👕 Total de Peças", f"{total_pecas:,}".replace(",", "."))
        with m_col3:
            st.metric("📦 Média p/ SKU", f"{avg_pecas:.1f}".replace(".", ","))
        with m_col4:
            st.metric("🎨 Produtos / Cores", f"{unique_products_count} / {unique_colors_count}")

        st.markdown("---")
        
        # Gráficos Plotly
        st.markdown("#### Distribuição Visual")
        g_col1, g_col2 = st.columns(2)
        
        with g_col1:
            # 1. Distribuição de Grade / Tamanho (Donut Chart)
            col_g = next((c for c in df_filtered.columns if c.lower() == 'grade'), None)
            if col_g and col_qtd:
                grade_data = df_filtered.groupby(col_g)[col_qtd].sum().reset_index()
                # Ordenação lógica de grade se possível
                tamanho_order = {"PP":0, "P":1, "M":2, "G":3, "GG":4, "XG":5, "EG":6}
                grade_data['order'] = grade_data[col_g].map(tamanho_order).fillna(99)
                grade_data = grade_data.sort_values('order')
                
                fig_donut = px.pie(
                    grade_data, 
                    values=col_qtd, 
                    names=col_g, 
                    hole=0.4,
                    title="Volume por Grade/Tamanho",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f3f4f6',
                    margin=dict(t=40, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Colunas de 'Grade' ou 'Quantidade' não encontradas para exibir gráfico de Grade.")
                
        with g_col2:
            # 2. Top Produtos mais volumosos — usa desc_produto se disponível
            col_desc = next((c for c in df_filtered.columns if 'desc' in c.lower()), None)
            label_col = col_desc if col_desc else col_p

            if col_p and col_qtd:
                if col_desc:
                    prod_data = df_filtered.groupby([col_p, col_desc])[col_qtd].sum().reset_index()
                    prod_data = prod_data.sort_values(by=col_qtd, ascending=False).head(10)
                    # Trunca descrição para caber no gráfico
                    prod_data['label'] = prod_data[col_desc].str.slice(0, 22)
                else:
                    prod_data = df_filtered.groupby(col_p)[col_qtd].sum().reset_index()
                    prod_data = prod_data.sort_values(by=col_qtd, ascending=False).head(10)
                    prod_data['label'] = prod_data[col_p].astype(str)

                prod_data = prod_data.sort_values(by=col_qtd, ascending=True)

                fig_bar = px.bar(
                    prod_data,
                    x=col_qtd,
                    y='label',
                    orientation='h',
                    title="🏆 Top 10 Produtos por Volume",
                    text=col_qtd,
                    color=col_qtd,
                    color_continuous_scale=[[0, '#6366f1'], [1, '#a855f7']]
                )
                fig_bar.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_line_width=0
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f3f4f6',
                    font_size=12,
                    showlegend=False,
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Qtd. de Peças'),
                    yaxis=dict(showgrid=False, title=''),
                    margin=dict(t=50, b=20, l=10, r=60)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Colunas de 'Produto' ou 'Quantidade' não encontradas para exibir gráfico de Produtos.")

        st.markdown("---")
        # 3. Top 15 Cores mais volumosas (horizontal, limpo)
        if col_c and col_qtd:
            st.markdown("#### 🎨 Top 15 Cores por Volume")
            color_data = (
                df_filtered.groupby(col_c)[col_qtd]
                .sum()
                .reset_index()
                .sort_values(by=col_qtd, ascending=False)
                .head(15)
                .sort_values(by=col_qtd, ascending=True)
            )
            color_data[col_c] = "Cor " + color_data[col_c].astype(str)

            fig_color = px.bar(
                color_data,
                x=col_qtd,
                y=col_c,
                orientation='h',
                title="Top 15 Cores por Volume de Peças",
                text=col_qtd,
                color=col_qtd,
                color_continuous_scale=[[0, '#0ea5e9'], [1, '#6366f1']]
            )
            fig_color.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                marker_line_width=0
            )
            fig_color.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f3f4f6',
                font_size=12,
                showlegend=False,
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Qtd. de Peças'),
                yaxis=dict(showgrid=False, title=''),
                margin=dict(t=50, b=20, l=10, r=60)
            )
            st.plotly_chart(fig_color, use_container_width=True)

    # --- ABA 3: PIPELINE DE EXPORTAÇÃO & API ---
    with tab_pipeline:
        st.markdown("### ⚙️ Pipeline de Exportação JSON & Envio")
        
        # Preparando os dados finais para o JSON
        df_export = st.session_state['df_cleaned'].copy()
        cols_to_drop = st.session_state.get('cols_to_drop', [])
        
        df_export_json = df_export.drop(columns=cols_to_drop, errors='ignore')
        
        # Converter coluna quantidade para número se existir
        col_qtd = next((c for c in df_export_json.columns if 'qtd' in c.lower() or 'quantidade' in c.lower()), None)
        if col_qtd:
            df_export_json[col_qtd] = pd.to_numeric(df_export_json[col_qtd], errors='coerce').fillna(0).astype(int)
            
        json_data = df_export_json.to_dict(orient='records')
        json_str = json.dumps(json_data, indent=4, ensure_ascii=False)
        
        col_pipe1, col_pipe2 = st.columns(2)
        
        with col_pipe1:
            st.markdown("#### 📝 Preview do JSON Gerado")
            if cols_to_drop:
                st.caption(f"Colunas omitidas no JSON: `{', '.join(cols_to_drop)}`")
            st.code(json_str, language="json")
            
            # Botão de download
            data_hoje = datetime.now().strftime('%d-%m-%Y')
            st.download_button(
                label="⬇️ Baixar Arquivo JSON Organizado",
                data=json_str,
                file_name=f"arrumacao_{data_hoje}.json",
                mime="application/json",
                use_container_width=True
            )
            
        with col_pipe2:
            st.markdown("#### 🚀 API Sandbox (Opcional)")
            enviar_api = st.checkbox("Ativar envio de dados para API externa", value=False)
            
            if enviar_api:
                api_url = st.text_input("URL da API de Destino:", placeholder="https://api.exemplo.com/v1/picking")
                
                col_m, col_h = st.columns([1, 2])
                with col_m:
                    api_method = st.selectbox("Método HTTP:", ["POST", "PUT", "PATCH"])
                with col_h:
                    st.caption("Configurações rápidas de envio")
                
                # Custom Headers
                st.markdown("**Headers Customizados (JSON format)**")
                default_headers = '{\n    "Content-Type": "application/json",\n    "Authorization": "Bearer TOKEN_AQUI"\n}'
                headers_text = st.text_area("Insira os Headers HTTP no formato JSON:", value=default_headers, height=100)
                
                # Botão de Envio
                if st.button("🚀 Enviar Carga de Dados", use_container_width=True):
                    if not api_url:
                        st.error("⚠️ Por favor, insira a URL de destino da API.")
                    else:
                        headers = {}
                        if headers_text:
                            try:
                                headers = json.loads(headers_text)
                            except Exception as he:
                                st.warning(f"⚠️ Erro ao processar headers. Enviando sem headers adicionais. Erro: {he}")
                        
                        with st.spinner("Transmitindo lote para API..."):
                            try:
                                t_start = datetime.now()
                                
                                # Realizar a chamada HTTP
                                if api_method == "POST":
                                    response = requests.post(api_url, json=json_data, headers=headers, timeout=10)
                                elif api_method == "PUT":
                                    response = requests.post(api_url, json=json_data, headers=headers, timeout=10)
                                else: # PATCH
                                    response = requests.patch(api_url, json=json_data, headers=headers, timeout=10)
                                    
                                t_duration = (datetime.now() - t_start).total_seconds()
                                
                                # Registrar resposta no histórico
                                log_entry = {
                                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                                    "method": api_method,
                                    "url": api_url,
                                    "status": response.status_code,
                                    "duration": f"{t_duration:.2f}s",
                                    "response": response.text[:500] + ("..." if len(response.text) > 500 else "")
                                }
                                st.session_state['api_history'].insert(0, log_entry)
                                
                                if response.status_code in [200, 201, 202]:
                                    st.success(f"🎉 Sucesso! Código de retorno: {response.status_code} ({t_duration:.2f}s)")
                                else:
                                    st.error(f"❌ Falha no envio. Código de retorno: {response.status_code}")
                                    
                                # Exibir painel da última resposta
                                st.markdown("**Último Log de Resposta:**")
                                st.markdown(f"""
                                <div class="api-log-box">
                                    <b>[STATUS]</b> {response.status_code} {response.reason}<br>
                                    <b>[TEMPO]</b> {t_duration:.3f} segundos<br>
                                    <b>[HEADERS]</b><br>
                                    {json.dumps(dict(response.headers), indent=2)}<br><br>
                                    <b>[CORPO DA RESPOSTA]</b><br>
                                    {response.text}
                                </div>
                                """, unsafe_allow_html=True)
                                
                            except Exception as api_err:
                                st.error(f"❌ Falha catastrófica de conexão: {api_err}")
                
                # Histórico de Envio
                if st.session_state['api_history']:
                    st.markdown("---")
                    st.markdown("📜 **Histórico de Envios nesta Sessão**")
                    for item in st.session_state['api_history'][:3]:
                        status_color = "🟢" if item['status'] in [200, 201, 202] else "🔴"
                        st.markdown(f"**{status_color} {item['timestamp']}** | {item['method']} | {item['status']} | Duração: {item['duration']}")
                        st.caption(f"URL: {item['url']}")
            else:
                st.info("ℹ️ O envio automático para API está desativado. Você pode utilizar a coluna ao lado para baixar seu arquivo JSON de arrumação.")

else:
    # Caso nenhum dado tenha sido carregado
    st.info("👋 Seja bem-vindo! Para começar, utilize o menu lateral para selecionar e carregar seus dados (via Google Sheets ou Arquivo Local).")
    
    # Exibir um card ilustrativo
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 3rem; text-align: center;">
        <h4 style="color: #9ca3af; margin-bottom: 0.5rem;">Aguardando dados...</h4>
        <p style="color: #6b7280; font-size: 0.95rem; max-width: 500px; margin: 0 auto;">Assim que você importar uma planilha, este painel exibirá as estatísticas de estoque, visualizações de grade e ferramentas para sincronização externa.</p>
    </div>
    """, unsafe_allow_html=True)
