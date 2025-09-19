from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import FunctionCallTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.ui import Console
from img_gen import generate_image,resize_image
import os
import asyncio
load_dotenv()
gemini_api_key=os.getenv('GOOGLE_API_KEY')

print("Gemini key loaded:", gemini_api_key is not None)


async def main():
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
    art_director_Agent2=AssistantAgent(
        name="art_director2",
        model_client=model_client,
        system_message=open("art_d2_prompt.txt").read().strip()
    )

    # team=RoundRobinGroupChat(
    #     participants=[query_parser_agent,content_developer_agent,art_director_Agent1,],
    #     max_turns=4
    # )
    termination = MaxMessageTermination(max_messages=6)
    selector_prompt = """
    Select the next agent to speak based on these roles:
    {roles}

    Current conversation:
    {history}

    Pick one agent to contribute next.
    """

    # --- Build the SelectorGroupChat team ---
    team = SelectorGroupChat(
        participants=[query_parser_agent, content_developer_agent, art_director_Agent1],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=False  # prevent same agent from speaking twice in a row
    )
    await Console( team.run_stream(task="I want a fun story for 6-8 year olds about a curious little squirrel named Sammy who loves exploring the forest. He meets a wise owl named Olly along the way. The story should be adventurous and cheerful, set in a magical forest, around 5 chapters long. I want it to teach kids that courage helps overcome fears."))


    # task="""I want a fun story for 6-8 year olds about a curious little squirrel named Sammy who loves exploring the forest. He meets a wise owl named Olly along the way. The story should be adventurous and cheerful, set in a magical forest, around 5 chapters long. I want it to teach kids that courage helps overcome fears."
    # """
    # result = await query_parser_agent.run(task="generate a story for my 7 year old girl she like cooking with animals")
   
    # # Suppose `messages` is the list you printed
    # for msg in result.messages:
    #    print(msg.content)
async def main():
    model_client=OpenAIChatCompletionClient(
        model="gemini-2.5-flash",
        api_key=gemini_api_key,
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
    

        

    input="""  "chapter_images": [
    {
      "chapter": 1,
      "image_prompt": "A bright, whimsical cartoon of Sammy the curious squirrel at the top of a tall, sparkling oak tree, peering out over the magical Whispering Woods. The forest floor is covered in glowing flowers, and a slightly mysterious, dark path twists into the distance. Vibrant colors, storybook style."
    },
    {
      "chapter": 2,
      "image_prompt": "A child-friendly digital painting depicting Sammy the squirrel tiptoeing nervously down a winding, slightly shadowy forest path. Tall, ancient trees with swaying, whispering branches loom overhead. In the background, a large, ancient willow tree with long, drooping branches looks mysterious. Cheerful, adventurous atmosphere."
    },
    {
      "chapter": 3,
      "image_prompt": "A warm and charming storybook illustration of Sammy the squirrel looking up, a bit startled, at Olly the wise owl. Olly has moonlight-colored feathers and amber eyes, perched gracefully on a branch of a grand, ancient willow tree. The scene is friendly and gentle, with soft forest light."
    },

    

   """
    # "you are a image generator agent you recieve image prompt inputs and your goal is to generate images then resize that image  using tool you have image_generation , and image_resizer tools available. when you are using image_resizer the output path is 'image_3.png'"
    image_generator=AssistantAgent(
        name="ImageGenerator",
        model_client=model_client,
        system_message=open('img_gen_prompt.txt').read().strip(),
        tools=[image_generation,image_resizer],
        max_tool_iterations=15
    )
    text="A whimsical storybook illustration of Sammy the Squirrel with an excitedly twitching tail, perched high in a tall, ancient oak tree. He gazes down at a mysterious, winding path leading into a vibrant, sparkling magical forest, filled with glowing dewdrops and colorful, fantastical plants. Bright and cheerful, digital painting style."
    await Console(image_generator.run_stream(task=f"here is the ouput of art director 1  {input}"))

if __name__=='__main__':
    asyncio.run(main())
    # text="A whimsical storybook illustration of Sammy the Squirrel with an excitedly twitching tail, perched high in a tall, ancient oak tree. He gazes down at a mysterious, winding path leading into a vibrant, sparkling magical forest, filled with glowing dewdrops and colorful, fantastical plants. Bright and cheerful, digital painting style."
   
    # generate_image(text=text)
    # resize_image("5_story_book\images\generated_image.png", "5_story_book\images\image_medium.png") 