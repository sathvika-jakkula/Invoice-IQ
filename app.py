from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import PyPDF2
from pdf2image import convert_from_bytes
from docx import Document


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## function to load gemini pro vision model and get response



def get_gemini_pro_vision_response(input,image, prompt):
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    print(input,  prompt)
    response = model.generate_content([input, image[0], prompt])
    print("Response:", response.text)
    return response.text

def get_gemini_pro_response(input, text_content, prompt):
    """Function for text-based content (extracted from PDFs/DOCs)"""
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    combined_prompt = f"{input}\n\nDocument Content:\n{text_content}\n\n{prompt}"
    response = model.generate_content(combined_prompt)
    print("Response:", response.text)
    return response.text

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

def convert_pdf_to_images(uploaded_file):
    """Convert PDF first page to image for preview"""
    try:
        images = convert_from_bytes(uploaded_file.getvalue(), first_page=1, last_page=1)
        return images[0] if images else None
    except Exception as e:
        print(f"Error converting PDF to image: {str(e)}")
        return None

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
        raise FileNotFoundError("Please upload a file.")
    

st.title("Invoice IQ")
st.write("Upload a file (image, PDF, or DOCX) and provide a prompt to get a response.")

input = st.text_input("Enter your Prompt:", key="input_prompt")
uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png", "pdf", "docx"])
submit = st.button("Get Response")
input_prompt = """ You are an expert in understanding invoices and documents. 
You will receive input files (images, PDFs, or DOCs) and you will have to answer questions based on the content provided.
Only give the relevant answer based on the file provided.
Give answer in simple and easy to understand language.
"""
if submit:
    if uploaded_file is not None:
        file_type = uploaded_file.type
        
        # Handle different file types
        if file_type in ["image/jpeg", "image/jpg", "image/png"]:
            # Process as image
            image = input_image_setup(uploaded_file)
            response = get_gemini_pro_vision_response(input_prompt, image, input)
        
        elif file_type == "application/pdf":
            # Extract text from PDF
            st.info("Processing PDF file...")
            text_content = extract_text_from_pdf(uploaded_file)
            response = get_gemini_pro_response(input_prompt, text_content, input)
        
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Extract text from DOCX
            st.info("Processing DOCX file...")
            text_content = extract_text_from_docx(uploaded_file)
            response = get_gemini_pro_response(input_prompt, text_content, input)
        
        else:
            st.error("Unsupported file type!")
            response = None
        
        if response:
            st.subheader("The Response is:")
            
            # Create a container with a border
            with st.container(border=True):
                st.write(response)
    else:
        st.warning("Please upload a file first!")

# Display file preview
if uploaded_file is not None:
    file_type = uploaded_file.type
    
    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        img = Image.open(uploaded_file)
        st.subheader("Uploaded Image (Preview):")
        st.image(img, caption='Uploaded Image.', use_column_width=True)
    
    elif file_type == "application/pdf":
        st.subheader("Uploaded PDF (Preview):")
        # Try to show first page as image
        preview_img = convert_pdf_to_images(uploaded_file)
        if preview_img:
            st.image(preview_img, caption='PDF First Page Preview', use_column_width=True)
        else:
            st.info("PDF uploaded successfully. Preview not available.")
        
        # Reset file pointer for processing
        uploaded_file.seek(0)
    
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.subheader("Uploaded DOCX:")
        st.info(f"Document: {uploaded_file.name}")
        # Show a preview of the extracted text
        text_preview = extract_text_from_docx(uploaded_file)
        with st.expander("View document text preview"):
            st.text(text_preview[:500] + "..." if len(text_preview) > 500 else text_preview)
        
        # Reset file pointer for processing
        uploaded_file.seek(0)



