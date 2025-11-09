import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
import random
import urllib.parse
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

# -------------------- LLM Setup --------------------

os.environ["GOOGLE_API_KEY"] =os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)



def create_meme_prompt(topic, mood, language="english", image_description=None):
    """Generates image description and caption prompt using Gemini."""
    if image_description is None:
        desc_prompt = f"""
        Create a short and funny image description suitable for a meme.
        Topic: {topic}
        Mood: {mood}
        Rules:
        - Keep it visual (describe a scene).
        - Keep it short (max 1 sentence).
        - Make it meme-friendly.
        - No caption, just describe the image.
        """
        desc_result = llm.invoke(desc_prompt).content
        image_description = desc_result.strip()
    
    caption_prompt = f"""
    Create a meme caption.
    Topic: {topic}
    Mood: {mood}
    Language: {language}
    Image description: {image_description}
    Rules:
    - Keep it short, punchy.
    - Do not give options, just the caption.
    """
    return caption_prompt.strip(), image_description

def generate_image_from_description(description):
    """Generates Pollinations image URL with safe URL encoding."""
    encoded_prompt = urllib.parse.quote(description)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}"

def overlay_caption(img, caption):
    """Overlay meme-style caption with dynamic font sizing and smart placement."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_size = max(20, int(height / 10))
    try:
        font = ImageFont.truetype("impact.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def get_text_size(text):
        bbox = draw.textbbox((0,0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return w, h

    def draw_text(text, x, y):
        outline = max(2, int(height / 200))
        for dx in range(-outline, outline+1):
            for dy in range(-outline, outline+1):
                draw.text((x+dx, y+dy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

    text = caption.upper()
    words = text.split()
    max_width = width - 20
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        w, _ = get_text_size(test_line)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    if len(lines) <= 2 or random.random() < 0.5:
        total_height = sum(get_text_size(line)[1] for line in lines)
        y_start = height - total_height - 10
        for line in lines:
            w, h = get_text_size(line)
            x = (width - w) // 2
            draw_text(line, x, y_start)
            y_start += h
    else:
        mid = len(lines) // 2
        top_lines = lines[:mid]
        bottom_lines = lines[mid:]

        y_start = 10
        for line in top_lines:
            w, h = get_text_size(line)
            x = (width - w) // 2
            draw_text(line, x, y_start)
            y_start += h

        total_bottom_height = sum(get_text_size(line)[1] for line in bottom_lines)
        y_start = height - total_bottom_height - 10
        for line in bottom_lines:
            w, h = get_text_size(line)
            x = (width - w) // 2
            draw_text(line, x, y_start)
            y_start += h

    return img

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Ultimate AI Meme Generator", page_icon="😆", layout="centered")
st.title("😆 Ultimate AI Meme Generator")
st.write("Create memes automatically — image & caption powered by Gemini + Pollinations!")

# Input section
col1, col2 = st.columns([3,1])
with col1:
    topic = st.text_input("💬 Enter a topic (e.g. exams, coding, college life):")
with col2:
    if st.button("🎲 Surprise Me!"):
        topic = random.choice(["coding","exams","AI","college life","Mondays","gym","dating"])
        mood = random.choice(["funny","sarcastic","nerdy","dark","motivational"])
        st.session_state["topic"] = topic
        st.session_state["mood"] = mood
        st.success(f"✨ Surprise! Topic: **{topic}**, Mood: **{mood}**")

mood = st.selectbox("🎭 Select meme mood:", ["funny","sarcastic","nerdy","dark","motivational"])

if st.button("🖼️ Generate Meme"):
    if topic.strip():
        try:
            # Generate description & caption prompt
            caption_prompt, image_description = create_meme_prompt(topic, mood)
            
         
            caption = llm.invoke(caption_prompt).content.strip()
            
            # Generate image URL
            image_url = generate_image_from_description(image_description)
            
            # Fetch image safely
            response = requests.get(image_url)
            if response.status_code == 200 and response.content:
                try:
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                except Exception as e:
                    st.warning(f"⚠️ Could not open image from Pollinations. Error: {e}")
                    img = None
            else:
                st.warning(f"⚠️ Failed to fetch image. Status code: {response.status_code}")
                img = None

            if img:
                final_img = overlay_caption(img, caption)
                st.image(final_img, caption="Generated Meme", use_container_width=True)
                
                buf = BytesIO()
                final_img.save(buf, format="PNG")
                st.download_button("💾 Download Meme", data=buf.getvalue(), file_name=f"{topic}_meme.png", mime="image/png")
        except Exception as e:
            st.warning(f"⚠️ Could not generate meme. Error: {e}")
    else:
        st.warning("Please enter a topic to generate meme.")

st.markdown("---")
st.caption("Made by **Manas** • Powered by Gemini + Pollinations • 100% Free 🎨")
