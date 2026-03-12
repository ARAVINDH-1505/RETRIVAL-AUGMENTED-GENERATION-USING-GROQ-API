from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader
)


def load_documents():

    text_loader = DirectoryLoader(
        "data/documents",
        glob="**/*.txt",
        loader_cls=TextLoader
    )

    pdf_loader = DirectoryLoader(
        "data/documents",
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    text_docs = text_loader.load()
    pdf_docs = pdf_loader.load()

    documents = text_docs + pdf_docs

    print(f"Loaded {len(documents)} documents")

    return documents