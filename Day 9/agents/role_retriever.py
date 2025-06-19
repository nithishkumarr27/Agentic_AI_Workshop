from langchain.agents import AgentExecutor, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.schemas import RoleRequirements
from utils.prompts import ROLE_RETRIEVAL_PROMPT
from tools.vector_store import retrieve_similar_jobs
from utils.config import GEMINI_API_KEY  # Centralized config
class RoleRetrieverAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",google_api_key=GEMINI_API_KEY,  temperature=0.1)
        
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()
    
    def _setup_tools(self):
        return [
            Tool(
                name="job_retriever",
                func=retrieve_similar_jobs,
                description="Retrieve similar job descriptions from vector store"
            )
        ]
    
    def _setup_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", ROLE_RETRIEVAL_PROMPT),
            ("user", "{input}")
        ])
        
        agent = prompt | self.llm
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def retrieve_requirements(self, role_title: str) -> RoleRequirements:
        result = self.agent.invoke({
            "input": f"Retrieve requirements for role: {role_title}"
        })
        return RoleRequirements.parse_raw(result["output"])