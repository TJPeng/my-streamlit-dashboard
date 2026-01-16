import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, World! I can now build web apps in Python.")

name = st.text_input("What is your name?")

if name:
    st.write(f"Nice to meet you, {name}!")

