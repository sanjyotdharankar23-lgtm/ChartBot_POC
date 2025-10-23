import os
import json
import re
from typing import Dict, Any, List
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from openai import OpenAI as OpenAIClient

class NLPAccessParser(BaseOutputParser):
    def parse(self, text: str) -> Dict[str, Any]:
        try:
            # Clean the text to extract JSON
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return {"action": "unknown", "user_lan_id": None, "project": None, "confidence": 0.0}

class NLPProcessor:
    def __init__(self):
        self.llm = OpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo"
        )

        self.prompt_template = PromptTemplate(
            template="""Analyze the following user message about access control and extract relevant information.
            Return JSON with: action, user_lan_id, project, confidence, and additional_info.

            Possible actions:
            - onboard_user: When adding a new user to projects (e.g., "sanjyot dharankar is working in det,cart,oap")
            - grant_access: When requesting access to a project (e.g., "give access for eo project")
            - revoke_access: When removing access from a project (e.g., "remove access from oap project")
            - query_access: When checking current access (e.g., "what access does sanjyot have")
            - notify_change: When user notifies about project changes (e.g., "I am no longer in det project")

            Extract user information: Look for names and LAN IDs
            Extract project information: Look for project codes like DET, CART, OAP, PMBA, EO

            Message: {message}
            User role: {user_role}

            Return only valid JSON, no other text:""",
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
            print(f"NLP processing error: {e}")
            return {"action": "error", "error": str(e)}

    def extract_projects_from_text(self, text: str) -> List[str]:
        projects = ["det", "cart", "oap", "pmba", "eo"]
        found_projects = []
        text_lower = text.lower()
        
        for project in projects:
            if project in text_lower:
                found_projects.append(project.upper())
                
        return found_projects

    def extract_user_info(self, text: str) -> Dict[str, str]:
        # Simple pattern matching for names and LAN IDs
        patterns = {
            'lan_id': r'[a-z]{2,8}\d+',
            'full_name': r'[A-Z][a-z]+ [A-Z][a-z]+'
        }
        
        user_info = {}
        
        # Look for LAN ID pattern
        lan_match = re.search(patterns['lan_id'], text.lower())
        if lan_match:
            user_info['lan_id'] = lan_match.group()
            
        # Look for full name pattern
        name_match = re.search(patterns['full_name'], text)
        if name_match:
            user_info['full_name'] = name_match.group()
            
        return user_info