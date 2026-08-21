import streamlit as st


def footer_home():
    logo_url = "https://i.ibb.co/4r5X1FY/logo.png"
    st.markdown(f"""
           <div style="margin-top:2rem ; display:flex; gap:6x; justify-content:center;">
              <p style="font-weight:bold; color:white;">Built with ❤️ by </p>
              <img src="{logo_url}" style="max-height:25px"/>
           </div>
    """, unsafe_allow_html=True)
