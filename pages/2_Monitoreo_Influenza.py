import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import numpy as np

st.set_page_config("Monitoreo Vacunación Influenza", layout="wide")

st.markdown("---")
st.title("Monitoreo Vacunación Influenza")

# CARGA DE DATOS
df = pd.read_csv("avance_vac_inf_total.csv", sep=";", encoding="latin-1")
df = df.loc[df["Desagregación"] == "Comunas"]
vacxdia = pd.read_csv("vacxdia.csv", sep=";", encoding="latin-1")
vacxdia = vacxdia.loc[vacxdia["Desagregación"] == "Establecimientos de salud"]
df_criterios = df.loc[df["Criterio_elegibilidad"]!= "Población General"]

vac_inf_geo = pd.read_csv("vac_inf_est_geo.csv", sep=";", encoding="latin-1")


# FILTROS
st.sidebar.header("Filtros")


def agrupar_servicio(df):
    df = df.groupby(["Servicio"]).sum(["N° de vacunados", "Población objetivo"]).reset_index()
    df["Avance vacunación"] = round((df["N° de vacunados"] *100) / df["Población objetivo"], 1)
    return df

def filtro_c_elig(df):
    #df_pob_gral = df.loc[df["Criterio_elegibilidad"] == "Población General"]
    makes = list(df['Criterio_elegibilidad'].drop_duplicates())
    f_c_elig = st.sidebar.selectbox('Seleccione un Criterio de elegibilidad:', options=makes, format_func=lambda x: 'Todos los Criterios' if x == '' else x)
    df_filter = df.loc[df["Criterio_elegibilidad"] == f_c_elig]

    return df if not f_c_elig else df_filter

def filtro_ss(df):
    df = df.sort_values(by= "Servicio")
    makes = [''] + list(df['Servicio'].drop_duplicates())
    f_Servicio = st.sidebar.selectbox('Seleccione un Servicio de Salud:', options=makes, format_func=lambda x: 'Región Metropolitana - por defecto' if x == '' else x)
    df_filter = df.loc[df["Servicio"] == f_Servicio]

    return df if not f_Servicio else df_filter

def filtro_com(df):
    df = df.sort_values(by= "Comuna")
    makes = [''] + list(df['Comuna'].drop_duplicates())
    f_Comuna = st.sidebar.selectbox('Seleccione una Comuna:', options=makes, format_func=lambda x: 'Todas las Comunas' if x == '' else x)
    df_filter = df.loc[df["Comuna"] == f_Comuna]

    return df if not f_Comuna else df_filter



# APLICACION DE FILTROS
#df = filtro_desagregacion(df)
if not filtro_ss:
    df = agrupar_servicio(df)

df = filtro_c_elig(df)

# CALCULO PROMEDIO REGIONAL AVANCE VACUNACIÓN
mean = round(df["Avance vacunación"].mean(),1)
new_row = {'Comuna': 'RM', 'Servicio': 'RM', 'Avance vacunación': mean}

df = filtro_ss(df)

df = filtro_com(df)



df_filtro = df[["Servicio","Comuna","Criterio_elegibilidad"]]
df_filtro2 = df[["Servicio","Comuna"]]


vacxdia = vacxdia.merge(df_filtro, on=["Servicio","Comuna","Criterio_elegibilidad"], how="inner")
vacxdia_gb = vacxdia.groupby(["Servicio","Comuna","Criterio_elegibilidad", "FECHA_INMUNIZACION"]).sum("N° de vacunados").reset_index()
vac_inf_geo = vac_inf_geo.merge(df_filtro, on=["Servicio","Comuna","Criterio_elegibilidad"], how="inner")
df_criterios = df_criterios.merge(df_filtro2, on=["Servicio","Comuna"], how="inner")

#print(vac_inf_geo)

# INDICADORES
## Avance vacunación PROMEDIO
promedio_cob = round(df["Avance vacunación"].mean(),1)
dif_promedio_cob = 85-promedio_cob
dosis_adm = round(df["N° de vacunados"].sum())
dosis_adm =str('{0:,}'.format(dosis_adm))
dosis_adm = dosis_adm.replace(",", ".")
mean_vacxdia = round(vacxdia_gb["N° de vacunados"].mean())

df.loc[len(df)] = new_row

df = df.sort_values(by="Avance vacunación")


Criterio_elegibilidad_title = df.iloc[0]["Criterio_elegibilidad"]


df_table= df[["Servicio", "Comuna", "Avance vacunación"]]
df_table= df_table.set_index('Servicio')


# FIGURAS 
#color_discrete_sequence= px.colors.qualitative.Safe

da_table =  df[["Servicio", "Comuna", "N° de vacunados", "Población objetivo","Avance vacunación"]]
da_table= da_table.set_index("Servicio")

#df = df.groupby(["Servicio"]).sum(["N° de vacunados", "Población objetivo"]).reset_index()
#df["Avance vacunación"] = round((df["N° de vacunados"] *100) / df["Población objetivo"], 1)

