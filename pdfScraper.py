import pdfplumber

class PDFScraper:
    """Investiagtes occurrences of words in pdf files"""
    def __init__(self, pdf_file_path: str) -> None:
        self.__pdf_file_path = pdf_file_path

    def search_pdf_for_words(self, keywords: list[str]) -> str:
        """Returns first found keyword"""
 
        with pdfplumber.open(self.__pdf_file_path) as pdf:
            text = pdf.pages[0].extract_text()
            for word in keywords:
                if word in text:
                    return word
                    