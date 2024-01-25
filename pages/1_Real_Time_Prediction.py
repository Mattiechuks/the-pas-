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


# Function to create a placeholder frame
def create_placeholder_frame(width, height):
    # You can customize the placeholder image or message
    placeholder_image = np.zeros((height, width, 3), dtype=np.uint8)
    placeholder_image[:] = (255, 255, 255)  # White color as a placeholder
    return placeholder_image

# Real Time Prediction
# streamlit webrtc
# callback function
def video_frame_callback(frame):
    if frame is None:
        # Create a placeholder frame with the desired width and height
        width, height = 640, 480  # Adjust these values based on your requirements
        placeholder_frame = create_placeholder_frame(width, height)
        st.image(placeholder_frame, channels="BGR", use_column_width=True, caption="No video feed available")
        return None

    
    img = frame.to_ndarray(format="bgr24") # 3 dimension numpy array
    # operation that you can perform on the array
    pred_img = realtimepred.face_prediction(img,redis_face_db,
                                        'facial_features',['Name','Role'],thresh=0.5)
    
    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

# Function to save logs periodically
def save_logs_periodically(realtimepred):
    while True:
        time.sleep(60)  # Save logs every 60 seconds
        realtimepred.saveLogs_redis()

# Initialize the RealTimePred class
realtimepred = face_rec.RealTimePred()

# Start the saving logs thread
save_logs_thread = threading.Thread(target=save_logs_periodically, args=(realtimepred,))
save_logs_thread.start()

# Start the video streaming
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