fig = px.bar(df, x='Comuna', y='Avance vacunación',
            title= f"Porcentaje Avance vacunación", color=np.where((df['Comuna'] == "RM"), 'green', 'red'),
            color_discrete_sequence=["#3057D3", "#DD3C2C"],height=450,
            labels={"Avance vacunación": "Avance vacunación (%)"})
#fig.update_layout({
#'#plot_bgcolor': 'rgba(37, 50, 0, 0)',
#'paper_bgcolor': 'rgba(37, 0, 0, 0.2)',
#})
#fig.add_hline(y= mean)
fig.update_layout(xaxis_categoryorder = 'total descending')
fig.layout.update(showlegend=False)
fig.update_traces(
    hovertemplate="<br>".join([
        "Comuna: %{x}",
        "Avance vacunación: %{y}%<extra></extra>"]))


vacxdia_g = vacxdia.groupby(["Comuna", "Dosis"]).sum("N° de vacunados").reset_index()
vacxdia_g = vacxdia_g.sort_values(by=["Dosis"], ascending=False)

fig2 = px.bar(vacxdia_g, x="Comuna", y="N° de vacunados", height=450,
               color_discrete_sequence= ["#3057D3", "#DD3C2C", "#07EC07"], title=f"Total vacunas administradas, según dosis",color="Dosis")
fig2.update_layout(xaxis_categoryorder = 'total descending')


df_criterios = df_criterios.groupby("Criterio_elegibilidad").sum("N° de vacunados").reset_index()
fig3 = px.pie(df_criterios, values='N° de vacunados', names='Criterio_elegibilidad', title="Vacunas administradas según criterio de elegibilidad")
fig3.layout.update(showlegend=False)


geo_df = gpd.read_file("comunas_rm.geojson")
geo_df = geo_df.merge(df, on="Comuna", how="inner")


geo_df["x"] = geo_df.centroid.map(lambda p: p.x)
geo_df["y"] = geo_df.centroid.map(lambda p: p.y)

long_center = geo_df["x"].mean()
lat_center = geo_df["y"].mean()

  
geo_df= geo_df.set_index('Comuna')

figmapa = px.choropleth_mapbox(geo_df,
                           geojson=geo_df.geometry,
                           locations=geo_df.index,
                           color="Avance vacunación",
                           center={"lat": lat_center, "lon": long_center},
                           opacity=0.7,
                           mapbox_style="carto-positron",
                           color_continuous_scale= "RdBu",labels={
                     "Avance vacunación": "Avance (%)"
                 },
                           zoom=8.5, height=400, title= "Distribución territorial del avance de vacunación"
                           )
figmapa.update_layout(
    margin=dict(l=0, r=0, t=40, b=0)
)

figmapa2 = px.scatter_mapbox(vac_inf_geo, lat="latitud",
                        lon="longitud",   color="N° de vacunados",size="N° de vacunados",
                  color_continuous_scale="RdBu", size_max=15, zoom=8.5, height=500, mapbox_style="carto-positron",
                  hover_data=["Comuna", "Establecimiento"],
                  title= "Distribución territorial Vacunados por establecimiento")


vacxdia_f =  vacxdia.groupby(["FECHA_INMUNIZACION", "Dosis"]).sum("N° de vacunados").reset_index()

fig4 = px.area(vacxdia_f, x="FECHA_INMUNIZACION", y="N° de vacunados", height=450, color= "Dosis",
               color_discrete_sequence= ["#3057D3", "#DD3C2C", "#07EC07"], markers=True, title=f"Total Dosis diarias",
               labels={
                     "FECHA_INMUNIZACION": "Fecha de Inmunización"
                 },)
fig4.update_traces(line=dict(width=0.8))
fig4.update_traces(marker={'size': 3})

vacxdia_table = vacxdia[["Servicio", "Comuna", "FECHA_INMUNIZACION","N° de vacunados"]]
vacxdia_table = vacxdia_table.rename(columns={"FECHA_INMUNIZACION":"Fecha de inmunización"})
vacxdia_table= vacxdia_table.set_index('Servicio')


col1, col2, col3 = st.columns(3)

col4, col5, col6 = st.columns([1.2, 1.5, 1])

col7, col8 = st.columns([1, 1])



with col1:
    st.metric(label="Avance de vacunación", value= f"{promedio_cob}%", delta=f"{dif_promedio_cob}%", delta_color="inverse")

with col2:
    st.metric(label="Dosis administradas", value= f"{dosis_adm}")
    
with col3:
    st.metric(label= "Promedio dosis diarias", value= f"{mean_vacxdia}")



with col4:
    st.plotly_chart(fig, use_container_width=True)

with col5:
    st.plotly_chart(fig2, use_container_width=True)

with col6:
    st.plotly_chart(fig3, use_container_width=True)

with st.container():
    st.plotly_chart(fig4, use_container_width=True)


with col7:
    st.plotly_chart(figmapa)

with col8:
    st.plotly_chart(figmapa2)

st.markdown("###### Tabla N° de vacunados y Avance de Vacunación por Criterio de elegibilidad y Comuna")
with st.container():
    st.dataframe(da_table, use_container_width=True)