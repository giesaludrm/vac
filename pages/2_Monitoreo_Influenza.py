import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import numpy as np
from datetime import datetime, timedelta
import locale
#locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

################# TÍTULO Y NOMBRE DE PÁGINA #############################################
st.set_page_config("Monitoreo Vacunación Influenza", layout="wide")
st.title("Monitoreo Vacunación Influenza - Campaña 2023")

################################# CARGA DE DATOS ###########################################
df = pd.read_csv("inf_avance_vac_2023.csv", sep=";", encoding="latin-1")
fecha_act = df["fecha_actualizacion"].iloc[0]
st.markdown(f"Datos provisorios /    Fecha de actualización: {fecha_act} / Fecha corte de datos: día anterior a la fecha de actualización")
st.markdown("---")
fecha_act = pd.to_datetime(fecha_act, format='%d-%m-%Y').strftime('%Y-%m-%d %H:%M:%S')
fecha_act = pd.to_datetime(fecha_act).date()
vac_inf_com = pd.read_csv("inf_dosis_com_2023.csv", sep=";", encoding="latin-1")
vacxdia = pd.read_csv("inf_vacxdia_com_2023.csv", sep=";", encoding="latin-1")
df_criterios = df.loc[df["Criterio_elegibilidad"]!= "Población General"]
vac_inf_geo = pd.read_csv("inf_n_estab_geo_2023.csv", sep=";", encoding="latin-1")
geo_df = gpd.read_file("comunas_rm.geojson")
vacxdia_comp = pd.read_csv("inf_vacxdia_com_2022y2023.csv", sep=";", encoding="latin-1")
vacxdia_comp["FECHA_INMUNIZACION"] = pd.to_datetime(vacxdia_comp["FECHA_INMUNIZACION"])
vacxdia_comp['día-mes']=vacxdia_comp['FECHA_INMUNIZACION'].dt.strftime('%d-%b')
vacxdia_comp['día-mes']=pd.to_datetime(vacxdia_comp['día-mes'],format='%d-%b',errors='coerce')
vacxdia_comp=vacxdia_comp.sort_values(by='FECHA_INMUNIZACION') 


################################## DEFINICION DE FILTROS ######################################
st.sidebar.header("Filtros")

def filtro_c_elig(df):
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


######################### APLICACION DE FILTROS #########################################

# FILTRO CRITERIO ELEGIBILIDAD
df = filtro_c_elig(df)

# CALCULO VALORES DE LA REGION METROPOLITANA
Criterio_elegibilidad_title = df.iloc[0]["Criterio_elegibilidad"]
n_vac_rm = df["N° de vacunados"].sum()
n_pob_rm = df["Población objetivo"].sum()
mean_rm = round((n_vac_rm * 100) / n_pob_rm, 1)
new_row = {'Comuna': 'RM', 'Criterio_elegibilidad': Criterio_elegibilidad_title,
           'Servicio': 'RM','N° de vacunados': n_vac_rm, 'Población objetivo': n_pob_rm,'Avance vacunación': mean_rm}

# FILTRO SERVICIO DE SALUD
df = filtro_ss(df)
# FILTRO COMUNA
df = filtro_com(df)

df_filtro = df[["Servicio","Comuna","Criterio_elegibilidad"]]
df_filtro2 = df[["Servicio","Comuna"]]

################# TRASPASO DE FILTROS A LOS OTROS DF #########################################

