from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(docs, filename):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )

    chunks = splitter.split_documents(docs)

    for i, chunk in enumerate(chunks):

        chunk.metadata["doc_name"] = filename
        chunk.metadata["chunk_id"] = i

    return chunks