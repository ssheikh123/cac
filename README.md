# Instructions for Foodie

Thank you for checking us out!

How to access Foodie:

1. Download all the necessary files
   - calorie_log.txt
   - saved_recipes.txt
   - style.css
   - website4.py

2. Put them all into the same folder, then into your preferred Python IDE (We used Visual Studio Code).

3. This step is important: once in the website4.py file, ctrl+f "auth_key"
   - Replace the following lines with the respective API keys:
     - Replace st.secrets["auth_key"] with your Firebase API key
     - Replace st.secrets["auth_key2"] with your OpenAI API key
Unfortunately, due to privacy reasons, we cannot share our api keys with the public, so you need your own before accessing. Firebase's is free; OpenAI's is relatively cheap.

4. Before running, make sure to install all the dependencies. All of them are in the requirements.txt file, but will be listed below for your convenience:
   - Check what package management system (e.g. pip, conda, npm) your system (Windows, MacOS, Linux) uses to install the following:
     - matplotlib
     - numpy
     - opencv-python-headless
     - Pillow
     - Pyrebase4 (or Pyrebase)
     - requests
     - streamlit
     - streamlit-extras
     - setuptools

Once all of these steps have been successfully followed, run one of the following commands in your terminal to run Foodie:
  - python -m streamlit run website4.py
  - streamlit run website4.py

Thank you for taking the time to read this! Remember to stay Foodie!
