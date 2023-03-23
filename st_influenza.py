import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl


APP_TITLE = "Monitoreo Vacunación Influenza"
APP_SUB_TITLE = "SEREMI de Salud Metropolitana"

st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

serv_prov = pd.read_excel("serv_prov.xlsx")

cob65m = pd.read_csv("cob65.csv", usecols=["Comuna_residencia", "Cobertura"])
cob65m = cob65m.merge(serv_prov, left_on="Comuna_residencia", right_on="Comuna", how="left")

mean = cob65m["Cobertura"].mean()
new_row = {'Comuna_residencia': 'RM', 'Comuna': 'RM', 'Servicio': 'RM', 'Cobertura': mean}
cob65m.loc[len(cob65m)] = new_row


cob65m = cob65m.sort_values(by="Cobertura", ascending=False)
fig = px.bar(cob65m, x='Comuna_residencia', y='Cobertura', color="Servicio", title="Porcentaje de Cobertura en Adultos 65 o más años")
fig.add_hline(y= cob65m["Cobertura"].mean())

st.plotly_chart(fig, use_container_width=True)


