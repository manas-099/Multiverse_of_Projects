from dotenv import  load_dotenv

from pipeline.inference_pipe import AnimeRecommendationPipeline
import streamlit as st
st.set_page_config(page_title="Anime Recommender",layout="wide")
load_dotenv()

@st.cache_resource
def init_pipeline():
    return AnimeRecommendationPipeline()

pipeline=init_pipeline()

st.title("Anime recommender system")
query=st.text_input("enter you anime preferences ")

if query:
    with st.spinner("Fetching recommendations for you.."):
        response=pipeline.recommend(query)
        st.markdown("###Recommendations ")
        st.write(response)
