# Script para o widget Python Script no Orange
# Prepara dados de série temporal para LSTM

import numpy as np
import pandas as pd
from Orange.data import Table, Domain, ContinuousVariable
from sklearn.preprocessing import MinMaxScaler

def criar_sequencias_lstm(dados, lookback=24):
    """
    Transforma dados de série temporal em sequências para LSTM
    lookback: quantas horas anteriores usar para prever anomalia
    """
    
    # Converter Orange Table para pandas DataFrame
    df = dados.to_pandas()
    
    # Selecionar apenas colunas numéricas de sensores
    colunas_sensores = ['ph', 'temperatura', 'oxigenio', 'turbidez']
    df_sensores = df[colunas_sensores].fillna(method='ffill')
    
    # Normalizar dados
    scaler = MinMaxScaler()
    dados_norm = scaler.fit_transform(df_sensores)
    
    # Criar sequências
    X, y = [], []
    for i in range(lookback, len(dados_norm)):
        # Sequência de entrada (últimas 'lookback' horas)
        X.append(dados_norm[i-lookback:i])
        
        # Target: erro de reconstrução simulado
        # (em produção, seria calculado baseado no modelo LSTM treinado)
        current_values = dados_norm[i]
        previous_values = dados_norm[i-1]
        erro_reconstrucao = np.mean((current_values - previous_values)**2)
        
        # Definir anomalia se erro > threshold
        is_anomaly = 1 if erro_reconstrucao > 0.01 else 0
        y.append(is_anomaly)
    
    # Achatar X para usar em Orange (cada sequência vira uma linha)
    X_flat = np.array(X).reshape(len(X), -1)
    y = np.array(y)
    
    # Criar nomes de colunas
    col_names = []
    for t in range(lookback):
        for sensor in colunas_sensores:
            col_names.append(f"{sensor}_t-{lookback-t}")
    
    # Criar domínio Orange
    attributes = [ContinuousVariable(name) for name in col_names]
    class_var = ContinuousVariable("anomalia")
    domain = Domain(attributes, class_var)
    
    # Criar tabela Orange
    data_combined = np.column_stack([X_flat, y])
    table = Table(domain, data_combined)
    
    return table

# Executar transformação
if in_data is not None:
    out_data = criar_sequencias_lstm(in_data, lookback=24)
else:
    out_data = None