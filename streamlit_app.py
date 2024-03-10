#import necessary packages
import google.generativeai as genai
import textwrap
import streamlit as st
import json
import os
import requests
import time

from openai import OpenAI 
from elevenlabs import generate, play, save
from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def split_prompts(text: str, part: str):
  model = genai.GenerativeModel('gemini-pro')
  narration = model.generate_content(f"Return only The Part {part} Narration (except for the word narration) with no modification, from the script:" + text)
  image = model.generate_content(f"I have an story and I want only the Image Prompt for the part {part} with, the story is:" + text)
  return {
    "narration": narration.text,
    "image": image.text
    }
      
# Function to initialize session state
def initialize_session_state_gemini():
    return st.session_state.setdefault('gemini_api_key', None)

# Main Streamlit app
def text_page():
  st.title("DigA.I.")

  # Initialize session state
  initialize_session_state_gemini()  
  ELEVEN_LABS_API_KEY = st.session_state.setdefault('ELEVEN_LABS_API_KEY', None)
  OPENAI_API_KEY = st.session_state.setdefault('OPENAI_API_KEY', None)

  # Configure API keys
  gemini_key = st.sidebar.text_input("",value=st.session_state.gemini_api_key,label_visibility='collapsed', type='password', placeholder='Enter your Gemini Key')

    # Check if the API key is provided
  if not gemini_key:
    st.sidebar.error("Please enter your Gemini key.")
  else:
    # Store the API key in session state
    st.session_state.gemini_api_key = gemini_key

  genai.configure(api_key=gemini_key)

  # Configure elevenlabs keys
  elevenlabs_key = st.sidebar.text_input("", value=st.session_state.ELEVEN_LABS_API_KEY,label_visibility='collapsed', type='password', placeholder='Enter your Eleven Labs Key')

    # Check if the API key is provided
  if not elevenlabs_key:
    st.sidebar.error("Please enter your API key.")
  else:
    # Store the API key in session state
    st.session_state.ELEVEN_LABS_API_KEY = elevenlabs_key

    os.environ["elevenlabs_API_TOKEN"] = elevenlabs_key

  # Configure Openai keys
  openai_key = st.sidebar.text_input("", value=st.session_state.OPENAI_API_KEY,label_visibility='collapsed', type='password', placeholder='Enter your Openai Key')

  # Check if the API key is provided
  if not openai_key:
    st.sidebar.error("Please enter your API key.")
  else:
    # Store the API key in session state
    st.session_state.OPENAI_API_KEY = openai_key

    os.environ["OPENAI_API_KEY"] = openai_key

  safety_settings = "{}"  
  safety_settings = json.loads(safety_settings)
        
  prompt = st.text_input("Enter the question:")
  # Check if the query is provided
  if not prompt:
    st.stop()
  if not gemini_key:
    st.error("Please enter your API key.")
    st.stop()
    
  #Script generation
  with st.spinner('Generating script...'):
    gemini = genai.GenerativeModel(model_name="gemini-pro",
                                  #generation_config=generation_config,
                                  safety_settings=safety_settings)
                  
      
    theme_prompt= "is the question of my educational script of 5 parts. Each part must have a short Narration and a Prompt to generate an image about the event narrated. If you don't know about the subject, simply return 'i dont know'"
    prompt_parts = [theme_prompt] + [prompt] 
    
    response= ''
    
    if response:
      parts = response.parts
    try:
      response = gemini.generate_content(prompt_parts)
      if response.text: 
          st.toast('Script generated!', icon='🎈')  
      else:
        st.write("No output from Gemini.")
    except Exception as e:
      st.write(f"An error occurred: {str(e)}")
         
  #Prompt spliting
  splited_list = []
  with st.spinner('Spliting script...'):
    for i in range(5):
      splited = split_prompts(response.text, i+1)
      splited_list.append(splited)
      #st.write('iteration' + str(i+1))
      #st.write(splited_list[i]['narration'])

  #Audio generation
  audio_list = []

  with st.spinner('Generating audio files...'):
    for i in range(2):
      audio = generate(
          api_key=ELEVEN_LABS_API_KEY,
          text=splited_list[i]['narration'],
          voice="Rachel",
          model="eleven_multilingual_v2"
      )
      audio_list.append(audio)

  
  #Image generation
  image_response_list = []

  #client = OpenAI()
  with st.spinner('Generating image files...'):
    for i in range(2):
      imageresponse = client.images.generate(
        model="dall-e-3",
        prompt=splited_list[i]['image'],
        size="1024x1024",
        quality="standard",
        n=1,
      )
    
    st.subheader("Your video:")
    
    image_data = requests.get(imageresponse.data[0].url).content
    st.image(image_data)
    st.toast('Your video is ready!', icon='🎈')
    



# Run the Streamlit app
if __name__ == "__main__":
    text_page()