vac_inf_com = vac_inf_com.merge(df_filtro, on=["Servicio","Comuna","Criterio_elegibilidad"], how="inner")
vacxdia = vacxdia.merge(df_filtro, on=["Servicio","Comuna","Criterio_elegibilidad"], how="inner")
vacxdia_gb = vacxdia.groupby(["FECHA_INMUNIZACION"]).sum("N° de vacunados").reset_index()
vac_inf_geo = vac_inf_geo.merge(df_filtro, on=["Servicio","Comuna","Criterio_elegibilidad"], how="inner")
vac_inf_geo_gb = vac_inf_geo.groupby(["Comuna", "Establecimiento","Criterio_elegibilidad", "latitud", "longitud"]).sum("N° de vacunados").reset_index()
df_criterios = df_criterios.merge(df_filtro2, on=["Servicio","Comuna"], how="inner")
vacxdia_comp = vacxdia_comp.merge(df_filtro, on=["Servicio","Comuna","Criterio_elegibilidad"], how="inner")
geo_df = geo_df.merge(df, on="Comuna", how="inner")

################# INDICADORES #################################################################
promedio_cob = round(df["Avance vacunación"].mean(),1)
dif_promedio_cob = 85-promedio_cob
dosis_adm = round(df["N° de vacunados"].sum())
dosis_adm =str('{0:,}'.format(dosis_adm))
dosis_adm = dosis_adm.replace(",", ".")
vacxdia_gb["FECHA_INMUNIZACION"] = pd.to_datetime(vacxdia_gb["FECHA_INMUNIZACION"]).dt.date
#fecha lunes de la semana pasada
mon_1sem = ((fecha_act -timedelta(days=(7+(fecha_act.weekday()) % 7))))
#fecha lunes de hace 2 semanas
mon_2sem = ((fecha_act -timedelta(days=(14+(fecha_act.weekday()) % 7))))
#fecha domingo de la semana pasada
sun_1sem = ((fecha_act -timedelta(days=((fecha_act.weekday() + 1) % 7))))
#fecha domingo de hace 2 semanas
sun_2sem = ((fecha_act -timedelta(days=(7+(fecha_act.weekday() + 1) % 7))))

pen_sem = (vacxdia_gb["FECHA_INMUNIZACION"] >= mon_2sem) &  (vacxdia_gb["FECHA_INMUNIZACION"] <= sun_2sem) 
ult_sem = (vacxdia_gb["FECHA_INMUNIZACION"] >= mon_1sem) &  (vacxdia_gb["FECHA_INMUNIZACION"] <= sun_1sem)

una_semana_atras = vacxdia_gb.loc[ult_sem]
dos_semana_atras = vacxdia_gb.loc[pen_sem]

mean_vacxdia_1sem = round(una_semana_atras["N° de vacunados"].mean())
mean_vacxdia_1sem_f =str('{0:,}'.format(mean_vacxdia_1sem))
mean_vacxdia_1sem_f = mean_vacxdia_1sem_f.replace(",", ".")
mean_vacxdia_2sem = round(dos_semana_atras["N° de vacunados"].mean())
diferencia_mean_vacxdia= mean_vacxdia_1sem - mean_vacxdia_2sem
diferencia_mean_vacxdia_f =str('{0:,}'.format(diferencia_mean_vacxdia))
diferencia_mean_vacxdia_f = diferencia_mean_vacxdia_f.replace(",", ".")

df.loc[len(df)] = new_row

df = df.sort_values(by="Avance vacunación")



############################################ FIGURAS ###################################################

# TABLA DE DATOS
da_table =  df[["Servicio", "Comuna", "Criterio_elegibilidad","N° de vacunados", "Población objetivo","Avance vacunación"]]
da_table['Avance vacunación'] = da_table['Avance vacunación'] /100
da_table['Avance vacunación'] = da_table['Avance vacunación'].apply('{:.1%}'.format)
da_table= da_table.set_index("Servicio")
da_table= da_table.sort_values(by ="Comuna")

# GRÁFICO BARRA: % AVANCE VACUNACIÓN
fig = px.bar(df, x='Comuna', y='Avance vacunación',
            title= f"Porcentaje Avance vacunación", color=np.where((df['Comuna'] == "RM"), 'green', 'red'),
            color_discrete_sequence=["#3057D3", "#DD3C2C"],height=450,
            labels={"Avance vacunación": "Avance vacunación (%)"})
