# EJERCICIO 1
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Rendimiento jugadores Mundial 2026', layout='wide')

# cargamos los datos del bloque 1
partidos = pd.read_excel("partidosWC26.xlsx")
eventos = pd.read_excel("eventosWC26.xlsx")
jugadores = pd.read_excel("jugadoresWC2026.xlsx")

#separamos los analisis en tabs
tab1, tab2, tab3 = st.tabs(["Análisis 1", "Análisis 2", "Análisis 3"])

# ponemos un título al gráfico
with tab1:
    st.title("Eventos del Mundial 2026")
    st.header("Análisis 1: Ventanas de Partidos")
    st.subheader("Ejercicio 1: Eventos por partido")

    # elegimos el partido que queremos analizar
    partido = st.selectbox("Selecciona un partido", partidos["index_partido"])

    # extraemos los eventos de ese partido
    eventos_partido = eventos[eventos["index_partido"] == partido].copy()
    eventos_partido["cantidad"] = 1

    # creamos el gráfico de barras
    graf_barras = px.bar(
        eventos_partido,
        x="minuto_evento",
        y="cantidad",
        color="tipo_evento",
        hover_name="nombre_jugador"
    )

    # mostramos el gráfico
    st.plotly_chart(graf_barras, width='stretch') # hemos tenido que preguntar a la IA por este comando


# -----------
# EJERCICIO 2: MAPA DE CALOR
with tab1:
    st.subheader("Ejercicio 2: Mapa de calor de eventos")

    # añadimos la ronda de cada partido a los eventos
    datos = pd.merge(eventos, partidos[["index_partido", "ronda"]], on="index_partido")

    # elegimos el tipo de evento que queremos analizar
    tipo = st.selectbox("Tipo de evento", ["Todos"] + list(datos["tipo_evento"].unique()))

    # elegimos la ronda del mundial
    ronda = st.selectbox("Ronda del Mundial", ["Todas"] + list(datos["ronda"].unique()))

    # filtramos según lo que haya elegido el usuario
    if tipo != "Todos":
        datos = datos[datos["tipo_evento"] == tipo]

    if ronda != "Todas":
        datos = datos[datos["ronda"] == ronda]

    # creamos el mapa de calor
    mapa_calor = px.density_heatmap(
        datos,
        x="minuto_evento",
        y="tipo_evento",
        nbinsx=13 # agrupamos los minutos en intervalos
    )

    st.plotly_chart(mapa_calor,width='stretch')



# ------
# EJERCICIO 3: GRÁFICO CIRCULAR

with tab1:
    st.subheader("Ejercicio 3: Eventos por selección")

    # elegimos una selección
    seleccion = st.selectbox("Selecciona una selección",sorted(partidos["seleccion_local"].unique()))

    # buscamos todos los partidos de esa selección (tanto en la local como en la visitante)
    partidos_seleccion = partidos[(partidos["seleccion_local"] == seleccion) |(partidos["seleccion_visitante"] == seleccion)]

    # buscamos los eventos de esos partidos
    eventos_seleccion = eventos[eventos["index_partido"].isin(partidos_seleccion["index_partido"])].copy()

    # distinguimos los eventos a favor y en contra
    eventos_seleccion["situacion"] = "En contra"

    eventos_seleccion.loc[eventos_seleccion["seleccion_evento"] == seleccion,"situacion"] = "A favor"

    # unimos el tipo de evento con su situación
    eventos_seleccion["categoria"] = (eventos_seleccion["tipo_evento"] +" " + eventos_seleccion["situacion"])

    # contamos cuántos eventos hay de cada categoría
    resumen = eventos_seleccion["categoria"].value_counts()

    # creamos el gráfico circular
    graf_circular = px.pie(
        names=resumen.index,
        values=resumen.values,
        title="Eventos de " + seleccion
    )

    st.plotly_chart(graf_circular,width='stretch')
    st.write(resumen) # mostramos las cantidades



# -----
# EJERCICIO 4: RENDIMIENTO DE JUGADORES

