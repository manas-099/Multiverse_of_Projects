from src.recommender import AnimeRecommender
from src.vectorStore import VecotstoreBuilder
from config.config import GOOGLE_API_KEY,HUGGINGFACEHUB_API_TOKEN
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger=get_logger(__name__)

class AnimeRecommendationPipeline:
    def __init__(self,persist_dir="chroma_db"):
        try:
            logger.info({"Intialliaing Recommendation pipeline"})
            vector_builder=VecotstoreBuilder(csv_path="",persist_dir=persist_dir)
            retriever=vector_builder.load_vectorstore().as_retriever()
            self.recommender=AnimeRecommender(retriever,GOOGLE_API_KEY)
            logger.info("Pipe line intialized successfully")
        except Exception as e:
            logger.error({f"faild to intialize pipeline {str(e)}"})
            raise CustomException("error during pipeline intialization",e)
    def recommend(self,query:str)->str:
        try:
            logger.info(f"Recieve a query {query}")   
            recommendation=self.recommender.get_recommendation(query)
            logger.info("Recommendation generated succesfully")
            return recommendation
        except Exception as e:
            logger.error(f"failed to intialize pipeline {str(e)}")
            raise CustomException("error during getting  recommendation",e) 