import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import json
from typing import Dict, Any

class NLPAccessParser(BaseOutputParser):
    def parse(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except:
            return {"action": "unknown", "user_lan_id": None, "project": None, "confidence": 0.0}

class NLPProcessor:
    def __init__(self):
        self.llm = OpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt_template = PromptTemplate(
            template="""Analyze the following user message and extract access control information.
            Return JSON with: action, user_lan_id, project, confidence.
            
            Possible actions:
            - onboard_user: When adding a new user to projects
            - grant_access: When requesting access to a project
            - revoke_access: When removing access from a project
            - query_access: When checking current access
            - notify_admin: When user notifies about project changes
            
            User roles:
            - admin/hr: Can perform all actions
            - user: Can only request access and notify about changes
            
            Message: {message}
            User role: {user_role}
            
            Return only JSON:""",
            input_variables=["message", "user_role"]
        )
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            output_parser=NLPAccessParser()
        )
    
    def process_message(self, message: str, user_role: str) -> Dict[str, Any]:
        try:
            result = self.chain.run(message=message, user_role=user_role)
            return result
        except Exception as e:
            return {"action": "error", "error": str(e)}