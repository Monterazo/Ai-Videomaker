#import necessary packages
import google.generativeai as genai
import streamlit as st
import json
import os
import requests
import io

from PIL import Image
from openai import OpenAI 
from elevenlabs import generate, play, save
from IPython.display import display
from IPython.display import Markdown

def configure_api_key(api_name, session_key, placeholder_text):
  api_key = st.sidebar.text_input("", value=session_key, label_visibility='collapsed', type='password', placeholder=placeholder_text)

  if api_key:
    session_key = api_key
    if api_name == 'gemini':
      genai.configure(api_key=api_key)
    elif api_name == 'elevenlabs':
      os.environ["elevenlabs_API_TOKEN"] = api_key
    elif api_name == 'openai':
      os.environ["OPENAI_API_KEY"] = api_key
  return session_key

def get_prompt(inputChoice, process_image):
    if inputChoice == ":rainbow[Text]":
        prompt = st.text_input("Generate an educational video about:")
    elif inputChoice == "Camera":
        imageInput = st.camera_input("Take a picture")
        prompt = process_image(imageInput)
    elif inputChoice == "Image File :floppy_disk:":
        imageInput = st.file_uploader("Upload a file", type=["jpg", "png", "jpeg"],label_visibility='collapsed')
        prompt = process_image(imageInput)
    else:
      st.error("Please select an input option.")
      st.stop()
    
    return prompt

def process_image(imageInput):
  with st.spinner('Analyzing image...'):
    visionModel = genai.GenerativeModel('gemini-pro-vision')
    if imageInput is not None:
        imageInput = Image.open(imageInput)
        try:
          imageResult = visionModel.generate_content(["What is the main subject in the image?", imageInput])
          if imageResult:
            st.success('Image analyzed! 🎉')  
            st.write(imageResult.text)
            return imageResult.text
        except Exception as e:
          st.error(f"An error occurred: {str(e)}")
          st.stop()
    else:
        st.stop()
        
def generate_script(prompt, gemini_key, scenesAmount, imageStyle):    
    safety_settings = "{}"  
    safety_settings = json.loads(safety_settings)
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
        
        theme_prompt= "is the question of my educational script of" +str(scenesAmount) + "parts. Each part must have a short Narration and a Prompt to generate an image in the style" + str(imageStyle) + "about the event narrated."
        
        prompt_parts = [theme_prompt] + [prompt] 
        
        try:
            response = gemini.generate_content(prompt_parts)
            if response.text: 
                st.toast('Script generated!', icon='🎈')  
                return response.text
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

def split_prompts(text: str, part: str):
  model = genai.GenerativeModel('gemini-pro')
  narration = model.generate_content(f"Return only The Part {part} Narration (except for the word narration) with no modification, from the script:" + text)
  image = model.generate_content(f"I have an story and I want only the Image Prompt for the part {part} with, the story is:" + text)
  return {
    "narration": narration.text,
    "image": image.text
    }
      
def split_script(scenesAmount, response, split_prompts):
    splited_list = []
    with st.spinner('Spliting script...'):
        for i in range(scenesAmount):
            splited = split_prompts(response, i+1)
            splited_list.append(splited)
    return splited_list

def generate_audio(scenesAmount, splited_list, generate, ELEVEN_LABS_API_KEY):
  if st.session_state.OPENAI_API_KEY is None:
    st.error("ElevenLabs API key is not set. Please enter the token in the sidebar.")
    st.stop()
  else:
    audio_list = []
    with st.spinner('Generating audio files...'):
        for i in range(scenesAmount):
            audio_data = generate(
                api_key=ELEVEN_LABS_API_KEY,
                text=splited_list[i]['narration'],
                voice="Rachel",
                model="eleven_multilingual_v2"
            )
            audio_list.append(audio_data)
    return audio_list

def generate_images(scenesAmount, splited_list):
    if st.session_state.OPENAI_API_KEY is None:
          st.error("OpenAI API key is not set. Please enter the token in the sidebar.")
          st.stop()
    else:
      image_response_list = []
      client = OpenAI()
      with st.spinner('Generating image files...'):
          for i in range(scenesAmount):
              imageresponse = client.images.generate(
                  model="dall-e-3",
                  prompt=splited_list[i]['image'],
                  size="1024x1024",
                  quality="standard",
                  n=1,
              )  
              image_data = requests.get(imageresponse.data[0].url).content
              image_response_list.append(image_data)
      return image_response_list


# Function to initialize session state
def initialize_session_state_gemini():
    return st.session_state.setdefault('gemini_api_key', None)

# Main Streamlit app
def text_page():
  st.title("Tale Genius")
  
  # Style Selector
  st.sidebar.subheader("Image Style")
  imageStyle = st.sidebar.selectbox(
    'What image style is your favourite?',
    ('Pixar', 'Realistic', 'Watercolor','Pointillism', 'Cartoon'), label_visibility='collapsed')
    
  # Scenes amount selector
  st.sidebar.subheader("Amount of Scenes")
  scenesAmount = st.sidebar.slider('How many scenes do you want?', 1, 8, 3, label_visibility='collapsed')
  


  # Input Choice
  st.sidebar.subheader("Input Option")
  inputChoice = st.sidebar.radio(
     "What's your input option",
     [":rainbow[Text]", "Camera", "Image File :floppy_disk:"],
     label_visibility='collapsed')

  # Configure API keys
  initialize_session_state_gemini()  
  ELEVEN_LABS_API_KEY = st.session_state.setdefault('ELEVEN_LABS_API_KEY', None)
  OPENAI_API_KEY = st.session_state.setdefault('OPENAI_API_KEY', None)
  st.sidebar.subheader("API Tokens")
  st.session_state.gemini_api_key = configure_api_key('gemini', st.session_state.gemini_api_key, 'Enter Gemini Key')
  st.session_state.ELEVEN_LABS_API_KEY = configure_api_key('elevenlabs', st.session_state.ELEVEN_LABS_API_KEY, 'Enter ElevenLabs Key')
  gemini_key = st.session_state.gemini_api_key
  st.session_state.OPENAI_API_KEY = configure_api_key('openai', st.session_state.OPENAI_API_KEY, 'Enter Openai Key')

  #Main program

  prompt = get_prompt(inputChoice, process_image)

  response = generate_script(prompt, gemini_key, scenesAmount, imageStyle)

  splited_list = split_script(scenesAmount, response, split_prompts)

  audio_list = generate_audio(scenesAmount, splited_list, generate, ELEVEN_LABS_API_KEY)

  image_response_list = generate_images(scenesAmount, splited_list)


  
  for i in range(scenesAmount):
    st.image(image_response_list[i], caption='Image number'+str(i+1))
    
  st.subheader("Your video:")
    
  st.balloons()
  st.toast('Your video is ready!', icon='🎈')
  
  with st.expander("Output history"):
    st.write("Prompt: OLD")
    st.video("https://www.youtube.com/watch?v=6ZfuNTqbHE8")

# Run the Streamlit app
if __name__ == "__main__":
    text_page()
