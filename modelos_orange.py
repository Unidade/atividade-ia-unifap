# arquivo: usar_modelos_orange.py

import pickle
import Orange
import numpy as np
from PIL import Image
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class SistemaMonitoramentoIA:
    def __init__(self):
        self.modelo_cnn = None
        self.modelo_lstm = None
        self.scaler = MinMaxScaler()
        
    def carregar_modelos(self):
        """Carrega os modelos treinados no Orange"""
        try:
            # Carregar modelo CNN para diagnóstico de parasitos
            with open("modelo_parasitos_cnn.pkcls", "rb") as f:
                self.modelo_cnn = pickle.load(f)
            print("✓ Modelo CNN carregado com sucesso")
            
            # Carregar modelo LSTM para qualidade da água
            with open("modelo_qualidade_lstm.pkcls", "rb") as f:
                self.modelo_lstm = pickle.load(f)
            print("✓ Modelo LSTM carregado com sucesso")
            
        except FileNotFoundError as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            print("Execute primeiro os workflows no Orange Canvas")
    
    def diagnosticar_parasito(self, caminho_imagem):
        """
        Diagnóstica parasitos a partir de uma imagem microscópica
        """
        if not self.modelo_cnn:
            return "Modelo CNN não carregado"
        
        try:
            # Simular o processamento que seria feito pelo Image Embedding
            # Em uma implementação real, seria necessário replicar exatamente
            # o mesmo pré-processamento usado no Orange
            
            # Para esta demonstração, vamos simular uma previsão
            classes = ['saudavel', 'ictio', 'monogenoidea']
            probabilidades = np.random.dirichlet([1, 1, 1])  # Simulação
            
            classe_predita = classes[np.argmax(probabilidades)]
            confianca = max(probabilidades)
            
            return {
                'diagnostico': classe_predita,
                'confianca': f"{confianca:.2%}",
                'probabilidades': {
                    classes[i]: f"{prob:.2%}" 
                    for i, prob in enumerate(probabilidades)
                },
                'recomendacao': self._get_recomendacao(classe_predita)
            }
            
        except Exception as e:
            return f"Erro no diagnóstico: {e}"
    
    def detectar_anomalia_agua(self, dados_recentes):
        """
        Detecta anomalias na qualidade da água usando dados das últimas 24h
        dados_recentes: DataFrame com colunas ['ph', 'temperatura', 'oxigenio', 'turbidez']
        """
        if not self.modelo_lstm:
            return "Modelo LSTM não carregado"
        
        try:
            # Normalizar dados
            dados_norm = self.scaler.fit_transform(dados_recentes)
            
            # Simulação do erro de reconstrução
            if len(dados_norm) >= 24:
                sequencia_atual = dados_norm[-24:]  # Últimas 24 horas
                media_atual = np.mean(sequencia_atual, axis=0)
                media_anterior = np.mean(dados_norm[-48:-24], axis=0) if len(dados_norm) >= 48 else media_atual
                
                erro_reconstrucao = np.mean((media_atual - media_anterior)**2)
                
                # Threshold para anomalia (ajustável)
                threshold = 0.015
                is_anomalia = erro_reconstrucao > threshold
                
                # Identificar parâmetro mais crítico
                diferencas = np.abs(media_atual - media_anterior)
                parametros = ['pH', 'Temperatura', 'Oxigênio', 'Turbidez']
                param_critico = parametros[np.argmax(diferencas)]
                
                return {
                    'anomalia_detectada': is_anomalia,
                    'score_anomalia': f"{erro_reconstrucao:.4f}",
                    'threshold': f"{threshold:.4f}",
                    'parametro_critico': param_critico,
                    'nivel_alerta': 'CRÍTICO' if erro_reconstrucao > threshold * 2 else 'ATENÇÃO' if is_anomalia else 'NORMAL',
                    'valores_atuais': {
                        'pH': f"{dados_recentes['ph'].iloc[-1]:.2f}",
                        'Temperatura': f"{dados_recentes['temperatura'].iloc[-1]:.1f}°C",
                        'Oxigênio': f"{dados_recentes['oxigenio'].iloc[-1]:.2f} mg/L",
                        'Turbidez': f"{dados_recentes['turbidez'].iloc[-1]:.1f} NTU"
                    }
                }
            else:
                return {'erro': 'Dados insuficientes (necessário pelo menos 24h)'}
                
        except Exception as e:
            return f"Erro na detecção de anomalia: {e}"
    
    def _get_recomendacao(self, diagnostico):
        """Retorna recomendações baseadas no diagnóstico"""
        recomendacoes = {
            'saudavel': "✓ Condição normal. Manter práticas atuais de manejo.",
            'ictio': "⚠️ URGENTE: Ictiofitiríase detectada. Iniciar tratamento com sal (3-5g/L) ou formalina. Melhorar qualidade da água.",
            'monogenoidea': "⚠️ Monogenoidea detectado. Tratar com praziquantel ou organofosforados. Verificar densidade de estocagem."
        }
        return recomendacoes.get(diagnostico, "Consultar veterinário.")

# Exemplo de uso
if __name__ == "__main__":
    # Inicializar sistema
    sistema = SistemaMonitoramentoIA()
    sistema.carregar_modelos()
    
    # Teste 1: Diagnóstico de parasito
    print("\n=== TESTE DIAGNÓSTICO DE PARASITO ===")
    resultado_parasito = sistema.diagnosticar_parasito("dados_demo/imagens/ictio/amostra_001.jpg")
    print(f"Diagnóstico: {resultado_parasito}")
    
    # Teste 2: Detecção de anomalia na água
    print("\n=== TESTE DETECÇÃO ANOMALIA ÁGUA ===")
    dados_agua = pd.read_csv("dados_demo/qualidade_agua.csv")
    resultado_agua = sistema.detectar_anomalia_agua(dados_agua.tail(48))  # Últimas 48 horas
    print(f"Anomalia: {resultado_agua}")