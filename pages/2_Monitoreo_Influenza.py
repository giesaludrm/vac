import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
import geopandas as gpd


st.set_page_config("Monitoreo Vacunación Influenza", layout="wide")
APP_TITLE = "Monitoreo Vacunación Influenza"
APP_SUB_TITLE = ""

st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)
#st.markdown("""---""")

col1, col2 = st.columns(2)


# CARGA DE DATOS

df = pd.read_csv("inf_cob_data.csv", usecols=["Servicio","Comuna_residencia", "Comuna","Grupo_obj","Cobertura"])
vacxdia = pd.read_csv("vacxdia.csv")


# FILTROS
st.sidebar.header("Filtros")


def filtro_g_obj(df):
    df_pob_gral = df.loc[df["Grupo_obj"] == "Población General"]
    makes = list(df['Grupo_obj'].drop_duplicates())
    f_g_obj = st.sidebar.selectbox('Seleccione un Grupo Objetivo:', options=makes)
    df_filter = df.loc[df["Grupo_obj"] == f_g_obj]

    return df_pob_gral if not f_g_obj else df_filter

def filtro_ss(df):
    df = df.sort_values(by= "Servicio")
    makes = [''] + list(df['Servicio'].drop_duplicates())
    f_Servicio = st.sidebar.selectbox('Seleccione un Servicio de Salud:', options=makes, format_func=lambda x: 'Todos los Servicios de Salud' if x == '' else x)
    df_filter = df.loc[df["Servicio"] == f_Servicio]

    return df if not f_Servicio else df_filter

def filtro_com(df):
    df = df.sort_values(by= "Comuna")
    makes = [''] + list(df['Comuna'].drop_duplicates())
    f_Comuna = st.sidebar.selectbox('Seleccione una Comuna:', options=makes, format_func=lambda x: 'Todos las Comunas' if x == '' else x)
    df_filter = df.loc[df["Comuna"] == f_Comuna]

    return df if not f_Comuna else df_filter



# APLICACION DE FILTROS
df = filtro_g_obj(df)

# CALCULO PROMEDIO REGIONAL COBERTURA 
mean = round(df["Cobertura"].mean(),1)
new_row = {'Comuna_residencia': 'RM', 'Comuna': 'RM', 'Servicio': 'RM', 'Cobertura': mean}

df = filtro_ss(df)
df = filtro_com(df)

df = df.sort_values(by=["Servicio","Cobertura"])
df.loc[len(df)] = new_row

grupo_obj_title = df.iloc[0]["Grupo_obj"]


df_table= df[["Servicio", "Comuna", "Cobertura"]]
df_table= df_table.set_index('Servicio')


# FIGURAS 

fig = px.bar(df, x='Comuna_residencia', y='Cobertura', color="Servicio", 
            color_discrete_sequence= px.colors.qualitative.Safe,
            labels={
                     "Cobertura": "Cobertura (%)"
                 },
            height=500)
fig.add_hline(y= mean)


#---------------------------------------

vacxdia = vacxdia.merge(df, on=["Comuna", "Grupo_obj"], how="inner")

fig2 = px.line(vacxdia, x="FECHA_INMUNIZACION", y="N° de vacunados", color='Comuna', height=500,
               color_discrete_sequence= px.colors.qualitative.Safe, markers=True,
               labels={
                     "FECHA_INMUNIZACION": "Fecha de Inmunización"
                 },)
fig2.update_xaxes(rangeslider_visible=True)
fig2.update_traces(line=dict(width=0.8))
fig2.update_traces(marker={'size': 3})

geo_df = gpd.read_file("comunas_rm.geojson")
geo_df = geo_df.merge(df, on="Comuna", how="inner")
geo_df["x"] = geo_df.centroid.map(lambda p: p.x)
geo_df["y"] = geo_df.centroid.map(lambda p: p.y)

long_center = geo_df["x"].mean()
lat_center = geo_df["y"].mean()

  
geo_df= geo_df.set_index('Comuna')


fig3 = px.choropleth_mapbox(geo_df,
                           geojson=geo_df.geometry,
                           locations=geo_df.index,
                           color="Cobertura",
                           center={"lat": lat_center, "lon": long_center},
                           opacity=0.7,
                           mapbox_style="carto-positron",
                           color_continuous_scale= "BrBG",labels={
                     "Cobertura": "Cobertura (%)"
                 },
                           zoom=8,
                           height=600)



vacxdia_table = vacxdia[["Servicio_x", "Comuna", "FECHA_INMUNIZACION","N° de vacunados"]]
vacxdia_table = vacxdia_table.rename(columns={"Servicio_x": "Servicio", "FECHA_INMUNIZACION":"Fecha de inmunización"})
vacxdia_table= vacxdia_table.set_index('Servicio')

with col1:
    st.subheader(f"Cobertura en {grupo_obj_title}")
    tab1, tab2, tab3 = st.tabs(["📈 Gráfico", "🗃 Datos", "🌐 Mapa"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        #st.markdown("###### Tabla de coberturas")
        st.write(df_table, use_container_width=True)
    with tab3:
        st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader(f" Vacunas diarias en {grupo_obj_title}")
    tab1, tab2, tab3 = st.tabs(["📈 Gráfico", "🗃 Datos", "🌐 Mapa"])
    with tab1:
        st.plotly_chart(fig2, use_container_width=True)
    with tab2:
        #st.markdown("###### Tabla de n° de vacunados por día")
        st.write(vacxdia_table, use_container_width=True)
