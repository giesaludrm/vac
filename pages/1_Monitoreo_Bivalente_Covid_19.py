import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd


st.set_page_config("Monitoreo Vacunación Bivalente Covid-19", layout="wide")
APP_TITLE = "Monitoreo Vacunación Bivalente Covid-19"
APP_SUB_TITLE = ""

st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)
