import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
import geopandas as gpd


st.set_page_config("Monitoreo Vacunación Influenza", layout="wide")
APP_TITLE = "Monitoreo Vacunación Influenza"
APP_SUB_TITLE = "Fuente: Registro Nacional de Inmunizaciones"

st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)



col1, col2 = st.columns(2)

serv_prov = pd.read_excel("serv_prov.xlsx")

@st.cache(persist =True)
def get_data_from_csv():
    data = pd.read_csv(
        "cob65.csv",
        usecols=["Comuna_residencia", "Cobertura"]
    )
    return data

df = get_data_from_csv()
df = df.merge(serv_prov, left_on="Comuna_residencia", right_on="Comuna", how="left")

#df = pd.read_csv("cob65.csv", usecols=["Comuna_residencia", "Cobertura"])


st.sidebar.header("Filtros")
df = df.sort_values(by= "Servicio")

#[''] + list(df['Servicio'].drop_duplicates())
makes = [''] + list(df['Servicio'].drop_duplicates())
f_Servicio = st.sidebar.selectbox('Seleccione un Servicio de Salud:', options=makes)

df_select = df.loc[df["Servicio"] == f_Servicio]


mean = df_select["Cobertura"].mean()
new_row = {'Comuna_residencia': 'RM', 'Comuna': 'RM', 'Servicio': 'RM', 'Cobertura': mean}

df_select = df_select.sort_values(by=["Servicio", "Cobertura"])

df_select.loc[len(df_select)] = new_row

fig = px.bar(df_select, x='Comuna_residencia', y='Cobertura', color="Servicio", title="Porcentaje de Cobertura en Población General")
fig.add_hline(y= df_select["Cobertura"].mean())

#---------------------------------------

vacxdia = pd.read_csv("vacxdia.csv")
vacxdia= vacxdia.loc[vacxdia["FECHA_INMUNIZACION"] >= "2023-03-15"]
vacxdia = vacxdia.merge(serv_prov, left_on="Comuna_residencia", right_on="Comuna", how="left")
vac_gby = pd.DataFrame(vacxdia.groupby(["Servicio", "FECHA_INMUNIZACION"])["N° de vacunados"].sum().reset_index())                

fig2 = px.line(vac_gby, x="FECHA_INMUNIZACION", y="N° de vacunados", color='Servicio')

geo_df = gpd.read_file("comunas_rm.geojson")

geo_df= geo_df.set_index('Comuna')

fig3 = px.choropleth_mapbox(geo_df,
                           geojson=geo_df.geometry,
                           locations=geo_df.index,
                           color="st_area_sh",
                           center={"lat": -33.55457159236532, "lon": -70.63308734055428},
                           opacity=0.8,
                           mapbox_style="carto-positron",
                           zoom=7)


with col1:
    st.header("Cobertura")
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.header("Vacunas diarias")
    st.plotly_chart(fig2, use_container_width=True)




#df_selection = df.query("Servicio == @f_Servicio")
#st.dataframe(df_selection)
