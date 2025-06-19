# from langchain.agents import AgentExecutor, Tool
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from utils.schemas import UserProfile
# from utils.prompts import PROFILE_ANALYSIS_PROMPT
# from tools.pdf_parser import parse_resume_pdf
# from tools.skill_extractor import extract_skills
# from utils.config import GEMINI_API_KEY  # Centralized config
# from langchain.agents import Tool, AgentExecutor
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.tools import tool  # Add this import
# from langchain.agents import AgentExecutor, Tool
# from langchain_core.callbacks import BaseCallbackHandler
# class CustomCallbackHandler(BaseCallbackHandler):
#     def on_agent_action(self, action, **kwargs):
#         if isinstance(action, tuple):
#             # Handle tuple outputs gracefully
#             print(f"Agent action: {str(action)}")
#         else:
#             print(f"Agent action: {action.log}")

# class ProfileAnalyzerAgent:
#     def __init__(self):
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-flash",
#             google_api_key=GEMINI_API_KEY,
#             temperature=0.2
#         )
#         self.callbacks = [CustomCallbackHandler()]
#         self.tools = self._setup_tools()
#         self.agent = self._setup_agent()

#     def _setup_tools(self):
#         # Proper Tool initialization
#         return [
#             Tool(
#                 name="pdf_parser",
#                 func=parse_resume_pdf,
#                 description="Extracts text from PDF resumes",
#                 return_direct=True  # Important for single-tool agents
#             ),
#             Tool(
#                 name="skill_extractor",
#                 func=extract_skills,
#                 description="Identifies technical and soft skills from text",
#                 return_direct=True
#             )
#         ]

#     def _setup_agent(self):
#         agent = (
#             {
#                 "input": lambda x: x["input"],
#                 "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
#             }
#             | prompt
#             | self.llm
#             | self._parse_output  # Add this new method
#         )
#         return AgentExecutor(
#             agent=agent,
#             tools=self.tools,
#             callbacks=self.callbacks,
#             verbose=True
#         )
#     def analyze(self, input_data: str) -> UserProfile:
#         if not input_data.strip():
#           raise ValueError("Empty input provided")

#         result = self.agent.invoke({
#             "input": f"Analyze this profile data: {input_data}"
#         })
#         return UserProfile.parse_raw(result["output"])
#     def _parse_output(self, output):
#         """Ensure consistent output format"""
#         if isinstance(output, tuple):
#             return {"output": output[0]}
#         return output
# # from langchain.agents import AgentExecutor, Tool
# # from langchain_core.callbacks import BaseCallbackHandler

# # class CustomCallbackHandler(BaseCallbackHandler):
# #     def on_agent_action(self, action, **kwargs):
# #         if isinstance(action, tuple):
# #             # Handle tuple outputs gracefully
# #             print(f"Agent action: {str(action)}")
# #         else:
# #             print(f"Agent action: {action.log}")

# # class ProfileAnalyzerAgent:
# #     def __init__(self):
# #         self.llm = ChatGoogleGenerativeAI(
# #             model="gemini-1.5-flash",
# #             google_api_key=GEMINI_API_KEY,
# #             temperature=0.2
# #         )
# #         self.callbacks = [CustomCallbackHandler()]
# #         self.tools = self._setup_tools()
# #         self.agent = self._setup_agent()

# #     def _setup_agent(self):
# #         agent = (
# #             {
# #                 "input": lambda x: x["input"],
# #                 "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
# #             }
# #             | prompt
# #             | self.llm
# #             | self._parse_output  # Add this new method
# #         )
# #         return AgentExecutor(
# #             agent=agent,
# #             tools=self.tools,
# #             callbacks=self.callbacks,
# #             verbose=True
# #         )

# #     def _parse_output(self, output):
# #         """Ensure consistent output format"""
# #         if isinstance(output, tuple):
# #             return {"output": output[0]}
# #         return output
from langchain.agents import AgentExecutor, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.schemas import UserProfile
from utils.prompts import PROFILE_ANALYSIS_PROMPT
from tools.pdf_parser import parse_resume_pdf
from tools.skill_extractor import extract_skills
from typing import List, Dict, Any
from langchain.agents import create_tool_calling_agent 
from utils.config import GEMINI_API_KEY  # Centralized config
def format_log_to_str(intermediate_steps: List[tuple]) -> str:
    """Convert agent's intermediate steps to a readable string"""
    log_lines = []
    for i, (action, observation) in enumerate(intermediate_steps):
        tool_name = getattr(action, 'tool', str(action))
        log_lines.append(f"Step {i+1}: {tool_name} - {observation}")
    return "\n".join(log_lines)

class ProfileAnalyzerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.2
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PROFILE_ANALYSIS_PROMPT),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")  # This is crucial for the scratchpad
        ])
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()


    def _setup_agent(self):
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
            }
            | prompt
            | self.llm
            | self._parse_output  # Add this new method
        )
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            callbacks=self.callbacks,
            verbose=True
        )

    def _setup_agent(self) -> AgentExecutor:
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    def _parse_output(self, output: Any) -> Dict[str, str]:
        """Ensure consistent output format"""
        if isinstance(output, tuple):
            return {"output": output[0]}
        if isinstance(output, str):
            return {"output": output}
        return output

    def analyze(self, input_data: str) -> UserProfile:
        """Main analysis method"""
        try:
            result = self.agent.invoke({
                "input": f"Analyze this profile data: {input_data}",
                # agent_scratchpad will be automatically handled by the agent executor
            })
            return UserProfile.parse_raw(result["output"])
        except Exception as e:
            raise RuntimeError(f"Profile analysis failed: {str(e)}") from e