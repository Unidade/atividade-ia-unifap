# arquivo: dashboard_aquicultura.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from modelos_orange import SistemaMonitoramentoIA

st.set_page_config(
    page_title="AquaIA - Monitoramento Inteligente",
    page_icon="🐟",
    layout="wide"
)

@st.cache_resource
def init_sistema_ia():
    sistema = SistemaMonitoramentoIA()
    sistema.carregar_modelos()
    return sistema

sistema_ia = init_sistema_ia()

st.sidebar.title("🐟 AquaIA Amapá")
st.sidebar.markdown("Sistema Inteligente de Monitoramento Aquícola")

opcao = st.sidebar.selectbox(
    "Selecione a funcionalidade:",
    ["Dashboard Principal", "Diagnóstico de Parasitos", "Histórico e Relatórios"]
)

if opcao == "Dashboard Principal":
    st.title("📊 Dashboard de Monitoramento em Tempo Real")
    
    dados_agua = pd.read_csv("dados_demo/qualidade_agua.csv")
    dados_agua['timestamp'] = pd.to_datetime(dados_agua['timestamp'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    ultimo_registro = dados_agua.iloc[-1]
    
    with col1:
        st.metric(
            "pH",
            f"{ultimo_registro['ph']:.2f}",
            delta=f"{ultimo_registro['ph'] - dados_agua.iloc[-2]['ph']:.2f}"
        )
    
    with col2:
        st.metric(
            "Temperatura",
            f"{ultimo_registro['temperatura']:.1f}°C",
            delta=f"{ultimo_registro['temperatura'] - dados_agua.iloc[-2]['temperatura']:.1f}"
        )
    
    with col3:
        cor_o2 = "normal" if ultimo_registro['oxigenio'] > 4.0 else "inverse"
        st.metric(
            "Oxigênio",
            f"{ultimo_registro['oxigenio']:.2f} mg/L",
            delta=f"{ultimo_registro['oxigenio'] - dados_agua.iloc[-2]['oxigenio']:.2f}",
            delta_color=cor_o2
        )
    
    with col4:
        st.metric(
            "Turbidez",
            f"{ultimo_registro['turbidez']:.1f} NTU",
            delta=f"{ultimo_registro['turbidez'] - dados_agua.iloc[-2]['turbidez']:.1f}"
        )
    
    st.subheader("🚨 Análise de Anomalias (IA)")
    resultado_anomalia = sistema_ia.detectar_anomalia_agua(dados_agua.tail(48))
    
    if isinstance(resultado_anomalia, dict):
        nivel = resultado_anomalia.get('nivel_alerta', 'NORMAL')
        
        if nivel == 'CRÍTICO':
            st.error(f"⚠️ ALERTA CRÍTICO: Anomalia detectada!")
        elif nivel == 'ATENÇÃO':
            st.warning(f"⚠️ ATENÇÃO: Condições anômalas detectadas")
        else:
            st.success("✅ Condições normais")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Score de Anomalia:** {resultado_anomalia.get('score_anomalia', 'N/A')}")
            st.write(f"**Parâmetro Crítico:** {resultado_anomalia.get('parametro_critico', 'N/A')}")
        
        with col2:
            valores = resultado_anomalia.get('valores_atuais', {})
            for param, valor in valores.items():
                st.write(f"**{param}:** {valor}")
    
    st.subheader("📈 Tendências dos Últimos 7 Dias")
    
    dados_semana = dados_agua.tail(7*24)  # Últimos 7 dias
    
    fig_o2 = px.line(
        dados_semana, x='timestamp', y='oxigenio',
        title='Oxigênio Dissolvido (mg/L)',
        color_discrete_sequence=['blue']
    )
    fig_o2.add_hline(y=4.0, line_dash="dash", line_color="red", 
                     annotation_text="Limite Crítico")
    st.plotly_chart(fig_o2, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ph = px.line(dados_semana, x='timestamp', y='ph', title='pH')
        fig_ph.add_hline(y=6.5, line_dash="dash", line_color="orange")
        fig_ph.add_hline(y=8.5, line_dash="dash", line_color="orange")
        st.plotly_chart(fig_ph, use_container_width=True)
    
    with col2:
        fig_temp = px.line(dados_semana, x='timestamp', y='temperatura', 
                          title='Temperatura (°C)', color_discrete_sequence=['red'])
        st.plotly_chart(fig_temp, use_container_width=True)

elif opcao == "Diagnóstico de Parasitos":
    st.title("🔬 Diagnóstico Rápido de Parasitos")
    st.markdown("Faça upload de uma imagem microscópica para diagnóstico automático")
    
    uploaded_file = st.file_uploader(
        "Escolha uma imagem microscópica",
        type=['jpg', 'jpeg', 'png'],
        help="Imagem de amostra de muco ou raspado de brânquia (400x aumentos recomendado)"
    )
    
    if uploaded_file is not None:
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Imagem carregada", use_column_width=True)
        
        with col2:
            if st.button("🔍 Analisar Imagem", type="primary"):
                with st.spinner("Analisando imagem com IA..."):
                    time.sleep(2)  
                    resultado = sistema_ia.diagnosticar_parasito(uploaded_file.name)
                
                if isinstance(resultado, dict):
                    st.subheader("📋 Resultado do Diagnóstico")
                    
                    diagnostico = resultado['diagnostico']
                    confianca = resultado['confianca']
                    
                    if diagnostico == 'saudavel':
                        st.success(f"✅ **{diagnostico.upper()}** (Confiança: {confianca})")
                    else:
                        st.error(f"⚠️ **{diagnostico.upper()}** detectado (Confiança: {confianca})")
                    
                    st.subheader("📊 Probabilidades por Classe")
                    probs = resultado['probabilidades']
                    
                    df_probs = pd.DataFrame([
                        {'Classe': k.title(), 'Probabilidade': v} 
                        for k, v in probs.items()
                    ])
                    
                    fig_probs = px.bar(df_probs, x='Classe', y='Probabilidade', 
                                      title='Distribuição de Probabilidades')
                    st.plotly_chart(fig_probs, use_container_width=True)
                    
                    st.subheader("💊 Recomendações de Tratamento")
                    st.info(resultado['recomendacao'])
                else:
                    st.error(resultado)
    
    st.subheader("📚 Guia de Referência")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🟢 Saudável**
        - Células normais
        - Poucos detritos
        - Sem parasitos visíveis
        """)
    
    with col2:
        st.markdown("""
        **⚪ Ictiofitiríase**
        - Pontos brancos característicos
        - Trofozoítos esféricos
        - Tratamento: sal 3-5g/L
        """)
    
    with col3:
        st.markdown("""
        **🔴 Monogenóidea**
        - Estruturas alongadas
        - Ganchos e ventosas
        - Tratamento: praziquantel
        """)

elif opcao == "Histórico e Relatórios":
    st.title("📈 Histórico e Análise de Tendências")
    
    dados_agua = pd.read_csv("dados_demo/qualidade_agua.csv")
    dados_agua['timestamp'] = pd.to_datetime(dados_agua['timestamp'])
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input(
            "Data de início",
            value=dados_agua['timestamp'].min().date()
        )
    
    with col2:
        data_fim = st.date_input(
            "Data de fim",
            value=dados_agua['timestamp'].max().date()
        )
    
    # Filtrar dados
    mask = (dados_agua['timestamp'].dt.date >= data_inicio) & \
           (dados_agua['timestamp'].dt.date <= data_fim)
    dados_filtrados = dados_agua.loc[mask]
    
    # Estatísticas resumo
    st.subheader("📊 Estatísticas do Período")
    
    stats = dados_filtrados[['ph', 'temperatura', 'oxigenio', 'turbidez']].describe()
    st.dataframe(stats.round(2))
    
    # Gráfico combinado
    st.subheader("📈 Tendências Históricas")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dados_filtrados['timestamp'], 
        y=dados_filtrados['ph'],
        name='pH', 
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=dados_filtrados['timestamp'], 
        y=dados_filtrados['temperatura'],
        name='Temperatura (°C)', 
        yaxis='y2'
    ))
    
    fig.add_trace(go.Scatter(
        x=dados_filtrados['timestamp'], 
        y=dados_filtrados['oxigenio'],
        name='O₂ (mg/L)', 
        yaxis='y3'
    ))
    
    # Layout com múltiplos eixos Y
    fig.update_layout(
        title="Parâmetros da Qualidade da Água - Histórico",
        xaxis=dict(title="Data"),
        yaxis=dict(title="pH", side="left"),
        yaxis2=dict(title="Temperatura (°C)", side="right", overlaying="y"),
        yaxis3=dict(title="O₂ (mg/L)", side="right", overlaying="y", position=0.95),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Exportar relatório
    if st.button("📄 Gerar Relatório PDF"):
        st.success("Relatório gerado! (Funcionalidade simulada)")
        st.balloons()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**AquaIA Amapá 2025**")
st.sidebar.markdown("Sistema desenvolvido para monitoramento inteligente da aquicultura")