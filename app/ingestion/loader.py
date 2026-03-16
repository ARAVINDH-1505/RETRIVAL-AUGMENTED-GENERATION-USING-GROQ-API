from langchain_community.document_loaders import PyPDFLoader
import os


def load_documents():

    path = "data/documents"

    documents = []
    filename = None

    for file in os.listdir(path):

        if file.endswith(".pdf"):

            filename = file

            loader = PyPDFLoader(os.path.join(path, file))

            docs = loader.load()

            documents.extend(docs)

    return documents, filename