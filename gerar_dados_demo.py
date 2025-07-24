# Script para gerar dados simulados
# Salve como: gerar_dados_demo.py

import pandas as pd
import numpy as np
import os
from PIL import Image, ImageDraw
import random
from datetime import datetime, timedelta

# Criar diretório para dados
os.makedirs("dados_demo", exist_ok=True)
os.makedirs("dados_demo/imagens/saudavel", exist_ok=True)
os.makedirs("dados_demo/imagens/ictio", exist_ok=True)
os.makedirs("dados_demo/imagens/monogenoidea", exist_ok=True)

# 1. Gerar imagens sintéticas de parasitos
def criar_imagem_parasito(tipo, idx):
    img = Image.new('RGB', (224, 224), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    if tipo == 'saudavel':
        # Imagem limpa, apenas algumas células normais
        for _ in range(5):
            x, y = random.randint(20, 200), random.randint(20, 200)
            draw.ellipse([x-10, y-10, x+10, y+10], fill='lightgreen')
    
    elif tipo == 'ictio':
        # Pontos brancos característicos do íctio
        for _ in range(15):
            x, y = random.randint(20, 200), random.randint(20, 200)
            draw.ellipse([x-5, y-5, x+5, y+5], fill='white')
            draw.ellipse([x-3, y-3, x+3, y+3], fill='gray')
    
    elif tipo == 'monogenoidea':
        # Estruturas alongadas típicas de monogenoidea
        for _ in range(8):
            x, y = random.randint(20, 200), random.randint(20, 200)
            draw.rectangle([x-15, y-3, x+15, y+3], fill='darkred')
            draw.ellipse([x-20, y-5, x-10, y+5], fill='red')
    
    img.save(f"dados_demo/imagens/{tipo}/amostra_{idx:03d}.jpg")

# Gerar 50 imagens de cada tipo
for tipo in ['saudavel', 'ictio', 'monogenoidea']:
    for i in range(50):
        criar_imagem_parasito(tipo, i)

print("Imagens sintéticas criadas!")

# 2. Gerar dados de qualidade da água (30 dias, leituras a cada hora)
def gerar_dados_qualidade_agua():
    start_date = datetime.now() - timedelta(days=30)
    dados = []
    
    # Parâmetros base normais
    ph_base = 7.2
    temp_base = 28.0
    o2_base = 6.5
    turbidez_base = 15.0
    
    for i in range(30 * 24):  # 30 dias * 24 horas
        timestamp = start_date + timedelta(hours=i)
        
        # Variação natural + algumas anomalias
        ph = ph_base + np.random.normal(0, 0.3)
        temp = temp_base + np.random.normal(0, 1.5) + 3*np.sin(2*np.pi*i/24)  # ciclo diário
        o2 = o2_base + np.random.normal(0, 0.8) - 2*np.sin(2*np.pi*i/24)  # menos O2 de noite
        turbidez = turbidez_base + np.random.normal(0, 5)
        
        # Inserir algumas anomalias (eventos críticos)
        if 200 <= i <= 220:  # Evento de baixo oxigênio (dia 8-9)
            o2 *= 0.4
            ph += 0.8
        elif 400 <= i <= 430:  # Evento de alta turbidez (dia 16-17)
            turbidez *= 2.5
            temp += 2
        
        # Garantir limites realistas
        ph = np.clip(ph, 5.5, 9.0)
        temp = np.clip(temp, 20, 35)
        o2 = np.clip(o2, 0.5, 12)
        turbidez = np.clip(turbidez, 2, 80)
        
        dados.append({
            'timestamp': timestamp,
            'ph': round(ph, 2),
            'temperatura': round(temp, 2),
            'oxigenio': round(o2, 2),
            'turbidez': round(turbidez, 2)
        })
    
    df = pd.DataFrame(dados)
    df.to_csv("dados_demo/qualidade_agua.csv", index=False)
    print("Dados de qualidade da água criados!")
    return df

# Gerar os dados
df_agua = gerar_dados_qualidade_agua()
print(f"Dataset criado com {len(df_agua)} registros")
print("\nPrimeiras 5 linhas:")
print(df_agua.head())