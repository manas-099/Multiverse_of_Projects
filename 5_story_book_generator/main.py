from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import FunctionCallTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from img_gen import generate_image,resize_image
# from pdf_routh import create_storybook_pdf
from createStoryBook import create_storybook_pdf
from autogen_agentchat.ui import Console
import os
import asyncio
load_dotenv()
gemini_api_key=os.getenv('GOOGLE_API_KEY')

print("Gemini key loaded:", gemini_api_key is not None)

async def main(task:str):
    model_client=OpenAIChatCompletionClient(
        model="gemini-2.5-flash",
        api_key=gemini_api_key,
    )

    query_parser_agent=AssistantAgent(
        name="query_parser_agent",
        model_client=model_client,
        system_message=open("q_parser.txt").read().strip()
    )
    content_developer_agent=AssistantAgent(
        name="content_developer",
        model_client=model_client,
        system_message=open("c_dev.txt").read().strip()
    )
    art_director_Agent1=AssistantAgent(
        name="art_director",
        model_client=model_client,
        system_message=open("art_d_prompt.txt").read().strip()
    )
    async def image_generation(text: str) -> str:
        image_generated=generate_image(text=text)
        if image_generated:
            return f"image is generated for the input:{text}"
        else:
            return f"could not generate image !!!"
    async def image_resizer(output_path:str) -> str:
        response=resize_image(input_path="generated_image.png",output_path=output_path)
        return response
    async def pdf_crafter(pages: list[dict],title:str) -> str:
        response=create_storybook_pdf(pages=pages,title=title)
        return response

    pdf_maker=AssistantAgent(
        name="pdf_maker",
        model_client=model_client,
        system_message=open('pdf_maker.txt').read().strip(),
        tools=[pdf_crafter],
        max_tool_iterations=2,
    )
    image_generator=AssistantAgent(
        name="ImageGenerator",
        model_client=model_client,
        system_message=open('img_gen_prompt.txt').read().strip(),
        tools=[image_generation,image_resizer],
        max_tool_iterations=30
    )
    art_director_Agent2=AssistantAgent(
        name="art_director2",
        model_client=model_client,
        system_message=open("art_d2_prompt.txt").read().strip()
    )

    team=RoundRobinGroupChat(
        participants=[query_parser_agent,content_developer_agent,art_director_Agent1,image_generator,art_director_Agent2,pdf_maker],
        max_turns=6
    )
    await Console( team.run_stream(task=task))


    # task="""I want a fun story for 6-8 year olds about a curious little squirrel named Sammy who loves exploring the forest. He meets a wise owl named Olly along the way. The story should be adventurous and cheerful, set in a magical forest, around 5 chapters long. I want it to teach kids that courage helps overcome fears."
    # """
    # result = await query_parser_agent.run(task="generate a story for my 7 year old girl she like cooking with animals")
   
    # # Suppose `messages` is the list you printed
    # for msg in result.messages:
    #    print(msg.content)


if __name__=='__main__':
    task=input("enter here :")
    asyncio.run(main(task=task))