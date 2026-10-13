import streamlit as st


def footer_home():
    # logo_url = "https://i.ibb.co/4r5X1FY/logo.png"
    st.markdown(f"""
           <div style="margin-top:2rem ; display:flex; gap:6px; justify-content:center;">
              <p style="font-weight:bold; color:white;">Built with ❤️ by </p>
           </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    logo_url = "https://i.ibb.co/4r5X1FY/logo.png"
    st.markdown(f"""
           <div style="margin-top:2rem ; display:flex; gap:6px; justify-content:center;">
              <p style="font-weight:bold; color:black;">Built with ❤️ by </p>
           </div>
    """, unsafe_allow_html=True)
