# -*- coding: utf-8 -*-
import streamlit as st
import psycopg2

st.set_page_config(page_title="Admin - Registro de Usuarios SAP MVP", page_icon="🔑")

# 1. CONEXIÓN A LA BASE DE DATOS EN LA NUBE
# Lee las credenciales de forma segura desde los Secrets de Streamlit
def conectar_db():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"]
    )

# 2. CREACIÓN DE TABLA AUTOMÁTICA (Si no existe)
def inicializar_base_datos():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_sap (
                usuario VARCHAR(50) PRIMARY KEY,
                contrasena VARCHAR(50) NOT NULL,
                empresa VARCHAR(100) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error de infraestructura: {e}")

inicializar_base_datos()

# 3. INTERFAZ VISUAL DE REGISTRO
st.title("🛡️ Panel de Administración — Alta de Clientes SAP")
st.markdown("Utilizá este formulario para registrar nuevos usuarios habilitados para consumir el MVP.")
st.divider()

col1, _ = st.columns(2)

with col1:
    input_empresa = st.text_input("Nombre de la Empresa", placeholder="Ej: Electrosur SA")
    input_usuario = st.text_input("Nombre de Usuario (ID de acceso)", placeholder="Ej: carlos12")
    input_pass = st.text_input("Contraseña", type="password", placeholder="Ej: clave1234")
    
    boton_guardar = st.button("💾 Registrar en Base de Datos", use_container_width=True)

if boton_guardar:
    if not input_empresa or not input_usuario or not input_pass:
        st.warning("Todos los campos son obligatorios para dar de alta.")
    else:
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            
            # Verificamos si el usuario ya existe para evitar duplicados
            cursor.execute("SELECT usuario FROM usuarios_sap WHERE usuario = %s", (input_usuario,))
            if cursor.fetchone():
                st.error(f"El usuario '{input_usuario}' ya se encuentra registrado.")
            else:
                # Insertamos el nuevo cliente
                cursor.execute(
                    "INSERT INTO usuarios_sap (usuario, contrasena, empresa) VALUES (%s, %s, %s)",
                    (input_usuario, input_pass, input_empresa)
                )
                conn.commit()
                st.success(f"¡Éxito! El usuario '{input_usuario}' de '{input_empresa}' fue dado de alta correctamente.")
                
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error al guardar en la base de datos: {e}")
