from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## function to load gemini pro vision model and get response



def get_gemini_pro_vision_response(input,image, prompt):
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    print(input,  prompt)
    response = model.generate_content([input, image[0], prompt])
    print("Response:", response.text)
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        return FileNotFoundError("Please upload an image file.")
    

st.title("Invoice IQ")
st.write("Upload an image and provide a prompt to get a response from Gemini.")

input = st.text_input("Enter your Prompt:", key="input_prompt")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
submit = st.button("Get Response")
input_prompt = """ You are an expert in understanding invoices. 
You will receive input images and you will have to answer question based on the image provided.
only give the relevant answer based on the image provided.
give answer in simple and easy to understand language.
"""
if submit:
    image = input_image_setup(uploaded_file)
    response = get_gemini_pro_vision_response(input_prompt, image, input)
    
    st.subheader("The Response is:")
    
    # Create a container with a border
    with st.container(border=True):
        st.write(response)
image = ""
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.subheader("Uploaded Image(Preview):")
    st.image(img, caption='Uploaded Image.', use_column_width=True)