with tab2:
    st.header("Análisis 2: Rendimiento de jugadores")
    st.subheader("Ejercicio 4: Valor de mercado y calificación media")

    # seleccionamos los jugadores con al menos 180 minutos
    jugadores_180 = jugadores[jugadores["minutos_jugados"] >= 180]

    # creamos los filtros
    seleccion4 = st.selectbox("Selección nacional",["Todas"] + list(jugadores_180["seleccion_nacional"].unique()))
    partidos4 = st.selectbox("Partidos jugados",["Todos"] + sorted(jugadores_180["partidos_jugados"].unique()))
    posicion4 = st.selectbox("Posición del jugador",["Todas"] + list(jugadores_180["posicion"].unique()))


    if seleccion4 != "Todas":
        jugadores_180 = jugadores_180[jugadores_180["seleccion_nacional"] == seleccion4]

    if partidos4 != "Todos":
        jugadores_180 = jugadores_180[jugadores_180["partidos_jugados"] == partidos4]

    if posicion4 != "Todas":
        jugadores_180 = jugadores_180[jugadores_180["posicion"] == posicion4]

    # creamos el gráfico de dispersión
    if len(jugadores_180) > 0:
        graf_disp = px.scatter(
            jugadores_180,
            x="valor_mercado",
            y="calificacion_media",
            color="posicion",
            hover_name="nombre_jugador",
            title="Valor de mercado vs Calificación media"
        )

        st.plotly_chart(graf_disp,width='stretch')

        # calculamos la correlación
        if len(jugadores_180) > 1:
            correlacion = jugadores_180["valor_mercado"].corr(jugadores_180["calificacion_media"])
            st.write("Correlación:", round(correlacion, 2))
    else:
        st.write("No hay jugadores con estos filtros")


# -----
# EJERCICIO 5: MÉTRICAS POR MINUTO Y TOP 15
with tab2:
    st.subheader("Ejercicio 5: Métricas por minuto y Top 15")

    #calculamos el ranking de valor de mercado entre todos los jugadores del mundial
    jugadores["ranking_mercado"] = jugadores["valor_mercado"].rank(ascending=False, method="min").astype(int)

    # al igual que en el ej 4 filtro en 180 minutos o más, para que los jugadores con pocos minutos no dominen las estadisticas
    jugadores_metr = jugadores[jugadores["minutos_jugados"] >= 180].copy()

    # definimos las métricas por minuto pedidas en el enunciado
    jugadores_metr["goles/minuto"] = jugadores_metr["goles"] / jugadores_metr["minutos_jugados"]
    jugadores_metr["goles+asistencias/minuto"] = (jugadores_metr["goles"] + jugadores_metr["asistencias"]) / jugadores_metr["minutos_jugados"]
    jugadores_metr["asistencias/minuto"] = jugadores_metr["asistencias"] / jugadores_metr["minutos_jugados"]
    jugadores_metr["goles_concedidos/minuto"] = jugadores_metr["goles_concedidos"] / jugadores_metr["minutos_jugados"]
    jugadores_metr["tarjetas_amarillas/minuto"] = jugadores_metr["tarjetas_amarillas"] / jugadores_metr["minutos_jugados"]
    jugadores_metr["tarjetas_rojas/minuto"] = jugadores_metr["tarjetas_rojas"] / jugadores_metr["minutos_jugados"]

    # definimos la métrica agregada
    jugadores_metr["metrica_agregada"] = (
        jugadores_metr["goles/minuto"] * 50
        + jugadores_metr["goles+asistencias/minuto"] * 30
        + jugadores_metr["asistencias/minuto"] * 20
        - jugadores_metr["goles_concedidos/minuto"] * 25
        - jugadores_metr["tarjetas_amarillas/minuto"] * 15
        - jugadores_metr["tarjetas_rojas/minuto"] * 50
    )

    lista_metricas = [
        "goles/minuto",
        "goles+asistencias/minuto",
        "asistencias/minuto",
        "goles_concedidos/minuto",
        "tarjetas_amarillas/minuto",
        "tarjetas_rojas/minuto",
        "metrica_agregada"
    ]

    metrica_escogida = st.selectbox("Selecciona una métrica", lista_metricas)

    #en goles concedidos filtramos por porteros
    if metrica_escogida == "goles_concedidos/minuto":
        base_top = jugadores_metr[jugadores_metr["posicion"] == "GK"].copy()
        orden_asc = True #cuantos menos mejor
    else:
        base_top = jugadores_metr.copy()
        orden_asc = False

    # ordenamos por la métrica y desempatamos con quien haya jugado más minutos para beneficiar a los que más han jugado
    top15 = base_top.sort_values(by=[metrica_escogida, "minutos_jugados"],ascending=[orden_asc, False]).head(15).copy()

    #para ponerlo como en el ejemplo
    top15["etiqueta_ranking"] = top15["ranking_mercado"].astype(str) + "º"

    #representamos
    graf_top15 = px.bar(
        top15,
        x=metrica_escogida,
        y="nombre_jugador",
        orientation="h",
        text="etiqueta_ranking",
        color="posicion",
        hover_data=["seleccion_nacional", "valor_mercado", "minutos_jugados"],
        title="Top 15 jugadores en " + metrica_escogida + " (junto a su ranking en valor de mercado)"
        )

    graf_top15.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(graf_top15,width='stretch')


