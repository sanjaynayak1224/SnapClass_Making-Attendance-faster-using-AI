import streamlit as st

from src.database.db import create_attendance


def show_attendance_results(results_df, attendance_logs):
  st.write("Please review the attendance before confirming")
  st.dataframe(results_df, hide_index=True, width='stretch')

  col1, col2=st.columns(2)

  with col1:
    if st.button("Discard", width="stretch"):
      st.session_state.attendance_images=[]
      st.session_state.voice_attendance_results= None
      st.rerun()
  
  with col2:
    if st.button("Confirm and Save", width="stretch", type="primary"):
      try:
        create_attendance(attendance_logs)
        st.toast("Attendance Taken Successfully")
        st.session_state.attendance_images=[]
        st.session_state.voice_attendance_results= None
        st.rerun()

      except Exception as e:
        st.error("Sync Failed!")
  

@st.dialog("Attendance Reports")
def attendance_result_dialog(results_df, attendance_logs):
  show_attendance_results(results_df, attendance_logs)
