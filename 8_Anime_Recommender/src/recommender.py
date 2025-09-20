from langchain_google_genai import ChatGoogleGenerativeAI
from src.prompt import get_anime_prompt

class AnimeRecommender:
    def __init__(self, retriever, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=api_key
        )
        self.prompt = get_anime_prompt()
        self.retriever = retriever

    def get_recommendation(self, query: str) -> str:
        # 1. Retrieve documents from the vector store
        docs = self.retriever.get_relevant_documents(query)
     

        # 2. Format the docs into a single context string
        context = "\n\n".join(doc.page_content for doc in docs)

        # 3. Prepare the input for the prompt
        # prompt_input = {
        #     "context": context,
        #     "question": query
        # }
     
        prompt_text = self.prompt.format(context=context, question=query)

        # 4. Call the LLM directly with the dict input
        response = self.llm.invoke(prompt_text) 
       
        return response.content
    
