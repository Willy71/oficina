# firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])

    # Normalizar la private_key por si viene con \n escapados
    if "private_key" in firebase_dict:
        firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
