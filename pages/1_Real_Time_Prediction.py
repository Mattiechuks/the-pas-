import streamlit as st 
import base64
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time
import threading

st.set_page_config(page_title='Predictions')
st.subheader('Real-Time Attendance System')


# Retrive the data from Redis Database
with st.spinner('Retriving Data from Redis DB ...'):    
    redis_face_db = face_rec.retrive_data(name='academy:register')
    st.dataframe(redis_face_db)
    
st.success("Data sucessfully retrived from Redis")

# time 
waitTime = 30 # time in sec
setTime = time.time()
realtimepred = face_rec.RealTimePred() # real time prediction class

# Real Time Prediction
# streamlit webrtc
# callback function
def video_frame_callback(frame):
    global setTime
    
    img = frame.to_ndarray(format="bgr24") # 3 dimension numpy array
    # operation that you can perform on the array
    pred_img = realtimepred.face_prediction(img,redis_face_db,
                                        'facial_features',['Name','Role'],thresh=0.5)
    
    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waitTime:
        setTime = time.time() # reset time        
        print('Save Data to redis database')
    

    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

# Function to save logs periodically
def save_logs_periodically(realtimepred):
    while True:
        time.sleep(60)  # Save logs every 60 seconds
        realtimepred.saveLogs_redis()

# Start the saving logs thread
save_logs_thread = threading.Thread(target=save_logs_periodically, args=(realtimepred,))
save_logs_thread.start()

webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback)

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
                opacity: 0.9; /* Adjust the transparency here */
            }}
        </style>
        """

def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(logo_markup, unsafe_allow_html=True)

add_logo("img/myimg.png")
