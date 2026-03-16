import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cnd_path = os.path.join(BASE_DIR,"ConditionGeneralAssuranceVarde.pdf")
    

loader = PyPDFLoader(cnd_path)
docs = loader.load()

for i in docs:

    i.metadata = {
        'auteur':"varde11",
        'page label' : '1'
     }

embedding_model = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
docs_chunk = splitter.split_documents(docs)
    
vectorstore = Chroma.from_documents(
documents=docs_chunk,
embedding=embedding_model,
persist_directory=  "app/vectorDB/"
    
 )
print("Données misent à jour dans la vectorDB")
#durée = 1 min