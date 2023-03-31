# Source: http://etienned.github.io/posts/extract-text-from-word-docx-simply/


try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile


"""
Module that extract text from MS XML Word document (.docx).
(Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
"""

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'


def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.iter(PARA):
        texts = [node.text
                 for node in paragraph.iter(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(' '.join(texts))

    return '\n\n'.join(paragraphs)


if __name__ == "__main__":
    import tkinter.filedialog as tkd
    docx_file_path = tkd.askopenfilename(filetypes=[('Microsoft Word Documents', '*.docx')])
    text = get_docx_text(docx_file_path)
    print(text)