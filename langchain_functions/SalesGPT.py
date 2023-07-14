import os
from config import Config

os.environ["OPENAI_API_KEY"] = Config.OPENAI.API_KEY

from typing import Dict, List, Any
from langchain.llms import BaseLLM
from pydantic import BaseModel, Field
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain_functions.SalesCoversationChain import SalesConversationChain
from langchain_functions.StageAnalyzerChain import StageAnalyzerChain
    
llm = ChatOpenAI(temperature=0.9)

class SalesGPT(Chain, BaseModel):
    """Controller model for the Sales Agent."""

    conversation_history: List[str] = []
    current_conversation_stage: str = "1"
    stage_analyzer_chain: StageAnalyzerChain = Field(...)
    sales_conversation_utterance_chain: SalesConversationChain = Field(...)

    conversation_stage_dict: Dict = {
        "1": "Saludo e introducción: Inicia la conversación con un saludo cordial y preséntate como representante de La compañia.",
        "2": "Pregunta por el nombre: Solicita el nombre del cliente para personalizar la interacción.",
        "3": """Descubre las necesidades: Indaga sobre los servicios de Boar Share en los que está interesado el cliente, como las "Salidas Diarias" o la "Membresía Anual". Ofrece una breve descripción de cada opción.""",
        "4": "Cita para visitar la oficina: Propón al cliente agendar una cita para que visite nuestra oficina. Esta visita le permitirá conocer nuestras embarcaciones en detalle.",
        "5": "Información adicional: Pregunta la edad del cliente y solicita el DNI para completar el registro.",
        "6": """Genera un reporte: Una vez que obtengas los datos del cliente, no programes una cita en ese momento. En su lugar, redacta un reporte con el siguiente formato y envíalo al cliente: "|| Nombre de cliente || Edad del cliente || Servicio en el cual está interesado || día en que quiere visitar la oficina ||". Reemplaza los campos correspondientes con los datos del cliente."""
    }


    salesperson_name: str = ""
    salesperson_role: str = ""
    company_name: str = ""
    company_location: str = ""
    company_products: str = ""
    company_business: str = ""
    company_values: str = ""
    conversation_purpose: str = ""


    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, "1")

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def seed_agent(self):
        # Step 1: seed the conversation
        self.current_conversation_stage = self.retrieve_conversation_stage("1")
        self.conversation_history = []

    def determine_conversation_stage(self):
        conversation_stage_id = self.stage_analyzer_chain.run(
            conversation_history='"\n"'.join(self.conversation_history),
            current_conversation_stage=self.current_conversation_stage,
        )

        self.current_conversation_stage = self.retrieve_conversation_stage(
            conversation_stage_id
        )

        return self.current_conversation_stage

    def human_step(self, human_input):
        # process human input
        human_input = human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    def step(self):
        self._call(inputs={})
        return self.conversation_history

    def _call(self, inputs: Dict[str, Any]) -> None:
        """Run one step of the sales agent."""

        # Generate agent's utterance
        ai_message = self.sales_conversation_utterance_chain.run(
            salesperson_name=self.salesperson_name,
            salesperson_role=self.salesperson_role,
            company_name=self.company_name,
            company_location=self.company_location,
            company_products=self.company_products,
            company_business=self.company_business,
            company_values=self.company_values,
            conversation_purpose=self.conversation_purpose,
            conversation_history="\n".join(self.conversation_history),
            conversation_stage=self.current_conversation_stage,
        )

        # Add agent's response to conversation history
        self.conversation_history.append(ai_message)

        return ai_message.rstrip(" <END_OF_TURN>")

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SalesGPT":
        stage_analyzer_chain = StageAnalyzerChain.from_llm(llm, verbose=verbose)
        sales_conversation_utterance_chain = SalesConversationChain.from_llm(
            llm, verbose=verbose
        )

        return cls(
            stage_analyzer_chain=stage_analyzer_chain,
            sales_conversation_utterance_chain=sales_conversation_utterance_chain,
            verbose=verbose,
            **kwargs,
        )
    
# Set up of your agent

# Agent characteristics - can be modified

conversation_stages = {
        "1": "Saludo e introducción: Inicia la conversación con un saludo cordial y preséntate como representante de La compañia.",
        "2": "Pregunta por el nombre: Solicita el nombre del cliente para personalizar la interacción.",
        "3": """Descubre las necesidades: Indaga sobre los servicios de Boar Share en los que está interesado el cliente, como las "Salidas Diarias" o la "Membresía Anual". Ofrece una breve descripción de cada opción.""",
        "4": "Cita para visitar la oficina: Propón al cliente agendar una cita para que visite nuestra oficina. Esta visita le permitirá conocer nuestras embarcaciones en detalle.",
        "5": "Información adicional: Pregunta la edad del cliente y solicita el DNI para completar el registro.",
        "6": """Genera un reporte: Una vez que obtengas los datos del cliente, no programes una cita en ese momento. En su lugar, redacta un reporte con el siguiente formato y envíalo al cliente: "|| Nombre de cliente || Edad del cliente || Servicio en el cual está interesado || día en que quiere visitar la oficina ||". Reemplaza los campos correspondientes con los datos del cliente."""
}

config = dict(
    salesperson_name="Boati",
    salesperson_role="Representante de Desarrollo de Negocios",
    company_name="Boat Share",
    company_location="Guarderia Nautica Neptuno, Localidad de Tigre",
    company_products="Boat Share Ofrece 3 tipos de Membersias diferentes segun la categoria de las lanchas que desee el cliente: Alta, con un precio de 3000 US$ mensuales - Media, con un precio de 2000US$ mensuales - Baja, con un precio de 800US$ mensuales. Ademas en caso de que solo quieran dar paseos por el dia ofrecemos salidas diarias en cualquiera de nuestras dos embarcaciones: Guther para 12 personas con un precio de 600 US$ el dia y El Ponton para 14 personas con un precio de 400US$ el dia. Ambos incluyen un paseo por el delta y comer arriba del barco o parar en un restaurante en el rio segun lo deseen los clientes.",
    company_business="Boat Shaer es un tiempo compartido de lanchas que le brinda a sus clientes la posibilidad de ser propietarios de una embarcacion sin tener que comprarla ni asumir los gastos de mantenimiento pagando una cuota todos los meses.",
    company_values="Nuestro compormiso con los clientes es que puedan disfrutar de sus propia embarcacion sin tener que comprarla, y puedan vivir la experiencia nautica a un precio mucho menor que el de tener que comprar tu propia lancha.",
    conversation_purpose="Lograr que el cliente quiera ir a la oficina de boat share para ver las embarcaciones y cerrar la venta",
    conversation_stage=conversation_stages.get(
        "1",
        "Introducción: Comienza la conversación presentándote a ti mismo y a tu empresa. Sé cortés y respetuoso, manteniendo un tono profesional en la conversación.",
    ),

)

sales_agent = SalesGPT.from_llm(llm, verbose=False, **config)