# -----
# EJERCICIO 6: GRÁFICO DE BURBUJAS
with tab2:
    st.subheader("Ejercicio 6: Minutos jugados, calificación media y valor de mercado")

    # creamos los filtros
    seleccion6 = st.selectbox("Selección (burbujas)", ["Todas"] + sorted(jugadores["seleccion_nacional"].unique()))
    posicion6 = st.selectbox("Posición (burbujas)", ["Todas"] + list(jugadores["posicion"].unique()))

    datos6 = jugadores.copy()

    if seleccion6 != "Todas":
        datos6 = datos6[datos6["seleccion_nacional"] == seleccion6].copy()

    if posicion6 != "Todas":
        datos6 = datos6[datos6["posicion"] == posicion6].copy()

    # distinguimos con un color específico los jugadores que han marcado gol (rojo)
    datos6["goleador"] = "No ha marcado"
    datos6.loc[datos6["goles"] > 0, "goleador"] = "Ha marcado"


    graf_burbujas = px.scatter(
        datos6,
        x="minutos_jugados",
        y="calificacion_media",
        size="valor_mercado",
        size_max=40,
        color="goleador",
        color_discrete_map={"Ha marcado": "red", "No ha marcado": "royalblue"},
        hover_name="nombre_jugador",
        hover_data=["seleccion_nacional", "posicion", "valor_mercado", "goles"],
        title="Minutos Jugados vs Calificación Media (Tamaño: Valor de Mercado)"
        )
    st.plotly_chart(graf_burbujas,width='stretch')

    
# -----
# EJERCICIO 7: DIAGRAMA DE CAJA (BOX PLOT)
with tab3:
    st.header("Análisis 3: Impacto Arbitral")
    st.subheader("Ejercicio 7: Distribución de tarjetas por partido y ronda")

    #extraemos las tarjetas
    eventos_tarjetas = eventos[eventos["tipo_evento"].isin(["Yellow Card", "Red Card"])].copy()

    #número de tarjetas por partido
    conteo_tarjetas = eventos_tarjetas.groupby("index_partido").size().reset_index(name="num_tarjetas")

    # unimos con el dataframe de partidos
    partidos_tarjetas = pd.merge(partidos, conteo_tarjetas, on="index_partido", how="left")
    partidos_tarjetas["num_tarjetas"] = partidos_tarjetas["num_tarjetas"].fillna(0).astype(int)

    # limpiamos las rondas y creamos el nombre del partido 
    partidos_tarjetas["ronda"] = partidos_tarjetas["ronda"].str.strip()
    partidos_tarjetas["nombre_partido"] = (partidos_tarjetas["seleccion_local"] + " vs " + partidos_tarjetas["seleccion_visitante"])

    graf_caja = px.box(
        partidos_tarjetas,
        x="ronda",
        y="num_tarjetas",
        points="all", # mostramos los puntos para poder identificar cada partido
        hover_name="nombre_partido",
        hover_data=["index_partido", "arbitro_partido"],
        title="Distribución de tarjetas por partido según la ronda"
    )

    st.plotly_chart(graf_caja,width='stretch')


