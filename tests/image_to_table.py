from biobridge.utilities.image_to_table import image_to_text, save_to_excel, save_to_csv, text_to_dataframe

image_path = 'image.png'  # Replace with the path to your image
output_excel = 'output.xlsx'
output_csv = 'output.csv'
tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Replace with your Tesseract path

df = image_to_text(image_path, tesseract_cmd)
df = text_to_dataframe(df)
save_to_excel(df, output_excel)
save_to_csv(df, output_csv)

print("Table has been extracted and saved.")
