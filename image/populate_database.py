import argparse
import math
import os
import shutil
import glob
import pandas as pd
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag_app.get_embedding_function import get_embedding_function

CHROMA_PATH = "src/data/chroma"
DATA_SOURCE_PATH = "src/data/source"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_csv_documents() + load_model_documents()
    add_to_chroma(documents)

# load datasets
def load_csv_documents():
    documents = []
    csv_files = glob.glob(os.path.join(DATA_SOURCE_PATH, "*.csv"))
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        num_rows = len(df)
        group_size = 24
        num_groups = math.ceil(num_rows / group_size)
        for group_idx in range(num_groups):
            start = group_idx * group_size
            end = min(start + group_size, num_rows)
            group_df = df.iloc[start:end]
            content = group_df.to_json(orient="records", lines=True)
            doc_id = f"{os.path.basename(csv_file)}:group:{group_idx}"
            date_start = str(group_df['datetime'].iloc[0])[:10]
            date_end = str(group_df['datetime'].iloc[-1])[:10]
            metadata = {
                "id": doc_id,
                "csv_file": os.path.basename(csv_file),
                "group_index": group_idx,
                "row_range": f"{start}-{end-1}",
                "date_range": f"{date_start}_{date_end}"
            }
            documents.append(Document(page_content=content, metadata=metadata))
    return documents

#loading model files: notebooks and keras models (.ipynb and .h5 files may need some pre processing to work)
def load_model_documents():
    documents = []
    model_files = glob.glob(os.path.join(DATA_SOURCE_PATH, "*.ipynb")) + \
                  glob.glob(os.path.join(DATA_SOURCE_PATH, "*.h5"))
    for model_file in model_files:
        ext = os.path.splitext(model_file)[1].lower()
        if ext == ".ipynb":
            with open(model_file, "r", encoding="utf-8") as f:
                content = f.read()
            metadata = {
                "id": f"{os.path.basename(model_file)}",
                "type": "notebook",
                "filename": os.path.basename(model_file),
                "path": model_file
            }
        elif ext == ".h5":
            content = f"Keras model file: {os.path.basename(model_file)}"
            metadata = {
                "id": f"{os.path.basename(model_file)}",
                "type": "keras_model",
                "filename": os.path.basename(model_file),
                "path": model_file
            }
        else:
            continue
        documents.append(Document(page_content=content, metadata=metadata))
    return documents


def add_to_chroma(documents):
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )
    # Remove duplicates within this batch (shouldn't happen, but just in case)
    seen = set()
    unique_docs = []
    for doc in documents:
        if doc.metadata["id"] not in seen:
            unique_docs.append(doc)
            seen.add(doc.metadata["id"])
    if unique_docs:
        print(f"👉 Adding new documents: {len(unique_docs)}")
        doc_ids = [doc.metadata["id"] for doc in unique_docs]
        db.add_documents(unique_docs, ids=doc_ids)
    else:
        print("✅ No new documents to add")

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

if __name__ == "__main__":
    main()