# -----
# EJERCICIO 8: ÍNDICE DE INTERVENCIÓN ARBITRAL
with tab3:
    st.subheader("Ejercicio 8: Índice de Intervención Arbitral")

    #puntos por evento
    puntos_evento = {
        "Yellow Card": 1.0,
        "Red Card": 3.0,
        "VAR Review": 1.0,
        "Goal": 0.2
    }

    eventos_arb = eventos[eventos["tipo_evento"].isin(puntos_evento.keys())].copy()
    eventos_arb["puntos"] = eventos_arb["tipo_evento"].map(puntos_evento)

    # puntos por partido
    indice_por_partido = eventos_arb.groupby("index_partido")["puntos"].sum().reset_index(name="indice_intervencion")

    #unimos con la tabla de partidos
    partidos_arb = pd.merge(partidos, indice_por_partido, on="index_partido", how="left")
    partidos_arb["indice_intervencion"] = partidos_arb["indice_intervencion"].fillna(0)
    partidos_arb["ronda"] = partidos_arb["ronda"].str.strip()
    partidos_arb["nombre_partido"] = (partidos_arb["seleccion_local"] + " vs " + partidos_arb["seleccion_visitante"])

    # elegimos la ronda y selección que queremos analizar 
    ronda8 = st.selectbox("Ronda (Árbitros)", ["Todas"] + list(partidos_arb["ronda"].unique()))
    seleccion8 = st.selectbox("Selección (Árbitros)", ["Todas"] + sorted(partidos_arb["seleccion_local"].unique()))


    if ronda8 != "Todas":
        partidos_arb = partidos_arb[partidos_arb["ronda"] == ronda8].copy()

    if seleccion8 != "Todas":
        partidos_arb = partidos_arb[
            (partidos_arb["seleccion_local"] == seleccion8) | 
            (partidos_arb["seleccion_visitante"] == seleccion8)
        ].copy()

    if len(partidos_arb) > 0:
        # calculamos la media del índice para cada árbitro en los partidos filtrados
        medias_arbitro = partidos_arb.groupby("arbitro_partido")["indice_intervencion"].mean().reset_index(name="media_indice")
        medias_arbitro = medias_arbitro.sort_values("media_indice")
        orden_arbitros = list(medias_arbitro["arbitro_partido"])

        # gráfico con los partidos de cada árbitro
        graf_arbitros = px.scatter(
            partidos_arb,
            x="indice_intervencion",
            y="arbitro_partido",
            color="ronda",
            hover_name="nombre_partido",
            category_orders={"arbitro_partido": orden_arbitros},
            height=900,
            title="Índice de Intervención Arbitral por partido y media por árbitro"
        )

        # añadimos la media del índice de cada árbitro
        graf_arbitros.add_scatter(
            x=medias_arbitro["media_indice"],
            y=medias_arbitro["arbitro_partido"],
            mode="markers",
            marker=dict(symbol="diamond", size=10, color="red"),
            name="Media del árbitro"
        )

        st.plotly_chart(graf_arbitros,width='stretch')

        # arbitro mas y menos severo
        menos = medias_arbitro.iloc[0]
        mas = medias_arbitro.iloc[-1]
        st.write(f"Árbitro menos severo: {menos['arbitro_partido']} (media: {menos['media_indice']:.2f})")
        st.write(f"Árbitro más severo: {mas['arbitro_partido']} (media: {mas['media_indice']:.2f})")
    else:
        st.write("No hay partidos para los filtros seleccionados")