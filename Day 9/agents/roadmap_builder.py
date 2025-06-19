from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.schemas import GapAnalysis, LearningRoadmap
from utils.prompts import ROADMAP_BUILDER_PROMPT
from utils.config import GEMINI_API_KEY  # Centralized config
class RoadmapBuilderAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY,temperature=0.3)
        self.agent = self._setup_agent()
    
    def _setup_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", ROADMAP_BUILDER_PROMPT),
            ("user", "{input}")
        ])
        return prompt | self.llm
    
    def build_roadmap(self, gap_analysis: GapAnalysis) -> LearningRoadmap:
        result = self.agent.invoke({
            "input": f"Build learning roadmap based on: {gap_analysis.json()}"
        })
        return LearningRoadmap.parse_raw(result["output"])