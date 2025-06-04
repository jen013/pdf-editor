from pdf_editor import PdfEditor

def main():
    with PdfEditor() as pdf_editor_app:
        pdf_editor_app.run()

    
if __name__ == '__main__':
    main()