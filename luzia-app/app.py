import streamlit as st
import csv
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

# ---------------------
# CONFIGURACIÓN
# ---------------------
COSTO_POR_KWH_USD = 0.15
PRESUPUESTO_USD = 50
TASA_CAMBIO = 1000

st.set_page_config(
    page_title="LuzIA - App de Consumo de Luz",
    layout="centered",
    page_icon="💡"
)

# ---------------------
# ENCABEZADO Y GUÍA
# ---------------------
st.markdown("""
<style>
.header {
    background-color: #f0f2f6;
    padding: 1.5rem;
    border-radius: 1rem;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}
.header h1 {
    color: #333333;
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.header p {
    color: #555;
    font-size: 1rem;
    margin: 0.3rem 0;
}
.footer {
    margin-top: 2rem;
    padding: 1rem;
    font-size: 0.9rem;
    text-align: center;
    color: #888;
}
</style>

<div class="header">
    <h1>💡 LuzIA - App de Consumo de Luz</h1>
    <p><strong>¿Cómo usar esta app?</strong></p>
    <p>1. Seleccioná tu moneda (USD o ARS) para continuar.</p>
    <p>Luego, se desbloquearán las siguientes secciones paso a paso.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------
# AVISO LEGAL Y AUTORÍA
# ---------------------
st.markdown("""
<hr style='margin-top:2rem;margin-bottom:1rem'>
<div class="footer">
    <p>🛡️ Esta app no recopila datos personales. Toda la información ingresada se guarda localmente en tu dispositivo o entorno de ejecución.</p>
    <p>📌 LuzIA es una herramienta educativa para estimar el consumo energético. Las recomendaciones son orientativas y no reemplazan el asesoramiento profesional.</p>
    <p>🧠 Este es un proyecto independiente desarrollado con fines educativos y experimentales. Su uso es gratuito.</p>
    <p>© 2025 LuzIA – Desarrollado por <strong>LuzIA Labs</strong>. Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------
# SELECCIÓN DE MONEDA
# ---------------------
st.markdown("## Paso 1: Seleccioná tu moneda")
moneda = st.radio("\U0001F4B1 Visualizar en:", ["USD", "ARS"])
if moneda:
    usar_usd = moneda == "USD"
    simbolo = "USD" if usar_usd else "ARS"
    tasa = 1 if usar_usd else TASA_CAMBIO

    st.success(f"Seleccionaste {moneda}. Ahora podés ingresar tus datos de consumo.")

    # Mostrar sección de guía de consumo
    with st.expander("\U0001F4CB ¿No sabés cuánto consume cada cosa? Estimá acá"):
        st.markdown("""
        **Consumo promedio por hora de uso:**
        - Aire acondicionado: 1.5 kWh/h
        - Foco LED: 0.01 kWh/h (por unidad)
        - TV: 0.15 kWh/h
        - PC de escritorio: 0.25 kWh/h
        - Heladera: ~1.2 kWh/día
        - Lavarropas: 0.6 kWh por ciclo

        Estos valores son estimaciones. Si querés calcularlo, sumá:
        `potencia del equipo (kW) × horas de uso diario × días del mes`
        """)

    st.markdown("## Paso 2: Ingresá tu consumo mensual por categoría")

    mes = st.selectbox("\U0001F4C5 Seleccioná el mes:", [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])

    aire = st.number_input("Aire acondicionado (kWh)", min_value=0.0, step=1.0)
    luces = st.number_input("Iluminación (kWh)", min_value=0.0, step=1.0)
    otros = st.number_input("Otros dispositivos (kWh)", min_value=0.0, step=1.0)

    mes_anterior = st.number_input("\U0001F522 Consumo total del mes anterior (kWh)", min_value=0.0, step=1.0)

    if st.button("\U0001F4CA Analizar consumo"):
        st.markdown("## Paso 3: Resultados y análisis")

        mes_actual = aire + luces + otros
        diferencia_kwh = mes_actual - mes_anterior
        costo_anterior_usd = mes_anterior * COSTO_POR_KWH_USD
        costo_actual_usd = mes_actual * COSTO_POR_KWH_USD
        diferencia_usd = costo_actual_usd - costo_anterior_usd

        presupuesto = PRESUPUESTO_USD * tasa
        costo_actual = costo_actual_usd * tasa
        costo_anterior = costo_anterior_usd * tasa
        diferencia = diferencia_usd * tasa
        ahorro_potencial = presupuesto - costo_actual

        st.write(f"**Diferencia de consumo:** {diferencia_kwh:.2f} kWh")
        st.write(f"**Costo anterior:** ${costo_anterior:.2f} {simbolo}")
        st.write(f"**Costo actual:** ${costo_actual:.2f} {simbolo}")
        st.write(f"**Diferencia:** {'+' if diferencia > 0 else '-'}${abs(diferencia):.2f} {simbolo}")

        if costo_actual > presupuesto:
            st.error(f"🚨 Superás tu presupuesto en ${costo_actual - presupuesto:.2f} {simbolo}")
        elif costo_actual < presupuesto:
            st.success(f"✅ Estás dentro del presupuesto. Te sobran ${ahorro_potencial:.2f} {simbolo}")
        else:
            st.info("⚖️ Estás justo en el límite del presupuesto.")

        # Guardar
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        with open("historial_consumo.csv", mode="a", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([fecha_actual, mes, aire, luces, otros, costo_actual_usd])

        # Recomendaciones
        if diferencia_kwh > 0:
            st.markdown("## 💡 Recomendaciones para ahorrar")
            if aire > luces and aire > otros:
                st.write("- Reducí el uso del aire acondicionado.")
            elif luces > aire and luces > otros:
                st.write("- Aprovechá más la luz natural.")
            else:
                st.write("- Apagá los dispositivos que no estés usando.")
        elif diferencia_kwh < 0:
            st.markdown("## ✅ ¡Buen trabajo!")
            st.write("Tu consumo bajó respecto al mes anterior. Seguí así.")

        # Gráfico de categoría
        st.markdown("## 📊 Detalle del consumo por categoría")
        etiquetas = ["Aire acondicionado", "Iluminación", "Otros"]
        valores = [aire, luces, otros]
        fig2, ax2 = plt.subplots()
        ax2.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)

        # Predicción IA
        st.markdown("## 🤖 Predicción IA del próximo mes")
        try:
            historial = pd.read_csv("historial_consumo.csv", header=None)
            consumos = historial[2] + historial[3] + historial[4]
            if len(consumos) >= 2:
                X = np.array(range(len(consumos))).reshape(-1, 1)
                y = np.array(consumos)
                modelo = LinearRegression()
                modelo.fit(X, y)
                siguiente_mes = np.array([[len(consumos)]])
                prediccion = modelo.predict(siguiente_mes)[0]
                st.write(f"Se estima un consumo de **{prediccion:.2f} kWh**.")
                costo_estimado = prediccion * COSTO_POR_KWH_USD * tasa
                st.write(f"Eso costaría aproximadamente **${costo_estimado:.2f} {simbolo}**.")
        except:
            st.info("No hay suficiente historial para predecir el siguiente mes.")

    # Mostrar historial
    st.markdown("## 📂 Historial de consumo")
    try:
        df_historial = pd.read_csv("historial_consumo.csv", header=None, on_bad_lines='skip')

        if isinstance(df_historial, pd.DataFrame) and df_historial.shape[1] == 6:
            df_historial.columns = ["Fecha", "Mes", "Aire (kWh)", "Luces (kWh)", "Otros (kWh)", "Costo (USD)"]
            st.dataframe(df_historial)

            csv = df_historial.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar historial como CSV",
                data=csv,
                file_name="historial_consumo.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ No se encontraron filas con formato válido (6 columnas).")
    except FileNotFoundError:
        st.warning("Todavía no hay historial guardado.")
