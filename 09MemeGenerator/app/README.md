
# 😆 Ultimate AI Meme Generator

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/) 
[![Streamlit](https://img.shields.io/badge/Streamlit-App-green)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Generate memes automatically with **AI-powered images and captions**! This app uses **Google Gemini** via LangChain for generating captions and image descriptions, and **Pollinations** for AI-generated meme images.

---

## 🎯 Features

- AI-generated meme images & captions
- Smart overlay of captions on image (top, bottom, or both)
- Random topic generator for inspiration
- Download meme as PNG
- Optional screen recording using built-in laptop tools
- Dynamic font sizing & classic meme styling

---

## 🖼 Example Memes

![Example Meme 1](https://via.placeholder.com/400x300.png?text=Example+Meme+1)  
![Example Meme 2](https://via.placeholder.com/400x300.png?text=Example+Meme+2)

---

## ⚙️ How It Works
## 🎬 (Demo)

[![Watch Demo](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)

1. Enter a topic (e.g., exams, coding, coffee) or click **Surprise Me**  
2. Select a mood (funny, sarcastic, dark, nerdy, motivational)  
3. Click **Generate Meme**  
   - **Gemini** generates:
     - Short, funny **image description**
     - **Meme caption**
   - **Pollinations** generates the meme image  
   - Caption is automatically overlaid in classic meme style  


---

## 💻 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ultimate-ai-meme-generator.git
cd ultimate-ai-meme-generator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Replace your **Google API Key** in the script:

```python
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
```

4. Run the app:

```bash
streamlit run app.py
```

---

## 🛠 Built With

- [Streamlit](https://streamlit.io/) – Web app framework  
- [Pillow](https://pillow.readthedocs.io/) – Image processing  
- [LangChain Google GenAI](https://www.langchain.com/docs/) – Gemini integration  
- [Pollinations](https://image.pollinations.ai/) – AI image generation  

---

## 📄 License

MIT License © 2025 Manas  
See the [LICENSE](LICENSE) file for details.

---

## 🎉 Usage Tips

- Use **Surprise Me** for random topics  
- Longer captions may appear **top & bottom automatically**  

