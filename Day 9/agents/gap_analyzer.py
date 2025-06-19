from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.schemas import UserProfile, RoleRequirements, GapAnalysis
from utils.prompts import GAP_ANALYSIS_PROMPT
from utils.config import GEMINI_API_KEY  # Centralized config
class GapAnalyzerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY,temperature=0.1)
        self.agent = self._setup_agent()
    
    def _setup_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", GAP_ANALYSIS_PROMPT),
            ("user", "{input}")
        ])
        return prompt | self.llm
    
    def analyze_gaps(self, profile: UserProfile, requirements: RoleRequirements) -> GapAnalysis:
        input_data = {
            "profile": profile.json(),
            "requirements": requirements.json()
        }
        result = self.agent.invoke({
            "input": f"Analyze skill gaps: {input_data}"
        })
        return GapAnalysis.parse_raw(result["output"])