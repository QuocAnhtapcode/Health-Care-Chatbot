from flask import Flask, render_template, jsonify, request, redirect, url_for
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
import mysql.connector

app = Flask(__name__)

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize embeddings and vector store
embeddings = download_hugging_face_embeddings()
index_name = "healthcarebot"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Setup LLM and prompt chain
llm = OpenAI(temperature=0.4, max_tokens=500)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Setup MySQL connection
mysql_db = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="1234",  
    database="healthcare"
)
cursor = mysql_db.cursor()

# Routes
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/chat")
def chat_page():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    response = rag_chain.invoke({"input": msg})
    print("Response : ", response["answer"])
    return str(response["answer"])

@app.route("/book", methods=["POST"])
def book():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    address = request.form["address"]
    phone = request.form["phone"]

    sql = "INSERT INTO appointments (first_name, last_name, address, phone) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (first_name, last_name, address, phone))
    mysql_db.commit()

    return redirect(url_for("index"))

@app.route("/admin/appointments")
def admin_appointments():
    cursor.execute("SELECT * FROM appointments ORDER BY created_at DESC")
    appointments = cursor.fetchall()
    return render_template("admin_appointments.html", appointments=appointments)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
