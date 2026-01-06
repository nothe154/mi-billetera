import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px  # Necesitaremos instalar esto: pip install plotly

# Configuración de la página
st.set_page_config(page_title="Mi Billetera 2.0", layout="centered")
st.title("📱 Control de Gastos & Ahorro")

# NOMBRE DEL ARCHIVO DONDE SE GUARDAN LOS DATOS
ARCHIVO_DATOS = 'mis_gastos.csv'

# 1. Función para Cargar Datos
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        return pd.read_csv(ARCHIVO_DATOS)
    else:
        return pd.DataFrame(columns=["Fecha", "Descripción", "Monto", "Categoría", "Tipo"])

# 2. Función para Guardar Datos
def guardar_datos(nuevo_df):
    nuevo_df.to_csv(ARCHIVO_DATOS, index=False)

# 3. Lógica Inteligente de Categorías
def categorizar_gasto(descripcion):
    desc = descripcion.lower()
    # Transporte y Vehículo
    if any(x in desc for x in ['gasolina', 'combustible', 'peaje', 'aceite', 'llanta']):
        return "Vehículo", "Necesario (Pero optimizable) 🚗"
    elif any(x in desc for x in ['uber', 'taxi', 'didi', 'bus', 'transmilenio', 'metro']):
        return "Transporte", "Necesario 🚌"
    # Hormiga y Ocio
    elif any(x in desc for x in ['helado', 'café', 'postre', 'cerveza', 'cigarrillo', 'gaseosa']):
        return "Antojo", "Hormiga 🐜"
    elif any(x in desc for x in ['cine', 'fiesta', 'licor', 'salida', 'restaurante']):
        return "Ocio", "Discrecional 🥂"
    # Hogar
    elif any(x in desc for x in ['arriendo', 'luz', 'agua', 'gas', 'mercado', 'internet']):
        return "Hogar", "Obligatorio 🏠"
    else:
        return "Varios", "General 📝"

# --- INTERFAZ ---

# Cargar historial
df = cargar_datos()

# Pestañas para organizar la app
tab1, tab2, tab3 = st.tabs(["📝 Registrar", "📊 Estadísticas", "💡 Consejos"])

with tab1:
    st.subheader("Nuevo Gasto")
    with st.form("entrada_gastos"):
        fecha = st.date_input("Fecha", datetime.date.today())
        desc = st.text_input("Descripción (Ej: Gasolina, Uber, Helado)")
        monto = st.number_input("Valor ($)", min_value=0, step=1000)
        submitted = st.form_submit_button("Guardar Gasto")

        if submitted and desc and monto > 0:
            cat, tipo = categorizar_gasto(desc)
            nuevo_registro = pd.DataFrame({
                "Fecha": [fecha],
                "Descripción": [desc],
                "Monto": [monto],
                "Categoría": [cat],
                "Tipo": [tipo]
            })
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            guardar_datos(df) # GUARDAR EN ARCHIVO
            st.success(f"¡Listo! ${monto:,.0f} en {cat} guardado.")
            st.rerun() # Recarga la página para actualizar datos

with tab2:
    if not df.empty:
        st.subheader("¿Dónde se va tu dinero?")
        
        # Gráfico de Torta por Categoría
        fig = px.pie(df, values='Monto', names='Categoría', title='Distribución de Gastos')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
        
        # Total Gastado
        total = df['Monto'].sum()
        hormiga = df[df['Tipo'].str.contains("Hormiga")]['Monto'].sum()
        st.metric("Total Gastado", f"${total:,.0f}")
        st.metric("Gastos Hormiga Totales", f"${hormiga:,.0f}", delta_color="inverse")
    else:
        st.info("Aún no tienes gastos registrados.")

with tab3:
    st.subheader("Tu Entrenador Financiero")
    if not df.empty:
        hormiga = df[df['Tipo'].str.contains("Hormiga")]['Monto'].sum()
        vehiculo = df[df['Categoría'] == "Vehículo"]['Monto'].sum()
        
        if hormiga > 50000:
            st.warning(f"🐜 ¡Cuidado! Llevas ${hormiga:,.0f} en gastos hormiga. Eso equivale a {(hormiga/10000):.0f} empanadas o pasajes.")
        
        if vehiculo > 200000:
            st.info(f"🚗 Tu vehículo te ha costado ${vehiculo:,.0f}. Revisa presión de llantas y filtros para ahorrar gasolina.")
            
        st.markdown("""
        **Tips Generales:**
        * Si sales a beber, define un presupuesto en efectivo antes de salir.
        * Usa transporte público 1 o 2 veces por semana en vez de Uber.
        * Lleva termo con agua, evita comprar botellas en la calle.
        """)