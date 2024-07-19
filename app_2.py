# import os
# import fitz  # PyMuPDF
# import re
# from openai import OpenAI
# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.units import inch
# import streamlit as st

# # Initialize OpenAI client
# openai_api_key = os.getenv('OPENAI_API_KEY')
# if openai_api_key is None:
#     st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
#     st.stop()
# client = OpenAI(api_key=openai_api_key)

# # Streamlit UI for uploading PDF
# st.title("PDF Annotations and Summary Report")
# uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

# # Text Cleaning Function
# def clean_text(text):
#     text = re.sub(r'[^\x20-\x7E]+', ' ', text)
#     text = re.sub(r'\s+', ' ', text)
#     text = text.strip()
#     return text

# # Function to Extract Annotations
# def extract_annotations(pdf_path):
#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         st.error(f"Error opening PDF: {e}")
#         return []

#     annotations = []

#     for page_num in range(doc.page_count):
#         page = doc.load_page(page_num)
#         for annot in page.annots():
#             if annot is None or annot.type[0] not in [8, 9, 10, 11]:
#                 continue
#             annot_type = annot.type[1]
#             content = annot.info.get("content", "").strip()
#             if not content and annot_type == "Highlight":
#                 rect = annot.rect
#                 content = page.get_text("text", clip=rect).strip()
#                 content = clean_text(content) if content else "No content"
#             else:
#                 content = clean_text(content)
#             annotations.append({"page": page_num + 1, "type": annot_type, "content": content})

#     doc.close()
#     return annotations

# # Function to Generate Summary
# def generate_summary(highlights_text):
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": "Precisely summarize the following highlights and provide a response in English and French:\n\n" + highlights_text}
#             ],
#             max_tokens=150
#         )
#         return completion.choices[0].message.content
#     except Exception as e:
#         st.error(f"Error generating summary: {e}")
#         return "Unable to generate summary."

# # Function to Create a Report PDF
# def create_report_pdf(original_pdf_path, annotations, summary):
#     report_pdf_name = "REPORT_" + os.path.basename(original_pdf_path)
#     doc = SimpleDocTemplate(report_pdf_name, pagesize=letter)

#     styles = getSampleStyleSheet()
#     title_style = styles['Heading1']
#     title_style.textColor = colors.darkblue
#     subtitle_style = ParagraphStyle('subtitle', parent=styles['Heading2'], textColor=colors.darkgreen)
#     normal_style = styles['Normal']

#     elements = []
#     elements.append(Paragraph("Document Summary and Annotations Report", title_style))
#     elements.append(Spacer(1, 0.2 * inch))
#     elements.append(Paragraph("Summary:", subtitle_style))
#     elements.append(Paragraph(summary, normal_style))
#     elements.append(Spacer(1, 0.2 * inch))
#     elements.append(Paragraph("Annotations:", subtitle_style))

#     for annot in annotations:
#         text = f"Page {annot['page']}, {annot['type']}: {annot['content']}"
#         elements.append(Paragraph(text, normal_style))
#         elements.append(Spacer(1, 0.1 * inch))

#     doc.build(elements)
#     return report_pdf_name

# # Main Execution
# if uploaded_pdf:
#     pdf_path = uploaded_pdf.name
#     with open(pdf_path, "wb") as f:
#         f.write(uploaded_pdf.getbuffer())
    
#     # Extract Annotations
#     annotations = extract_annotations(pdf_path)

#     # Generate Summary
#     highlights_text = "\n".join([annot["content"] for annot in annotations])
#     summary = generate_summary(highlights_text)

#     # Display Summary and Annotations
#     if annotations or summary:
#         report_pdf_name = create_report_pdf(pdf_path, annotations, summary)
#         st.success(f"Report generated: {report_pdf_name}")
#         with open(report_pdf_name, "rb") as file:
#             btn = st.download_button(label="Download Report", data=file, file_name=report_pdf_name)
#     else:
#         st.info("No annotations found and summary not available.")
import os
import fitz  # PyMuPDF
import re
import openai
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import streamlit as st

# Access OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client with the API key
openai.api_key = openai_api_key

# Streamlit UI for uploading PDF
st.title("PDF Annotations and Summary Report")
uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

# Text Cleaning Function
def clean_text(text):
    text = re.sub(r'[^\x20-\x7E]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# Function to Extract Annotations
def extract_annotations(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        st.error(f"Error opening PDF: {e}")
        return []

    annotations = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        for annot in page.annots():
            if annot is None or annot.type[0] not in [8, 9, 10, 11]:
                continue
            annot_type = annot.type[1]
            content = annot.info.get("content", "").strip()
            if not content and annot_type == "Highlight":
                rect = annot.rect
                content = page.get_text("text", clip=rect).strip()
                content = clean_text(content) if content else "No content"
            else:
                content = clean_text(content)
            annotations.append({"page": page_num + 1, "type": annot_type, "content": content})

    doc.close()
    return annotations

# Function to Generate Summary
def generate_summary(highlights_text):
    try:
        # completion = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": "Precisely summarize the following highlights and provide a response in English and French:\n\n" + highlights_text}
        #     ],
        #     max_tokens=150
        # )

        completion = openai.chat.completions.create(
             model="gpt-3.5-turbo",
             messages=[
                 {"role": "system", "content": "You are a helpful assistant."},
                 {"role": "user", "content": "Precisely summarize the following highlights and provide a response in English and French:\n\n" + highlights_text}
             ],
             max_tokens=150
         )
        return completion.choices[0].message.content
        #return completion.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Unable to generate summary."

# Function to Create a Report PDF
def create_report_pdf(original_pdf_path, annotations, summary):
    report_pdf_name = "REPORT_" + os.path.basename(original_pdf_path)
    doc = SimpleDocTemplate(report_pdf_name, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.textColor = colors.darkblue
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Heading2'], textColor=colors.darkgreen)
    normal_style = styles['Normal']

    elements = []
    elements.append(Paragraph("Document Summary and Annotations Report", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Summary:", subtitle_style))
    elements.append(Paragraph(summary, normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Annotations:", subtitle_style))

    for annot in annotations:
        text = f"Page {annot['page']}, {annot['type']}: {annot['content']}"
        elements.append(Paragraph(text, normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    doc.build(elements)
    return report_pdf_name

# Main Execution
if uploaded_pdf:
    pdf_path = uploaded_pdf.name
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    
    # Extract Annotations
    annotations = extract_annotations(pdf_path)

    # Generate Summary
    highlights_text = "\n".join([annot["content"] for annot in annotations])
    summary = generate_summary(highlights_text)

    # Display Summary and Annotations
    if annotations or summary:
        report_pdf_name = create_report_pdf(pdf_path, annotations, summary)
        st.success(f"Report generated: {report_pdf_name}")
        with open(report_pdf_name, "rb") as file:
            btn = st.download_button(label="Download Report", data=file, file_name=report_pdf_name)
    else:
        st.info("No annotations found and summary not available.")
