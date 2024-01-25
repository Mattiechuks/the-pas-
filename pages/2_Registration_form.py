import streamlit as st
from Home import face_rec
import base64
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import time
import av
import threading


st.set_page_config(page_title='Registration Form')
st.subheader('Registration Form')

## init registration form
registration_form = face_rec.RegistrationForm()

# Step-1: Collect person name and role
# form
person_name = st.text_input(label='Name',placeholder='First & Last Name')
role = st.selectbox(label='Select your Role',options=('Student',
                                                      'Teacher'))

# Function to create a placeholder frame
def create_placeholder_frame(width, height):
    # You can customize the placeholder image or message
    placeholder_image = np.zeros((height, width, 3), dtype=np.uint8)
    placeholder_image[:] = (255, 255, 255)  # White color as a placeholder
    return placeholder_image

# step-2: Collect facial embedding of that person
def video_callback_func(frame):
    if frame is None:
        # Create a placeholder frame with the desired width and height
        width, height = 640, 480  # Adjust these values based on your requirements
        placeholder_frame = create_placeholder_frame(width, height)
        st.image(placeholder_frame, channels="BGR", use_column_width=True, caption="No video feed available")
        return None

  
    img = frame.to_ndarray(format='bgr24') # 3d array bgr

    reg_img, embedding = registration_form.get_embedding(img)
    # two step process
    # 1st step save data into local computer txt
    if embedding is not None:
        with open('face_embedding.txt',mode='ab') as f:
            np.savetxt(f,embedding)
    
    return av.VideoFrame.from_ndarray(reg_img,format='bgr24')


# Function to save data periodically
def save_data_periodically(registration_form, person_name, role):
    while True:
        return_val = registration_form.save_data_in_redis_db(person_name,role)
        if return_val == True:
            st.success(f"{person_name} registered sucessfully")
        elif return_val == 'name_false':
            st.error('Please enter the name: Name cannot be empty or spaces')
            
        elif return_val == 'file_false':
            st.error('face_embedding.txt is not found. Please refresh the page and execute again.')

# Start the saving data thread
save_data_thread = threading.Thread(target=save_data_periodically, args=(registration_form, person_name, role))
save_data_thread.start()

#Start the video Streaming
webrtc_streamer(key='registration',video_frame_callback=video_callback_func)


# step-3: save the data in redis database


if st.button('Submit'):
    return_val = registration_form.save_data_in_redis_db(person_name,role)
    if return_val == True:
        st.success(f"{person_name} registered sucessfully")
    elif return_val == 'name_false':
        st.error('Please enter the name: Name cannot be empty or spaces')
        
    elif return_val == 'file_false':
        st.error('face_embedding.txt is not found. Please refresh the page and execute again.')
        
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
