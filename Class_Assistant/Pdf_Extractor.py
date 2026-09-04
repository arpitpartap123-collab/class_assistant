import pymupdf


def extract_text(path):
    doc = pymupdf.open(path)

    text = ""

    for page in doc:
        text = text + page.get_text()

    doc.close()

    return text


def page_count(path):
    doc = pymupdf.open(path)

    pages = len(doc)

    doc.close()

    return pages