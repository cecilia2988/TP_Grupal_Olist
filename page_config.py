import streamlit as st

def run():
    st.set_page_config(page_title="Reporte Olist",
                        page_icon="🛒",
                        layout="wide",
                        initial_sidebar_state="auto")

    # STYILING

    FONT_SIZE_CSS = f"""
    <style>
    h1 {{
        font-size: 40px !important;
        margin-top: 0px !important;
        padding-top: 0px !important;
    }}
    .js-plotly-plot.plotly.modebar {{
        right: 120px !important;
    }}
    .modebar.modebar--hover.ease-bg {{
        right: 120px !important;
    }}
    .section.css-1k0ckh2.e1fqkh3o9 {{
        background-color:blue;
    }}
    </style>
    """

    st.write(FONT_SIZE_CSS, unsafe_allow_html=True)