fig.update_layout(xaxis_categoryorder = 'total descending')
fig.layout.update(showlegend=False)
fig.update_traces(
    hovertemplate="<br>".join([
        "Comuna: %{x}",
        "Avance vacunación: %{y}%<extra></extra>"]))

# GRÁFICO BARRA: N° DE VACUNADOS POR COMUNA, SEGÚN DOSIS
vac_inf_com = vac_inf_com.sort_values(by="Dosis")
fig2 = px.bar(vac_inf_com, x="Comuna", y="N° de vacunados", height=450,
               color_discrete_sequence= ["#3057D3", "#EC5307", "#1DC427", "#4ADCF3"],
                 title=f"Total vacunas administradas, según dosis",color="Dosis")
fig2.update_layout(xaxis_categoryorder = 'total descending')


# GRÁFICO TORTA: N° DE DOSIS TOTALES, SEGÚN CRITERIO DE ELEGIBILIDAD
df_criterios = df_criterios.groupby("Criterio_elegibilidad").sum("N° de vacunados").reset_index()
fig3 = px.pie(df_criterios, values='N° de vacunados', names='Criterio_elegibilidad', title="Vacunas administradas según criterio de elegibilidad")
fig3.layout.update(showlegend=False)


# GRÁFICO TORTA: N° DE DOSIS TOTALES, SEGÚN DÍA DE LA SEMANA
una_semana_atras["FECHA_INMUNIZACION"] = pd.to_datetime(una_semana_atras["FECHA_INMUNIZACION"])
una_semana_atras["Día de la semana"] = una_semana_atras["FECHA_INMUNIZACION"].dt.day_name(locale='es_ES.utf8')
vacxdia_gb2 = una_semana_atras.groupby("Día de la semana").sum("N° de vacunados").reset_index()
orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
vacxdia_gb2["Día de la semana"] = vacxdia_gb2["Día de la semana"].astype("category")
vacxdia_gb2["Día de la semana"] = vacxdia_gb2["Día de la semana"].cat.set_categories(orden_dias)

fig32 = px.pie(vacxdia_gb2, values='N° de vacunados', names='Día de la semana', title="Vacunas administradas según día de la semana")
fig32.layout.update(showlegend=False)
fig32.update_traces(textposition='inside', textinfo='percent+label')
fig32.update_traces(sort=False) 


# GRÁFICO MAPA: % VACUNACIÓN POR COMUNA
from pyproj import Transformer
geo_df_utm = geo_df.to_crs(epsg=32719)
geo_df_utm["x"] = geo_df_utm.centroid.map(lambda p: p.x)
geo_df_utm["y"] = geo_df_utm.centroid.map(lambda p: p.y)

transformer = Transformer.from_crs('epsg:32719', 'epsg:4326',always_xy=True)

points = list(zip(geo_df_utm.x,geo_df_utm.y))
coordsWgs = np.array(list(transformer.itransform(points)))

geo_df_utm['long']=coordsWgs[:,0]
geo_df_utm['lat']=coordsWgs[:,1]


long_center = geo_df_utm["long"].mean()
lat_center = geo_df_utm["lat"].mean()

  
geo_df= geo_df.set_index('Comuna')

figmapa = px.choropleth_mapbox(geo_df,
                           geojson=geo_df.geometry,
                           locations=geo_df.index,
                           color="Avance vacunación",
                           center={"lat": lat_center, "lon": long_center},
                           opacity=0.7,
                           mapbox_style="carto-positron",
                           color_continuous_scale= "RdBu",
                           labels={"Avance vacunación": "Avance (%)"},
                           zoom=8.5, height=400, title= "Distribución territorial del avance de vacunación")
figmapa.update_layout(margin=dict(l=0, r=0, t=70, b=0))


