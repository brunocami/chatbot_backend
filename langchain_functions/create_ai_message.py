import os
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import  FAISS
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from config import Config

# Configurar la clave de la API de OpenAI
os.environ["OPENAI_API_KEY"] = Config.OPENAI.API_KEY

# Ubicación del archivo PDF
pdf_file_path = './data/contexto_boatshare.pdf'

# Leer datos desde el archivo PDF y almacenarlos en la variable raw_text
raw_text = ''
pdf_reader = PdfReader(pdf_file_path)
for page in pdf_reader.pages:
    text = page.extract_text()
    if text:
        raw_text += text

# Dividir el texto en fragmentos más pequeños
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
texts = text_splitter.split_text(raw_text)

# Descargar embeddings desde OpenAI
embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_texts(texts, embeddings)


session = {}

def create_chat_session(telefonoCliente, humanMessage): 

    combine_docs_custom_prompt = PromptTemplate.from_template(
        ("""
        Nunca olvides que tu nombre es Boati y trabajas como Asistente de ventas en Boat Share.

        Tu objetivo es contactar a un posible cliente para mantener una conversacion amigable con el potencial cliente brindando infarmacion acerca de los servicios de boatshare. Utilizarás un chatbot como medio de contacto, brindando asistencia y generando ventas.
        
        Responde amablemente a la pregunta del cliente: ({question})
        
        Recuerda mantener tus respuestas breves y concisas para captar la atención del usuario. Evita hacer demasiadas preguntas al cliente a menos que sea necesario, y espera a que te pregunte sobre los productos.

        ¡Genera solo una respuesta a la vez!

        Si no sabes la respuesta a una pregunta o no encuentras informacion en el texto proporcionado, preguntale al cliente si prefiere agendar una llamada con un agente de ventas.
    
        Esta es la informacion acerca de boatshare basada en la pregunta que realizo el cliente: ({context}) 
         
        ¡Importante! ¡Si no encuntras informacion suficiente para responder a la pregunta del cliente dile que no tienes respuesta a su pregunta y ofrecele que un agente de ventas los llame para brindarle informacion mas concisa!
        """)
    )

    if telefonoCliente not in session:
        session[telefonoCliente] = {
            'conversation_chain': ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(temperature=0),
                retriever=docsearch.as_retriever(),
                verbose=True,
                memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True),
                combine_docs_chain_kwargs=dict(prompt=combine_docs_custom_prompt),
            )
        }
        
    if "reiniciar sesion" in humanMessage:
        session.pop(telefonoCliente)
        print(f"chat session: {session}")
    else: 
        return session[telefonoCliente]['conversation_chain'].run(humanMessage)
