import streamlit as st
import pandas as pd
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------

st.set_page_config(
    page_title="Gestión de Flotas",
    layout="wide"
)

if "login" not in st.session_state:
    st.session_state.login = False

if "ruta_optima" not in st.session_state:
    st.session_state.ruta_optima = []

# ---------------------------------------------------
# TÍTULO
# ---------------------------------------------------

st.title("🚛 Plataforma de Gestión de Flotas")

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

if not st.session_state.login:

    st.subheader("🔐 Iniciar Sesión")

    usuario = st.text_input("Usuario")

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Ingresar"):

        conn = sqlite3.connect("flota.db")

        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM usuarios
        WHERE usuario=? AND password=?
        """, (usuario, password))

        resultado = cursor.fetchone()

        conn.close()

        if resultado:

            st.session_state.login = True

            st.success(
                "Inicio de sesión exitoso 😎"
            )

            st.rerun()

        else:

            st.error(
                "Usuario o contraseña incorrectos"
            )

# ---------------------------------------------------
# SISTEMA PRINCIPAL
# ---------------------------------------------------

else:

    # ---------------------------------------------------
    # MENÚ
    # ---------------------------------------------------

    menu = st.sidebar.selectbox(
        "Menú",
        [
            "Inicio",
            "Pedidos",
            "Despacho",
            "Entregas",
            "Vehículos",
            "Rutas",
            "Optimización",
            "Mapa",
            "Historial",
            "Finalizar Viaje",
            "Reportes",
            "Dashboard"
        ]
    )

    # ---------------------------------------------------
    # INICIO
    # ---------------------------------------------------

    if menu == "Inicio":

        st.header("😎 Bienvenido al Sistema")

        st.write("""
        Esta plataforma permite:

        - Registrar vehículos
        - Gestionar rutas
        - Optimizar recorridos
        - Calcular costos logísticos
        - Visualizar mapas
        - Generar reportes
        """)

# ---------------------------------------------------
# PEDIDOS
# ---------------------------------------------------

    elif menu == "Pedidos":

        st.header("📦 Gestión de Pedidos")

        # REGISTRO

        st.subheader("➕ Registrar Pedido")

        cliente = st.text_input("Cliente")

        origen = st.text_input("Origen")

        destino = st.text_input("Destino")

        peso = st.number_input(
            "Peso (kg)",
            min_value=1.0
        )

        estado = st.selectbox(
           "Estado",
           [
             "Pendiente",
             "En tránsito",
             "Entregado"
           ]
        )

        if st.button("Registrar Pedido"):

         conn = sqlite3.connect("flota.db")

         cursor = conn.cursor()

         cursor.execute("""
         INSERT INTO pedidos (
            cliente,
            origen,
            destino,
            peso,
            estado
         )
         VALUES (?, ?, ?, ?, ?)
         """, (
            cliente,
            origen,
            destino,
            peso,
            estado
         ))

         conn.commit()

         conn.close()

         st.success(
            "Pedido registrado 😎"
         )

     # MOSTRAR PEDIDOS

        conn = sqlite3.connect("flota.db")

        df_pedidos = pd.read_sql_query(
        "SELECT * FROM pedidos",
        conn
        )

        conn.close()

        st.subheader("📋 Pedidos Registrados")

        st.dataframe(df_pedidos)

# ---------------------------------------------------
# DESPACHO
# ---------------------------------------------------

    elif menu == "Despacho":

        st.header("🚚 Despacho Automático")

        conn = sqlite3.connect("flota.db")

        df_pedidos = pd.read_sql_query(
            """
            SELECT * FROM pedidos
            WHERE estado='Pendiente'
            """,
            conn
        )

        df_vehiculos = pd.read_sql_query(
            """
            SELECT * FROM vehiculos
            WHERE estado='Disponible'
            """,
            conn
        )

        if len(df_pedidos) > 0:

            pedidos_ids = df_pedidos["id"].tolist()

            pedido_id = st.selectbox(
                "Selecciona Pedido",
                pedidos_ids
            )

            pedido = df_pedidos[
                df_pedidos["id"] == pedido_id
            ].iloc[0]

            st.info(
                f"Cliente: {pedido['cliente']}"
            )

            st.info(
                f"Carga: {pedido['peso']} kg"
            )
 
            if st.button("Despachar Pedido"):

                capacidades = {
                    "Moto": 50,
                    "Automóvil": 200,
                    "Van": 1000,
                    "Camión": 5000
                }

                vehiculo_asignado = None

                mejor_capacidad = float("inf")

                for index, row in df_vehiculos.iterrows():

                    tipo = row["tipo"]

                    if tipo in capacidades:

                        capacidad = capacidades[tipo]

                        if pedido["peso"] <= capacidad:

                             if capacidad < mejor_capacidad:

                                mejor_capacidad = capacidad

                                vehiculo_asignado = row

                if vehiculo_asignado is not None:

                    cursor = conn.cursor()

                    # Actualizar pedido
                    cursor.execute("""
                    UPDATE pedidos
                    SET estado='En tránsito',
                        vehiculo=?
                    WHERE id=?
                    """, (
                        vehiculo_asignado["placa"],
                        pedido_id
                    ))

                    # Actualizar vehículo
                    cursor.execute("""
                    UPDATE vehiculos
                    SET estado='En ruta'
                    WHERE id=?
                    """, (
                        vehiculo_asignado["id"],
                    ))

                    conn.commit()

                    st.success(
                        f"Pedido despachado con vehículo {vehiculo_asignado['placa']} 😎"
                    )

                else:

                    st.error(
                        "No hay vehículos disponibles para ese pedido"
                    )

        else:

            st.info(
                "No hay pedidos pendientes"
            )

        conn.close()
# ---------------------------------------------------
# ENTREGAS
# ---------------------------------------------------

    elif menu == "Entregas":

        st.header("📦 Gestión de Entregas")

        conn = sqlite3.connect("flota.db")

        df_entregas = pd.read_sql_query(
            """
            SELECT * FROM pedidos
            WHERE estado='En tránsito'
            """,
            conn
        )

        if len(df_entregas) > 0:

            ids = df_entregas["id"].tolist()

            pedido_id = st.selectbox(
                "Selecciona Pedido",
                ids
            )

            pedido = df_entregas[
                df_entregas["id"] == pedido_id
            ].iloc[0]

            st.info(
                f"Cliente: {pedido['cliente']}"
            )

            st.info(
                f"Vehículo: {pedido['vehiculo']}"
            )

            if st.button("Confirmar Entrega"):

                cursor = conn.cursor()

                # Pedido entregado
                cursor.execute("""
                UPDATE pedidos
                SET estado='Entregado'
                WHERE id=?
                """, (
                    pedido_id,
                ))

                # Liberar vehículo
                cursor.execute("""
                UPDATE vehiculos
                SET estado='Disponible'
                WHERE placa=?
                """, (
                    pedido["vehiculo"],
                ))

                conn.commit()

                st.success(
                    "Entrega confirmada 😎"
                )

        else:

            st.info(
                "No hay entregas activas"
            )

        conn.close()

    # ---------------------------------------------------
    # VEHÍCULOS
    # ---------------------------------------------------

    elif menu == "Vehículos":

        st.header("🚚 Gestión de Vehículos")

        # REGISTRO

        st.subheader("➕ Registrar Vehículo")

        placa = st.text_input("Placa")

        tipo = st.selectbox(
            "Tipo",
            ["Camión", "Van", "Moto", "Automóvil"]
        )

        estado = st.selectbox(
            "Estado",
            ["Disponible", "En ruta", "Mantenimiento"]
        )
        kilometraje = st.number_input(
            "Kilometraje",
            min_value=0.0,
            value=0.0
        )

        if st.button("Registrar Vehículo"):

            conn = sqlite3.connect("flota.db")

            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO vehiculos (
                placa,
                tipo,
                estado,
                kilometraje
            )
            VALUES (?, ?, ?, ?)
            """, (placa, tipo, estado, kilometraje))

            conn.commit()

            conn.close()

            st.success("Vehículo registrado 😎")

        # MOSTRAR TABLA

        conn = sqlite3.connect("flota.db")

        df = pd.read_sql_query(
            "SELECT * FROM vehiculos",
            conn
        )

        st.subheader("📋 Vehículos Registrados")

        st.dataframe(df)

        ids = df["id"].tolist()

        # ACTUALIZAR

        st.subheader("✏️ Actualizar Estado")

        if ids:

            vehiculo_id = st.selectbox(
                "Selecciona ID",
                ids
            )

            nuevo_estado = st.selectbox(
                "Nuevo Estado",
                ["Disponible", "En ruta", "Mantenimiento"]
            )

            if st.button("Actualizar Estado"):

                cursor = conn.cursor()

                cursor.execute("""
                UPDATE vehiculos
                SET estado=?
                WHERE id=?
                """, (nuevo_estado, vehiculo_id))

                conn.commit()

                st.success("Estado actualizado 🔥")

        # ELIMINAR

        st.subheader("🗑️ Eliminar Vehículo")

        if ids:

            eliminar_id = st.selectbox(
                "ID a eliminar",
                ids
            )

            if st.button("Eliminar Vehículo"):

                cursor = conn.cursor()

                cursor.execute("""
                DELETE FROM vehiculos
                WHERE id=?
                """, (eliminar_id,))

                conn.commit()

                st.warning("Vehículo eliminado")

        conn.close()

    # ---------------------------------------------------
    # RUTAS
    # ---------------------------------------------------

    elif menu == "Rutas":

        st.header("🛣️ Gestión de Rutas")

        origen = st.text_input("Origen")

        destino = st.text_input("Destino")

        distancia = st.number_input(
            "Distancia (km)",
            min_value=0.0
        )

        if st.button("Registrar Ruta"):

            conn = sqlite3.connect("flota.db")

            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO rutas (
                origen,
                destino,
                distancia
            )
            VALUES (?, ?, ?)
            """, (origen, destino, distancia))

            conn.commit()

            conn.close()

            st.success("Ruta registrada 😎")

        # MOSTRAR RUTAS

        conn = sqlite3.connect("flota.db")

        df_rutas = pd.read_sql_query(
            "SELECT * FROM rutas",
            conn
        )

        st.subheader("📍 Rutas Registradas")

        st.dataframe(df_rutas)

        conn.close()

    # ---------------------------------------------------
    # OPTIMIZACIÓN
    # ---------------------------------------------------

    elif menu == "Optimización":

        st.header("📈 Optimización de Rutas")

        conn = sqlite3.connect("flota.db")

        df_rutas = pd.read_sql_query(
            "SELECT * FROM rutas",
            conn
        )

        conn.close()

        G = nx.Graph()

        for index, row in df_rutas.iterrows():

            G.add_edge(
                row["origen"],
                row["destino"],
                weight=row["distancia"]
            )

        nodos = list(G.nodes())

        if len(nodos) > 0:

            origen = st.selectbox(
                "Selecciona origen",
                nodos
            )

            destino = st.selectbox(
                "Selecciona destino",
                nodos
            )

            rendimiento = st.number_input(
                "Rendimiento del vehículo (km/L)",
                min_value=1.0,
                value=10.0
            )

            precio_combustible = st.number_input(
                "Precio combustible ($/L)",
                min_value=1.0,
                value=16000.0
            )

            velocidad = st.number_input(
                "Velocidad promedio (km/h)",
                min_value=1.0,
                value=80.0
            )

            carga = st.number_input(
                "Carga requerida (kg)",
                min_value=1
            )

            if st.button("Calcular Ruta Óptima"):

                try:

                    ruta = nx.shortest_path(
                        G,
                        source=origen,
                        target=destino,
                        weight="weight"
                    )

                    distancia_total = nx.shortest_path_length(
                        G,
                        source=origen,
                        target=destino,
                        weight="weight"
                    )

                    st.success(
                        f"Ruta óptima: {' → '.join(ruta)}"
                    )

                    st.session_state.ruta_optima = ruta

                    st.info(
                        f"Distancia total: {distancia_total} km"
                    )

                    # COSTOS

                    litros = distancia_total / rendimiento

                    costo = litros * precio_combustible

                    st.metric(
                        "⛽ Combustible Estimado",
                        f"{round(litros, 2)} L"
                    )

                    st.metric(
                        "💰 Costo Estimado",
                        f"${round(costo, 2)}"
                    )

                    # TIEMPO

                    tiempo_horas = distancia_total / velocidad

                    horas = int(tiempo_horas)

                    minutos = int(
                        (tiempo_horas - horas) * 60
                    )

                    st.metric(
                        "⏱️ Tiempo Estimado",
                        f"{horas} h {minutos} min"
                    )

                    # VEHÍCULOS

                    conn = sqlite3.connect("flota.db")

                    df_vehiculos = pd.read_sql_query(
                        "SELECT * FROM vehiculos",
                        conn
                    )

                    disponibles = df_vehiculos[
                        df_vehiculos["estado"] == "Disponible"
                    ]

                    capacidades = {
                        "Moto": 50,
                        "Automóvil": 200,
                        "Van": 1000,
                        "Camión": 5000
                    }

                    vehiculo_asignado = None

                    mejor_capacidad = float("inf")

                    for index, row in disponibles.iterrows():

                        tipo_vehiculo = row["tipo"]

                        if tipo_vehiculo in capacidades:

                            capacidad = capacidades[tipo_vehiculo]

                            if carga <= capacidad:

                                if capacidad < mejor_capacidad:

                                    mejor_capacidad = capacidad

                                    vehiculo_asignado = row

                    if vehiculo_asignado is not None:

                        st.success(
                            f"🚚 Vehículo asignado: {vehiculo_asignado['placa']}"
                        )

                        st.info(
                            f"Tipo: {vehiculo_asignado['tipo']}"
                        )

                        st.info(
                            f"Capacidad máxima: {capacidades[vehiculo_asignado['tipo']]} kg"
                        )
                        # SUMAR KILÓMETROS

                        nuevo_km = (
                            vehiculo_asignado["kilometraje"]
                            + distancia_total
                        )

                        nuevo_estado = "En ruta"

                        # Si supera límite
                        if nuevo_km >= 5000:

                            nuevo_estado = "Mantenimiento"

                        # CAMBIAR ESTADO

                        cursor = conn.cursor()

                        cursor.execute("""
                        UPDATE vehiculos
                        SET estado=?,
                            kilometraje=?
                        WHERE id=?
                        """, (
                                nuevo_estado,
                                nuevo_km,
                                vehiculo_asignado["id"]
                             ))

                        conn.commit()

                        st.warning(
                            "Estado actualizado a: En ruta 🚛"
                        )

                        # GUARDAR VIAJE

                        tiempo_texto = f"{horas} h {minutos} min"

                        cursor.execute("""
                        INSERT INTO viajes (
                            origen,
                            destino,
                            vehiculo,
                            distancia,
                            costo,
                            tiempo
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            origen,
                            destino,
                            vehiculo_asignado["placa"],
                            distancia_total,
                            costo,
                            tiempo_texto
                        ))

                        conn.commit()

                        st.success(
                            "Viaje guardado en historial 📦"
                        )

                    else:

                        st.error(
                            "No hay vehículos adecuados para esa carga"
                        )

                    conn.close()

                    # GRAFO

                    fig, ax = plt.subplots(
                        figsize=(8, 6)
                    )

                    pos = nx.spring_layout(G)

                    nx.draw(
                        G,
                        pos,
                        with_labels=True,
                        node_size=3000,
                        font_size=10,
                        ax=ax
                    )

                    labels = nx.get_edge_attributes(
                        G,
                        "weight"
                    )

                    nx.draw_networkx_edge_labels(
                        G,
                        pos,
                        edge_labels=labels
                    )

                    st.pyplot(fig)

                except:

                    st.error(
                        "No existe conexión entre los nodos"
                    )

    # ---------------------------------------------------
    # MAPA
    # ---------------------------------------------------

    elif menu == "Mapa":

        st.header("🗺️ Mapa Logístico")

        mapa = folium.Map(
            location=[10.4, -75.5],
            zoom_start=6
        )

        ciudades = {
            "Cartagena": [10.3910, -75.4794],
            "Barranquilla": [10.9685, -74.7813],
            "Santa Marta": [11.2408, -74.1990],
            "Sincelejo": [9.3047, -75.3978]
        }

        conn = sqlite3.connect("flota.db")

        df_rutas = pd.read_sql_query(
            "SELECT * FROM rutas",
            conn
        )
        df_pedidos = pd.read_sql_query(
            """
            SELECT * FROM pedidos
            WHERE estado='En tránsito'
            """,
            conn
        )

        conn.close()

        # CIUDADES

        for ciudad, coord in ciudades.items():

            folium.Marker(
                location=coord,
                popup=ciudad
            ).add_to(mapa)

        # RUTAS

        for index, row in df_rutas.iterrows():

            origen = row["origen"]
            destino = row["destino"]

            if origen in ciudades and destino in ciudades:

                folium.PolyLine(
                    locations=[
                        ciudades[origen],
                        ciudades[destino]
                    ],
                    tooltip=f"{origen} → {destino}",
                    weight=5
                ).add_to(mapa)

        # RUTA ÓPTIMA

        ruta_optima = st.session_state.ruta_optima

        if len(ruta_optima) > 1:

            for i in range(len(ruta_optima) - 1):

                origen = ruta_optima[i]
                destino = ruta_optima[i + 1]

                if origen in ciudades and destino in ciudades:

                    folium.PolyLine(
                        locations=[
                            ciudades[origen],
                            ciudades[destino]
                        ],
                        tooltip="Ruta Óptima",
                        weight=8,
                        color="red"
                    ).add_to(mapa)

    # ------------------------------------------------
    # VEHÍCULOS EN TRÁNSITO
    # ------------------------------------------------

        for index, row in df_pedidos.iterrows():

            origen = row["origen"]

            destino = row["destino"]

            vehiculo = row["vehiculo"]

            if origen in ciudades and destino in ciudades:

                origen_coord = ciudades[origen]

                destino_coord = ciudades[destino]

                # Punto medio simulando movimiento
                lat = (
                    origen_coord[0]
                    + destino_coord[0]
                ) / 2

                lon = (
                    origen_coord[1]
                    + destino_coord[1]
                ) / 2

                folium.Marker(
                    location=[lat, lon],
                    popup=f"Vehículo: {vehiculo}",
                    tooltip=f"Pedido hacia {destino}",
                    icon=folium.Icon(
                        color="red",
                        icon="truck",
                        prefix="fa"
                    )
                ).add_to(mapa)

            st_folium(
                mapa,
                width=900,
                height=500
            )
 
    # ---------------------------------------------------
    # HISTORIAL
    # ---------------------------------------------------

    elif menu == "Historial":

        st.header("📦 Historial de Viajes")

        conn = sqlite3.connect("flota.db")

        df_viajes = pd.read_sql_query(
            "SELECT * FROM viajes",
            conn
        )

        conn.close()

        st.dataframe(df_viajes)

    # ---------------------------------------------------
    # FINALIZAR VIAJE
    # ---------------------------------------------------

    elif menu == "Finalizar Viaje":

        st.header("✅ Finalizar Viajes")

        conn = sqlite3.connect("flota.db")

        df_vehiculos = pd.read_sql_query(
            "SELECT * FROM vehiculos",
            conn
        )

        en_ruta = df_vehiculos[
            df_vehiculos["estado"] == "En ruta"
        ]

        if len(en_ruta) > 0:

            placas = en_ruta["placa"].tolist()

            placa = st.selectbox(
                "Vehículo",
                placas
            )

            if st.button("Finalizar Viaje"):

                cursor = conn.cursor()

                cursor.execute("""
                UPDATE vehiculos
                SET estado='Disponible'
                WHERE placa=?
                """, (placa,))

                conn.commit()

                st.success(
                    f"Vehículo {placa} disponible nuevamente 😎"
                )

        else:

            st.info(
                "No hay vehículos en ruta"
            )

        conn.close()

    # ---------------------------------------------------
    # REPORTES
    # ---------------------------------------------------

    elif menu == "Reportes":

        st.header("📄 Exportar Reportes")

        conn = sqlite3.connect("flota.db")

        df_viajes = pd.read_sql_query(
            "SELECT * FROM viajes",
            conn
        )

        conn.close()

        st.subheader("📦 Historial de Viajes")

        st.dataframe(df_viajes)

        archivo = "reporte_viajes.xlsx"

        df_viajes.to_excel(
            archivo,
            index=False
        )

        with open(archivo, "rb") as file:

            st.download_button(
                label="⬇️ Descargar Reporte Excel",
                data=file,
                file_name="reporte_viajes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ---------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------

    elif menu == "Dashboard":

       st.header("📊 Dashboard Logístico")

       st.subheader("🚨 Alertas Inteligentes")


        conn = sqlite3.connect("flota.db")

        df_viajes = pd.read_sql_query(
            "SELECT * FROM viajes",
            conn
        )

        df = pd.read_sql_query(
            "SELECT * FROM vehiculos",
            conn
        )

        df_pedidos = pd.read_sql_query(
            "SELECT * FROM pedidos",
            conn
        )

        conn.close()

        total = len(df_vehiculos)

        disponibles = len(
            df_vehiculos[
                df_vehiculos["estado"] == "Disponible"
            ]
        )

        ruta = len(
            df_vehiculos[
                df_vehiculos["estado"] == "En ruta"
            ]
        )

        mantenimiento = len(
            df_vehiculos[
                df_vehiculos["estado"] == "Mantenimiento"
            ]
        )

        st.metric(
            "🚚 Total Vehículos",
            total
        )

        st.metric(
            "✅ Disponibles",
            disponibles
        )

        st.metric(
            "🛣️ En Ruta",
            ruta
        )

        st.metric(
            "🛠️ Mantenimiento",
            mantenimiento
        )

        st.bar_chart(
            df_vehiculos["estado"].value_counts()
        )

        # ---------------------------------
        # GRÁFICO ESTADOS VEHÍCULOS
        # ---------------------------------

        estados = df["estado"].value_counts()

        fig1 = px.pie(
            values=estados.values,
            names=estados.index,
            title="Estados de Vehículos"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )
        # ---------------------------------
        # PEDIDOS
        # ---------------------------------

        conn = sqlite3.connect("flota.db")

        df_pedidos = pd.read_sql_query(
            "SELECT * FROM pedidos",
            conn
        )

        conn.close()

        if len(df_pedidos) > 0:

            estados_pedidos = (
                df_pedidos["estado"]
                .value_counts()
            )

            fig2 = px.bar(
                x=estados_pedidos.index,
                y=estados_pedidos.values,
                title="Estados de Pedidos"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )
        # ---------------------------------
        # VEHÍCULOS MÁS USADOS
        # ---------------------------------

            if len(df_viajes) > 0:

             usados = (
                df_viajes["vehiculo"]
                .value_counts()
            )

            fig3 = px.bar(
                x=usados.index,
                y=usados.values,
                title="Vehículos Más Utilizados"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        # ---------------------------------
        # COSTOS LOGÍSTICOS
        # ---------------------------------

            if len(df_viajes) > 0:

             fig4 = px.line(
                df_viajes,
                y="costo",
                title="Evolución de Costos"
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

        # KPIs

       st.subheader("📈 KPIs Logísticos")

       total_viajes = len(df_viajes)

       st.metric(
            "📦 Total Viajes",
            total_viajes
        )

       if total_viajes > 0:

            costo_promedio = df_viajes["costo"].mean()

            distancia_promedio = df_viajes["distancia"].mean()

            mas_usado = df_viajes[
                "vehiculo"
            ].value_counts().idxmax()

            ocupados = len(
                df_vehiculos[
                    df_vehiculos["estado"] == "En ruta"
                ]
            )

            utilizacion = (
                ocupados / total
            ) * 100 if total > 0 else 0

            st.metric(
                "💰 Costo Promedio",
                f"${round(costo_promedio, 2)}"
            )

            st.metric(
                "🛣️ Distancia Promedio",
                f"{round(distancia_promedio, 2)} km"
            )

            st.metric(
                "🚚 Vehículo Más Usado",
                mas_usado
            )
            mantenimiento_alerta = df_vehiculos[
            df_vehiculos["kilometraje"] >= 5000
        ]

            if len(mantenimiento_alerta) > 0:

             st.warning(
                f"⚠️ {len(mantenimiento_alerta)} vehículo(s) requieren mantenimiento"
            )
            ocupados_alerta = len(
            df_vehiculos[
                df_vehiculos["estado"] == "En ruta"
            ]
        )

            total_alerta = len(df_vehiculos)

            if total_alerta > 0:

             porcentaje = (
                ocupados_alerta / total_alerta
            ) * 100

            if porcentaje >= 80:

                st.warning(
                    f"🚚 Alta utilización de flota: {round(porcentaje, 2)}%"
                )

            st.metric(
                "📊 Utilización Flota",
                f"{round(utilizacion, 2)}%"
            )