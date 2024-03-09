#import necessary packages
import google.generativeai as genai
import pathlib
import textwrap
import streamlit as st
import json
import elevenlabs
import os

from elevenlabs import generate, play, save
from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))



# Function to initialize session state
def initialize_session_state_gemini():
    return st.session_state.setdefault('gemini_api_key', None)

# Main Streamlit app
def text_page():
  st.title("DigA.I.")

    # Initialize session state
  initialize_session_state_gemini()  
  ELEVEN_LABS_API_KEY = st.session_state.setdefault('ELEVEN_LABS_API_KEY', None)

  # Configure API keys
  gemini_key = st.sidebar.text_input("Enter your Gemini key:", value=st.session_state.gemini_api_key, type='password')

    # Check if the API key is provided
  if not gemini_key:
    st.sidebar.error("Please enter your Gemini key.")
  else:
    # Store the API key in session state
    st.session_state.gemini_api_key = gemini_key

  genai.configure(api_key=gemini_key)

  # Configure elevenlabs keys
  elevenlabs_key = st.sidebar.text_input("Enter your Eleven Labs key:", value=st.session_state.ELEVEN_LABS_API_KEY, type='password')

    # Check if the API key is provided
  if not elevenlabs_key:
    st.sidebar.error("Please enter your API key.")
  else:
    # Store the API key in session state
    st.session_state.ELEVEN_LABS_API_KEY = elevenlabs_key

    os.environ["elevenlabs_API_TOKEN"] = elevenlabs_key
  

    
    # Set up the model configuration options
  temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.9, 0.1)
  top_p = st.sidebar.number_input("Top P", 0.0, 1.0, 1.0, 0.1)
  top_k = st.sidebar.number_input("Top K", 1, 100, 1)
  max_output_tokens = st.sidebar.number_input("Max Output Tokens", 1, 10000, 2048)

    # Set up the model
  generation_config = {
    "temperature": temperature,
    "top_p": top_p,
    "top_k": top_k,
    "max_output_tokens": max_output_tokens,
  }

  safety_settings = "{}"
  safety_settings = json.loads(safety_settings)
        
  prompt = st.text_input("Enter the question:")
  # Check if the query is provided
  if not prompt:
    st.stop()
  if not gemini_key:
    st.error("Please enter your API key.")
    st.stop()


  gemini = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
                

    
  theme_prompt= "is the question of my educational script of up to 5 parts. Each part must have a short Narration and a Prompt to generate an image about the event narrated. If you don't know about the subject, simply return 'i dont know'"
  prompt_parts = [theme_prompt] + [prompt] 
  
  response= ''
  model = genai.GenerativeModel('gemini-pro')
  if response:
    parts = response.parts
  else:
      st.error("No response was returned.")
    
  
  try:
    response = gemini.generate_content(prompt_parts)
    st.subheader("Gemini:")
    if response.text: 
        st.write(response.text)
    else:
      st.write("No output from Gemini.")
  except Exception as e:
    st.write(f"An error occurred: {str(e)}")
        
        
#Prompt spliting
  def split_prompts(text: str, part: str):
      narration = model.generate_content(f"Return only The Part {part} Narration (except for the word narration) with no modification, from the script:" + text)
      image = model.generate_content(f"I have an story and I want only the Image Prompt for the part {part} with, the story is:" + text)

      return {
          "narration": narration.text,
          "image": image.text
      }

  splited = split_prompts(response.text, 1)
  st.write(splited['narration'])


  audio = generate(
    api_key=ELEVEN_LABS_API_KEY,
    text=splited['narration'],
    voice="Rachel",
    model="eleven_multilingual_v2"
  )

  save(audio,'test.wav')
  
  st.audio(audio)

# Run the Streamlit app
if __name__ == "__main__":
    text_page()
