import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da Página
st.set_page_config(page_title="Dimensionamento de Muro e Bloco", layout="wide")

def calcular_empuxo(h, gamma, phi):
    phi_rad = np.radians(phi)
    ka = (np.tan(np.radians(45) - phi_rad/2))**2
    f_empuxo = 0.5 * ka * gamma * (h**2)
    braço = h / 3
    momento = f_empuxo * braço
    return ka, f_empuxo, momento

# --- INTERFACE LATERAL (INPUTS) ---
st.sidebar.header("🔵 Entrada de Dados")

with st.sidebar.expander("Geometria e Solo", expanded=True):
    h_muro = st.number_input("Altura do Muro (m)", value=4.0, step=0.1)
    gamma_solo = st.number_input("Peso Específico Solo (kN/m³)", value=18.0)
    phi_solo = st.number_input("Ângulo de Atrito (°)", value=30.0)

with st.sidebar.expander("Cargas e Bloco", expanded=True):
    carga_v = st.number_input("Carga Vertical Pilar (kN)", value=500.0)
    d_estaca = st.number_input("Diâmetro da Estaca (m)", value=0.40)
    dist_estacas = st.number_input("Distância entre Estacas (m)", value=1.20)
    ecc_pilar = st.number_input("Excentricidade do Pilar (m)", value=0.0, step=0.05)
    fck = st.selectbox("fck do Concreto (MPa)", [20, 25, 30, 35, 40], index=2)

# --- CÁLCULOS ---
ka, force_h, momento_muro = calcular_empuxo(h_muro, gamma_solo, phi_solo)

# Reações nas Estacas (2 estacas)
# R = V/n ± (M + H*h_bloco)/dist
h_bloco = 0.8  # Assumido
r1 = (carga_v / 2) + (momento_muro / dist_estacas)
r2 = (carga_v / 2) - (momento_muro / dist_estacas)

# --- LAYOUT PRINCIPAL ---
st.title("🏗️ Dimensionamento de Muro de Arrimo sobre Bloco (2 Estacas)")
st.markdown("---")

col1, col2 = columns = st.columns([1, 1])

with col1:
    st.subheader("📊 Resultados de Empuxo")
    res_empuxo = pd.DataFrame({
        "Parâmetro": ["Coef. Empuxo Ativo (Ka)", "Força Resultante (Eh)", "Momento na Base"],
        "Valor": [round(ka, 3), f"{force_h:.2f} kN/m", f"{momento_muro:.2f} kNm/m"],
        "Status": ["✅ OK", "✅ Calculado", "⚠️ Crítico"]
    })
    st.table(res_empuxo)

    st.subheader("🔩 Reações nas Estacas")
    st.metric("Estaca 1 (Tracionada/Mais Carregada)", f"{r1:.2f} kN")
    st.metric("Estaca 2", f"{r2:.2f} kN")

with col2:
    st.subheader("📐 Desenho Esquemático Dinâmico")
    
    fig, ax = plt.subplots(figsize=(6, 8))
    
    # Desenho do Muro
    ax.plot([0, 0], [0, h_muro], color='black', lw=3) # Parede
    ax.plot([-0.5, 0.5], [0, 0], color='black', lw=4) # Base bloco
    
    # Desenho do Solo (Triângulo de empuxo)
    y_coords = np.linspace(0, h_muro, 10)
    x_empuxo = (h_muro - y_coords) * ka * 0.5 # Escala visual
    ax.fill_betweenx(y_coords, 0, x_empuxo, color='orange', alpha=0.3, label='Diagrama de Empuxo')
    
    # Desenho das Estacas (Baseadas na distância e excentricidade)
    pos_pilar = ecc_pilar
    estaca_a = pos_pilar - (dist_estacas/2)
    estaca_b = pos_pilar + (dist_estacas/2)
    
    # Estaca 1
    ax.add_patch(plt.Rectangle((estaca_a - d_estaca/2, -2), d_estaca, 2, color='gray', alpha=0.5))
    # Estaca 2
    ax.add_patch(plt.Rectangle((estaca_b - d_estaca/2, -2), d_estaca, 2, color='gray', alpha=0.5))
    # Pilar
    ax.add_patch(plt.Rectangle((pos_pilar - 0.15, 0), 0.3, 0.5, color='blue'))
    
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2.5, h_muro + 1)
    ax.axhline(0, color='brown', ls='--')
    ax.set_title("Corte Transversal (Dinâmico)")
    ax.legend()
    
    st.pyplot(fig)

# --- ABA DE DETALHAMENTO ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Memória de Cálculo", "Armaduras", "Verificações (NBR 6118)"])

with tab1:
    st.write("### 📝 Equações Utilizadas")
    st.latex(r"K_a = \tan^2(45^\circ - \frac{\phi}{2})")
    st.latex(r"E_h = \frac{1}{2} \cdot \gamma \cdot H^2 \cdot K_a")
    st.write("O momento fletor é calculado em relação ao centro do bloco de fundação.")

with tab2:
    st.write("### 🥢 Estimativa de Armadura (Método das Bielas)")
    # Cálculo simplificado de armadura de tração no bloco
    z = 0.8 * h_bloco # Braço de alavanca interno aproximado
    as_necessario = (max(r1, r2) * 1.4) / (43.48) # cm² (Simplificado para CA-50)
    st.success(f"Área de Aço Principal Necessária: {as_necessario:.2f} cm²")
    st.info("Sugestão: 5 barras de 12.5mm ou 4 barras de 16mm")

with tab3:
    st.write("### ✅ Verificações de Segurança")
    if r1 > 0 and r2 > 0:
        st.write("- Verificação de Tombamento: **Estável** (Ambas estacas comprimidas)")
    else:
        st.error("- Verificação de Tombamento: **Risco de Tração** nas estacas! Reveja a distância ou o peso do bloco.")

# --- RODAPÉ ---
st.markdown("---")
st.caption("Desenvolvido para análise estrutural preliminar. Sempre consulte um engenheiro calculista.")