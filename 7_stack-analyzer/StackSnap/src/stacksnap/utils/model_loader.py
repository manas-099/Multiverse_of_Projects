import logging
import os


import os
from dotenv import load_dotenv
from typing import Literal,Optional,Any
from pydantic import BaseModel,Field

from stacksnap.utils.config_loader import load_config

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

class ConfigLoader:
    def __init__(self):
        print(f" loaded config...")
        self.config=load_config()
    def __getitem__(self,key):
        return self.config[key]
    
class ModelLoader(BaseModel):
    model_provider:Literal['groq','gemini']="gemini"
    config:Optional[ConfigLoader]=Field(default=None,exclude=True)

    def model_post_init(self, context:Any)->None:
        self.config=ConfigLoader()

    class Config:
        arbitrary_types_allowed = True
    def load_llm(self):
        print("llm is loading..")
        print(f"loading model from provider:{self.model_provider}")

        if self.model_provider=="groq":
            print("loading groq llm ")
            groq_api_key=os.getenv("GROQ_API_KEY")

            model_name=self.config['llm']['groq']['model_name']
            llm=ChatGroq(model=model_name,api_key=groq_api_key)
        if self.model_provider=="gemini":
            print("loading gemini llm ")
            groq_api_key=os.getenv("GOOGLE_API_KEY")

            model_name=self.config['llm']['gemini']['model_name']
            llm=ChatGoogleGenerativeAI(model=model_name,api_key=groq_api_key)
        
        return llm
    

if __name__=="__main__":
    obj=ModelLoader()
    print(obj.load_llm())