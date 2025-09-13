import pytesseract
from PIL import Image
import pandas as pd


def image_to_text(image_path, tesseract_path):
    # Set the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    # Open the image file
    image = Image.open(image_path)
    # Use Tesseract to do OCR on the image
    text = pytesseract.image_to_string(image)
    return text


def text_to_dataframe(text):
    # Split the text into lines
    lines = text.split('\n')
    # Split each line into columns
    data = [line.split() for line in lines if line.strip()]
    # Create a DataFrame
    df = pd.DataFrame(data)
    return df


def save_to_csv(df, output_path):
    df.to_csv(output_path, index=False, header=False)


def save_to_excel(df, output_path):
    df.to_excel(output_path, index=False, header=False)
