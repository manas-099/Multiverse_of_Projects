from google import genai
from google.genai import types
# from PIL import Image
from PIL import Image as PILImage 

from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
import os
gemini_api_key=os.getenv('GOOGLE_API_KEY')

print("Gemini key loaded:", gemini_api_key is not None)
os.environ['GOOGLE_API_KEY']=gemini_api_key


def generate_image(text:str):


    client = genai.Client()

    prompt = (text)


    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[prompt],

    )
    flag=False
    for part in response.candidates[0].content.parts:
        # if part.text is not None:
        #     pass
        if part.inline_data is not None:
            image = PILImage.open(BytesIO(part.inline_data.data))
            
            image.save("generated_image.png")
            flag=True
            
    return flag


def resize_image(input_path: str, output_path: str):
    """
    Resize an image to a new size and save it.

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path to save the resized image.
        new_size (tuple): Target size as (width, height).
    """
    # save_dir = r"5_story_book/images"
    # os.makedirs(save_dir, exist_ok=True)  # ✅ auto-create directory if missing
    with PILImage.open(input_path) as img: # Use PILImage.open instead of Image.open
        original_size = img.size
        resized_img = img.resize((450,501), PILImage.Resampling.LANCZOS) # Use PILImage.Resampling.LANCZOS
        resized_img.save(output_path)
        return f"✅ Resized from {original_size} to {(450,501)}, saved to {output_path}"


if __name__=='__main__':
    # res=generate_image(text="Create a picture of a lion playing with a baby girl in garden bear is very qute")
    # print(res)
    
    res=resize_image("generated_image.png", "image_1.png")
    print(res)
    # resize_image("generated_image.png", "image_2.png") 
   


