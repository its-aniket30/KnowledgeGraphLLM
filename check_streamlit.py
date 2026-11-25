
import streamlit as st

st.set_page_config(page_title="Streamlit Test", layout="wide")

st.title("Streamlit is Working!")
st.success("The dashboard is rendering successfully.")

st.write("KnowledgeGraphLLM - System Test")

name = st.text_input("Enter your name")

if name:
    st.write(f"Welcome, {name}!")
