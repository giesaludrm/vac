import streamlit as st

st.set_page_config(
    page_title="Monitoreo Regional del Registro Inmunizaciones",layout="wide"
    #page_icon="👋",
)
def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://seremi13.redsalud.gob.cl/wrdprss_minsal/wp-content/uploads/2021/06/isologo2-2021.jpg);
                background-repeat: no-repeat;
                background-size: 130px 110px;
                padding-top: 60px;
                background-position: 50px 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
add_logo()

st.markdown("""<p style="text-align:center;"><img src="https://seremi13.redsalud.gob.cl/wrdprss_minsal/wp-content/uploads/2021/06/isologo2-2021.jpg"
alt="whatever" width="120" height= "110"></p>""", unsafe_allow_html=True)

st.markdown("""<div style='text-align: center; color: black; font-size: 12px;'>
                SEREMI de Salud Región Metropolitana <br>
                Depto. de Salud Pública y Planificación Sanitaria <br>
                Subdepto. Gestión de Información y Estadísticas <br> 
                 </div>""", unsafe_allow_html=True)

#st.write("## Monitoreo Registro Regional de Inmunizaciones")
st.markdown("<h1 style='text-align: center; color: black;'>Monitoreo Regional del Registro Inmunizaciones</h1>", unsafe_allow_html=True)




col1, col2, col3 = st.columns([1,2.5,1])

with col2:
    st.markdown(
    """<div style="text-align: justify;"><br> Esta plataforma deja a disposición del sector Salud, información de alcance regional para
    el monitoreo de vacunas del Programa Nacional de Inmunizaciones, siendo su objetivo principal el apoyo para la gestión, 
    basándose en la utilización de datos provisorios, los cuales se presentan a modo de indicadores y gráficos con desagregación por:
    Región Metropolitana, Servicios de Salud Metropolitanos, Comunas y Establecimientos de Salud. <br> <br>
    La herramienta fue desarrollada mediante un trabajo colaborativo entre el Subdepto. de Gestión de Información
    y Estadísticas, Subdepto. de Epidemiología y el equipo del Programa Nacional de Inmunizaciones de la SEREMI de
    Salud Metropolitana.</div>""", unsafe_allow_html=True)


