import base64
import streamlit as st

st.set_page_config(page_title='Attendance System', layout='wide')

st.header('Attendance System using Face Recognition')

with st.spinner("Loading Models and Connecting to Redis db ..."):
    import face_rec

st.success('Model loaded successfully')
st.success('Redis db successfully connected')

def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def build_markup_for_logo(
    png_file,
    background_position="center",
    background_size="contain",
):
    binary_string = get_base64_of_bin_file(png_file)
    return f"""
        <style>
            .stApp {{
                background-image: url("data:image/png;base64,{binary_string}");
                background-repeat: no-repeat;
                background-position: {background_position};
                background-size: {background_size};
                background-attachment: fixed;
                opacity: 1.0; /* Adjust the transparency here */
            }}
        </style>
        """

def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(logo_markup, unsafe_allow_html=True)

add_logo("img/myimg.png")