# GRÁFICO MAPA: TOTAL DOSIS ADMINISTRADAS POR ESTABLECIMIENTO DE SALUD
figmapa2 = px.scatter_mapbox(vac_inf_geo_gb, lat="latitud",
                        lon="longitud",   color="N° de vacunados",size="N° de vacunados",
                  color_continuous_scale="RdBu", size_max=15, zoom=8.5, height=500, mapbox_style="carto-positron",
                  hover_data=["Comuna", "Establecimiento"],
                  title= "Distribución territorial Vacunados por establecimiento")


# GRÁFICO ÁREA: TOTAL DOSIS POR DÍA Y DOSIS
vacxdia_f =  vacxdia.groupby(["FECHA_INMUNIZACION", "Dosis"]).sum("N° de vacunados").reset_index()
vacxdia_f = vacxdia_f.sort_values(by="Dosis")

fig4 = px.area(vacxdia_f, x="FECHA_INMUNIZACION", y="N° de vacunados", height=450, color= "Dosis",
               color_discrete_sequence= ["#3057D3", "#EC5307", "#1DC427", "#4ADCF3"], 
               markers=True, title="Total Dosis diarias - Campaña 2023",
               labels={
                     "FECHA_INMUNIZACION": "Fecha de Inmunización"})
fig4.update_traces(line=dict(width=0.8))
fig4.update_traces(marker={'size': 3})
fig4.update_xaxes(rangeslider_visible=True)


# GRÁFICO LÍNEA: COMPARATIVA TOTAL DOSIS DIARIAS CAMPAÑA 2022 Y 2023
vacxdia_f2 =  vacxdia_comp.groupby(["día-mes", "Campaña"]).sum("N° de vacunados").reset_index()

fig5 = px.line(vacxdia_f2, x='día-mes', y='N° de vacunados', title='Comparación Dosis diarias - Campañas 2022 y 2023',
                color='Campaña',  color_discrete_sequence= ["#3057D3", "#EC5307"])
fig5.update_layout(xaxis_tickformat='%d-%b')
fig5.update_xaxes(rangeslider_visible=True)

# GRÁFICO INDICADOR: % AVANCE VACUNACIÓN
fig_ind = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = promedio_cob,   number={"suffix": "%", 'font_color':'black', 'font_size':35}, 
    gauge = {'axis': {'range': [0, 85],'tickvals': [0, 20, 42.5, 65 ,85]}},
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {"text": "Avance de vacunación"}
    ))
fig_ind.update_layout(height=200, width=200)
fig_ind.update_layout(margin={"r":50,"t":50,"l":50,"b":50})
fig_ind.update_traces(title_font_size=14, selector=dict(type='indicator'))
fig_ind.update_traces(title_font_color="black", selector=dict(type='indicator'))




############################ ESTRUCTURACIÓN DEL DASHBOARD #########################################

col1, col2, col3 = st.columns([1, 1, 1])

col4, col5, col6 = st.columns([1.2, 1.5, 1])

col7, col8, col9 = st.columns([1.5, 1.5, 1])


with col1:
    st.plotly_chart(fig_ind, use_container_width=True)


with col2:
    st.metric(label="Dosis administradas", value= f"{dosis_adm}")
    
with col3:
    st.metric(label= f"Promedio dosis diarias desde: {mon_1sem} hasta: {sun_1sem}",
               value= f"{mean_vacxdia_1sem_f}", delta=f"{diferencia_mean_vacxdia_f}")

with col4:
    st.plotly_chart(fig, use_container_width=True)

with col5:
    st.plotly_chart(fig2, use_container_width=True)

with col6:
    st.plotly_chart(fig3, use_container_width=True)

with st.container():
    st.plotly_chart(fig4, use_container_width=True)
    st.plotly_chart(fig5, use_container_width=True)


with col7:
    st.plotly_chart(figmapa, use_container_width=True)

with col8:
    st.plotly_chart(figmapa2, use_container_width=True)

with col9:
    st.plotly_chart(fig32, use_container_width=True)

st.markdown("###### Tabla N° de vacunados y Avance de Vacunación por Comuna")
with st.container():
    st.dataframe(da_table, use_container_width=True)