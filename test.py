#import necessary packages
import google.generativeai as genai
import streamlit as st
import json
import os
import requests
import io

from tempfile import NamedTemporaryFile

from pathlib import Path
from PIL import Image
from openai import OpenAI 
from elevenlabs import generate, play, save
from IPython.display import display
from IPython.display import Markdown
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def save_uploaded_file(uploaded_file):
    try:
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as f:
            f.write(uploaded_file.getvalue())
            return f.name
    except Exception as e:
        print(e)
        return None

def create_video(image_input, audio_input):
    # Carregar o arquivo de áudio
    audio_clip = AudioFileClip(audio_input)

    # Carregar a imagem e definir a duração para a duração do áudio
    img_clip = ImageClip(image_input).set_duration(audio_clip.duration)

    # Definir o áudio da imagem para o áudio carregado
    final_clip = img_clip.set_audio(audio_clip)

    # Criar um arquivo temporário para salvar o vídeo
    with NamedTemporaryFile(delete=False, suffix=".mp4") as f:
        temp_filename = f.name  

    # Escrever o resultado para o arquivo temporário
    final_clip.write_videofile(temp_filename, codec='libx264', fps=24)

    # Ler o arquivo temporário em um objeto BytesIO
    with open(temp_filename, "rb") as f:
        video_io = io.BytesIO(f.read())

    # Remover o arquivo temporário
    os.remove(temp_filename)

    # Retornar o objeto BytesIO
    return video_io

#Teste pro ffmpeg
ffmpeg_path = r'C:\Users\lucas\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-6.1.1-essentials_build\bin'

# Add the FFmpeg path to the PATH environment variable
os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']


# Main Streamlit app
def text_page():
  st.title("Tale Genius")
  
  image_input = st.file_uploader("Upload a file", type=["jpg", "png", "jpeg"],label_visibility='collapsed')
  audio_input = st.file_uploader("Upload an audio file", type=["mp3", "wav"],label_visibility='collapsed')

  if image_input is not None and audio_input is not None:
    image_filename = save_uploaded_file(image_input)
    audio_filename = save_uploaded_file(audio_input)
    output_filename = create_video(image_filename, audio_filename)
    st.video(output_filename)
    
# Run the Streamlit app
if __name__ == "__main__":
    text_page()
