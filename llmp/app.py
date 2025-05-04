from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.llms import Ollama  # <- Use langchain_community
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.prompt import *

import os

app = Flask(__name__)

# ✅ Set Pinecone API key directly or load via dotenv
os.environ["PINECONE_API_KEY"] = "pcsk_4paSYZ_U58HJwaSWY5k39ZFXWGpCpwaPtgiadAJsGmHTb63AtqNkfWweDJwNioWPaSetKN"

# ✅ Load embeddings
embeddings = download_hugging_face_embeddings()

# ✅ Connect to Pinecone index
index_name = "quickstart"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# ✅ Use Ollama instead of OpenAI
llm = Ollama(model="llama3", temperature=0.4)

# ✅ Set up RAG chain
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    print("User input:", msg)
    response = rag_chain.invoke({"input": msg})
    print("Response:", response["answer"])
    return str(response["answer"])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
