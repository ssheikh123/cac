# IMPORTANT MESSAGE!!
# PLEASE MAKE SURE TO READ THE README.txt FILE BEFORE ANYTHING. IT CONTAINS INSTRUCTIONS WITH WHAT TO DO.

import json
import time
import streamlit as st
from PIL import Image
import cv2
from datetime import datetime
import numpy as np
import requests
import base64
import os
import matplotlib.pyplot as plt
import pyrebase
import calendar
from streamlit_extras.let_it_rain import rain








with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


def emojis():
    rain(
        emoji="😋",
        font_size=54,
        falling_speed=10,
        animation_length=3,
    )




# Configuration Key
firebaseConfig = {
    "apiKey": st.secrets["auth_key"],
    "authDomain": "cacapp-d3eaa.firebaseapp.com",
    "databaseURL": "https://cacapp-d3eaa-default-rtdb.firebaseio.com",
    "projectId": "cacapp-d3eaa",
    "storageBucket": "cacapp-d3eaa.appspot.com",
    "messagingSenderId": "624131578751",
    "appId": "1:624131578751:web:ddc6ddad4858594d06184a",
    "measurementId": "G-N69EC4ZN70"
}




# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()




if 'daily_schedule' not in st.session_state:
    st.session_state.daily_schedule = []




# Database
db = firebase.database()
storage = firebase.storage()
st.sidebar.image("https://i.imgur.com/QagqWUy.png", width=150)




is_logged_in = False




# Authentication
#choice = st.sidebar.selectbox('Login/Signup', ['Login', 'Sign up'])








# Function to set a value in Firebase instead of session state
def set_firebase_state(user_id, key, value):
    db.child(user_id).child("app_state").child(key).set(value)




# Function to get a value from Firebase
def get_firebase_state(user_id, key, default_value=None):
    result = db.child(user_id).child("app_state").child(key).get().val()
    return result if result else default_value




success_placeholder = st.empty()




if not is_logged_in:
    # Show the login/signup form inside an expander
    with st.sidebar.expander("Login/Signup", expanded=True):
        choice = st.selectbox('', ['Login', 'Sign up'])


        # Obtain User Input for email and password
        email = st.text_input('Email address')
        password = st.text_input('Password', type='password')


        if choice == 'Sign up':
            handle = st.text_input('Username', value='Default')
            submit = st.button('Create my account!')


            if submit:
                try:
                    user = auth.create_user_with_email_and_password(email, password)
                    user_id = user['localId']
                    db.child("user_handles").child(user_id).set(handle)
                    st.success("Account created successfully!")
                    st.balloons()
                    emojis()
                except Exception as e:
                    st.error(f"Error: {str(e)}")


        if choice == 'Login':
            login = st.checkbox('Login')
            if login:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    user_id = user['localId']
                    user_token = user['idToken']
                    is_logged_in = True  # Set the login status to True
                    st.sidebar.success("Logged in successfully!")
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
else:
    # Sidebar buttons for the different pages
    if st.sidebar.button("Dashboard"):
        switch_page("Dashboard")
    if st.sidebar.button("Diary"):
        switch_page("Diary")
    if st.sidebar.button("Camera"):
        switch_page("Camera")
    if st.sidebar.button("Recipes"):
        switch_page("Recipes")
    if st.sidebar.button("Profile"):
        switch_page("Profile")




content_placeholder = st.empty()




# Function to handle page navigation and clearing content
def switch_page(new_page):
    st.session_state.page = new_page
    content_placeholder.empty()  # Clear any previous content




if is_logged_in:
    # Display all tabs only if the user is logged in
    st.sidebar.write("Logged in successfully!")
    if st.sidebar.button("Dashboard"):
        switch_page("Dashboard")
    if st.sidebar.button("Diary"):
        switch_page("Diary")
    if st.sidebar.button("Camera"):
        switch_page("Camera")
    if st.sidebar.button("Recipes"):
        switch_page("Recipes")
    if st.sidebar.button("Profile"):
        switch_page("Profile")
else:
    # If not logged in, restrict access to Profile only
    st.sidebar.write("Please log in before accessing other pages.")
    st.sidebar.button("Profile")
    st.session_state.page = "Profile"




# OpenAI API Key
api_key = st.secrets["auth_key2"]




if "page" not in st.session_state:
    st.session_state.page = "Profile"  # Set the default page
if "image_analyzed" not in st.session_state:
    st.session_state["image_analyzed"] = False




    #FOR SAVING RECIPES:
# Define the file path for saving recipes
RECIPE_FILE = "saved_recipes.txt"




# Ensure the file exists or create it if it doesn't
def initialize_recipe_file():
    if not os.path.exists(RECIPE_FILE):
        with open(RECIPE_FILE, "w") as f:
            json.dump({}, f)  # Initialize with an empty dictionary




# Function to load saved recipes from the text file
def load_saved_recipes():
    initialize_recipe_file()  # Ensure file exists
    with open(RECIPE_FILE, "r") as f:
        saved_recipes = json.load(f)
        st.session_state["saved_recipes"] = saved_recipes




# Function to save the current state of recipes to the text file
def save_recipe_to_file():
    with open(RECIPE_FILE, "w") as f:
        json.dump(st.session_state["saved_recipes"], f)




# Function to add a new recipe to the saved list
def save_recipe(api_response):
    # Ensure saved recipes state exists
    if "saved_recipes" not in st.session_state:
        st.session_state["saved_recipes"] = {}
   
    # Get the current count of saved recipes
    recipe_count = len(st.session_state["saved_recipes"]) + 1
    # Add new recipe to the dictionary with a numeric key
    st.session_state["saved_recipes"][str(recipe_count)] = api_response
    # Save updated recipes to file
    save_recipe_to_file()




# Function to display saved recipes as a dropdown
def display_saved_recipes():
    if st.session_state["saved_recipes"]:
        for key, recipe in st.session_state["saved_recipes"].items():
            with st.expander(f":gray[Recipe {key}]"):
                st.write(":gray[{recipe}]")
    else:
        st.write(":gray[No saved recipes found.]")




# Initialize session state for tracking saved recipes
if "saved_recipes" not in st.session_state:
    load_saved_recipes()  # Load recipes if they aren't already in session state




def calculate_bmr(age, height, weight, gender, activity_level):
    if gender == "Male":
        # BMR calculation for men
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        # BMR calculation for women
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
   
    # Adjust BMR based on activity level
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly active": 1.375,
        "Moderately active": 1.55,
        "Very active": 1.725,
        "Super active": 1.9
    }




    return bmr * activity_multipliers.get(activity_level, 1.2)  # Default to Sedentary if activity level is not found




def calculate_protein(weight):
    return weight * 0.85  # Return protein in grams




# Function to send food item to GPT and return nutrition info
def send_food_to_gpt(food_item):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"Here is a food: {food_item}. Return only a string of comma-separated values based on an approximate serving size estimate. DO NOT INCLUDE UNITS. Avoid special characters. Format: Food item, calories, sugar, fat, protein, carbohydrates, vitamin D, calcium, iron, potassium."
            }
        ],
        "max_tokens": 150
    }




    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }




    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)




    if response.status_code == 200:
        response_data = response.json()
        api_content = response_data['choices'][0]['message']['content']
        # Log the raw API response to check its format
        # st.write(f"API Response for {food_item}: {api_content}")
        return api_content
    else:
        st.markdown(f"""
            <div style="color: black; background-color: #f5b227; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                <strong>Failed to get response from GPT: {response.status_code}</strong>
            </div>
        """, unsafe_allow_html=True)
        return None




# Function to log to file and update totals
def log_to_file_and_update_totals(api_response):
   
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"nutrition_log_{today}.txt"




    # Initialize daily totals in session state if not present
    if "daily_totals" not in st.session_state:
        st.session_state["daily_totals"] = {
            'calories': 0, 'sugar': 0, 'fat': 0, 'protein': 0,
            'carbohydrates': 0, 'vitamin_d': 0, 'calcium': 0,
            'iron': 0, 'potassium': 0
        }




    totals = st.session_state["daily_totals"]




    # Clear previous API response to avoid duplicate logging
    food_items = [item for item in api_response.split('\n') if item.strip()]




    # Open the file in append mode and log each food item
    with open(filename, 'a') as file:
        for item in food_items:
            file.write(item + "\n")  # Log the item in the file




            parts = item.split(',')
            if len(parts) >= 10:  # Ensure there are enough parts in the item
                try:
                    # Parse and update each nutritional value, stripping units where necessary
                    calories = int(parts[1].strip())  # Calories is already a number
                    totals['calories'] += calories




                    sugar = float(parts[2].strip('g'))  # Remove 'g' from the sugar value
                    totals['sugar'] += sugar




                    fat = float(parts[3].strip('g'))  # Remove 'g' from the fat value
                    totals['fat'] += fat




                    protein = float(parts[4].strip('g'))  # Remove 'g' from the protein value
                    totals['protein'] += protein




                    carbohydrates = float(parts[5].strip('g'))  # Remove 'g' from the carbs value
                    totals['carbohydrates'] += carbohydrates




                    # Check for optional nutritional values, stripping units where necessary
                    vitamin_d = float(parts[6].strip('IU')) if len(parts) > 6 else 0
                    totals['vitamin_d'] += vitamin_d




                    calcium = float(parts[7].strip('mg')) if len(parts) > 7 else 0
                    totals['calcium'] += calcium




                    iron = float(parts[8].strip('mg')) if len(parts) > 8 else 0
                    totals['iron'] += iron




                    potassium = float(parts[9].strip('mg')) if len(parts) > 9 else 0
                    totals['potassium'] += potassium




                    # Append the food item and its macros to the daily schedule
                    for item_log in st.session_state.daily_schedule:
                        if item_log['food_item'] == parts[0].strip():
                            item_log['macros'] = f"""
                                <span style="color:gray;">
                                    Calories: {calories}, Sugar: {sugar}g, Fat: {fat}g, Protein: {protein}g, Carbs: {carbohydrates}g
                                 </span>
                             """
                            st.markdown(item_log['macros'], unsafe_allow_html=True)
                except ValueError as e:
                    log_message = f"Error parsing nutritional data from: {item}."




                    st.markdown(f"""
                    <div style="color: black; background-color: #f5b227; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                        <strong>Error: {log_message}</strong>
                    </div>
                    """, unsafe_allow_html=True)




            else:
                log_message = f"Incomplete data for item: {item}"




                st.markdown(f"""
                <div style="color: black; background-color: #d1ffbd; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                    <strong>{log_message}</strong>
                </div>
                """, unsafe_allow_html=True)




# Path to the calorie log file
calorie_file_path = "calorie_log.txt"




# Function to read the daily calorie data from the file
def read_calorie_log():
    if not os.path.exists(calorie_file_path):
        return {}
   
    calorie_data = {}
    with open(calorie_file_path, 'r') as f:
        for line in f.readlines():
            date, calories = line.strip().split(': ')
            calorie_data[date] = int(calories)
    return calorie_data




# Function to write daily calories at the end of the day
def write_calorie_log(date, calories):
    with open(calorie_file_path, 'a') as f:
        f.write(f"{date}: {calories}\n")




def update_daily_calories(calories):
    today = datetime.now().strftime('%Y-%m-%d')
    write_calorie_log(today, calories)




# Function to generate a calendar heatmap
# Function to generate a calendar heatmap
# Function to generate a calendar heatmap
def plot_calendar(calorie_data, calorie_goal):
     # Get current month and year
    today = datetime.today()
    year, month = today.year, today.month






    # Get month name
    month_name = calendar.month_name[month]
   
    # Generate the calendar for the current month
    cal = calendar.monthcalendar(year, month)






    # Prepare a figure and axis for the calendar plot
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#ffe6bfff')
    ax.set_title(f"{month_name} {year}", fontsize=20, pad=20)






    # Define color mapping based on deviation
    def get_color(calories, goal):
        if calories is None:
            return 'white'  # Default color if no data
       
        # Calculate the deviation as a fraction
        deviation = abs(calories - goal) / goal
       
        # Apply a non-linear scaling to make color change more intense
        deviation = min(deviation * 2, 1)
       
        # Use the RdYlGn colormap (reversed, so closer to the goal is green)
        color = plt.cm.RdYlGn(1 - deviation)  # 1 - deviation ensures that lower deviations are greener
        return color






    # Create the calendar plot
    for week_idx, week in enumerate(cal):
        for day_idx, day in enumerate(week):
            if day == 0:
                # Empty cell for days outside the current month
                color = 'white'
                text = ""
            else:
                # Format the date string
                date_str = f"{year}-{month:02d}-{day:02d}"
                # Fetch the calorie log for the day, if available
                calories = calorie_data.get(date_str)
                color = get_color(calories, calorie_goal)
                text = str(day)




            # Calculate the position of the box for the day
            x = day_idx
            y = -week_idx
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=color, edgecolor='black'))






            # Add the text (day number) in the middle of the box
            ax.text(x + 0.5, y - 0.5, text, ha='center', va='center', fontsize=12)








    # Set x and y limits to fit the calendar grid
    ax.set_xlim(0, 7)
    ax.set_ylim(-len(cal), 0)






    # Hide axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])






    # Display the calendar plot in Streamlit
    st.pyplot(fig)
       
def plot_donut_chart(calories_consumed, calorie_goal):
    remaining_calories = calorie_goal - calories_consumed




    # Data for the chart
    labels = [f'Consumed Calories\n({calories_consumed} kcal)',
              f'Remaining Calories\n({remaining_calories} kcal)']
    sizes = [calories_consumed, remaining_calories]
    colors = ['#f9ae36ff', '#555555']
    explode = (0.1, 0)  # only "explode" the first slice




    # Create the donut chart
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode, pctdistance=0.85)




    # Draw a circle at the center of the pie to make it a donut
    centre_circle = plt.Circle((0, 0), 0.50, fc='#ffe6bfff')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)




    fig.patch.set_facecolor('#ffe6bfff')
    # Adding title
    plt.title('Daily Calories Intake')




    # Display the chart
    st.pyplot(fig)








if "daily_totals" not in st.session_state:
    st.session_state["daily_totals"] = {
        'calories': 0, 'sugar': 0, 'fat': 0, 'protein': 0,
        'carbohydrates': 0, 'vitamin_d': 0, 'calcium': 0,
        'iron': 0, 'potassium': 0
    }




# Check which page to display
with content_placeholder.container():
    if st.session_state.page == "Dashboard":
            st.title("Nutrition Dashboard")




   
            # Display the calorie ring
            st.header("Your Caloric Intake Today")
            calorie_goal = st.session_state.get('calorie_goal', 2000)
            if not calorie_goal:
                # Fetch the calorie goal from Firebase if not in session
                profile = db.child(user_id).child("profile").get().val()
                if profile and "calorie_goal" in profile:
                    calorie_goal = profile["calorie_goal"]
                    st.session_state["calorie_goal"] = calorie_goal
            plot_donut_chart(st.session_state['daily_totals']['calories'], calorie_goal)




            # Daily Schedule Section
            st.header("Log Food")




            # Input to log food items and time
            food_item = st.text_input(":gray[Food Item]")
            time_consumed = st.time_input(":gray[Time Consumed]")
           


            if st.button("Log Food Item"):
                if food_item:
                    new_log = {'time': time_consumed.strftime("%H:%M"), 'food_item': food_item}
                   
                    # Append and sort by time
                    st.session_state.daily_schedule.append(new_log)
                    st.session_state.daily_schedule.sort(key=lambda x: x['time'])
                   
                    # Send food item to GPT for analysis
                    gpt_response = send_food_to_gpt(food_item)
                    if gpt_response:
                        # Log and update totals
                        log_to_file_and_update_totals(gpt_response)
                       
                        # Update the log message
                        log_message = "Logged: " + food_item + " at " + time_consumed.strftime('%H:%M')
                   
               


                       
                else:
                    # CSS to style the expander headers and content properly
                    st.markdown("""
                        <style>
                        /* Styling for the expander header */
                        .streamlit-expanderHeader {
                            background-color: #3399FF !important;  /* Set a visible background color */
                            color: white !important;               /* Ensure the text is white for contrast */
                            font-weight: bold;                     /* Make text bold */
                            padding: 10px;                         /* Add some padding */
                            border-radius: 5px;                    /* Add rounded corners */
                        }
                       
                        /* Styling for the expander content */
                        .streamlit-expanderContent {
                            background-color: #f0f8ff !important;  /* Light background color for content */
                            color: black !important;               /* Black text for readability */
                        }
                       
                        /* Additional styling to adjust spacing */
                        .streamlit-expander {
                            margin-bottom: 10px;                   /* Add space between expanders */
                        }
                        </style>
                        """, unsafe_allow_html=True)
               


            st.header("What I Ate Today:")
            st.write(":gray[(Click food item to expand nutritional information.)]")
            if st.session_state.daily_schedule:
                for item in st.session_state.daily_schedule:
                    food_name = item['food_item']
                    food_time = item['time']
                    macros = item.get('macros', '')  # Get macros if available




                    # Create an expander for each food item to show macros on click
                    with st.expander(f":gray[{food_name} at {food_time}]"):
                        if macros:
                            # Write the macros with proper styling
                            st.write(f'<p style="color: #3399FF;">{macros}</p>', unsafe_allow_html=True)
                        else:
                            st.write(":gray[No detailed macros available yet.]")
            else:
                st.write(":gray[No food items logged for today.]")




    # For the camera tab        
    elif st.session_state.page == "Camera":
            st.subheader(":gray[Take a picture of your food:]")
            # Initialize session state for capturing the photo and tracking totals
            if "photo_taken" not in st.session_state:
                st.session_state["photo_taken"] = False
            if "photo" not in st.session_state:
                st.session_state["photo"] = None
            if "take_photo_clicked" not in st.session_state:
                st.session_state["take_photo_clicked"] = False
            if "return_to_camera" not in st.session_state:
                st.session_state["return_to_camera"] = False
            if "api_response" not in st.session_state:
                st.session_state["api_response"] = None








            if "daily_totals" not in st.session_state:
                    st.session_state["daily_totals"] = {
                        'calories': 0, 'sugar': 0, 'fat': 0, 'protein': 0,
                        'carbohydrates': 0, 'vitamin_d': 0, 'calcium': 0,
                        'iron': 0, 'potassium': 0
                    }








            # Function to encode the image to base64
            def encode_image(image):
                _, buffer = cv2.imencode('.jpg', image)
                return base64.b64encode(buffer).decode('utf-8')








            # Function to open the camera and display the preview
            def live_camera_preview():
                cap = cv2.VideoCapture(0)
                frame_placeholder = st.empty()  # Placeholder for the video stream








                # Create the "Take Photo" button outside the loop
                take_photo_button = st.button("Take Photo")
           
                while True:
                    ret, frame = cap.read()
                    if not ret:




                        st.markdown("""
                        <div style="color: black; background-color: #f5b227; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                            <strong>Error: Could not get frame from the camera.</strong>
                        </div>
                        """, unsafe_allow_html=True)




                        break








                    # Convert the frame to RGB (OpenCV uses BGR)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)








                    # Display the frame in the placeholder
                    frame_placeholder.image(frame_rgb, channels="RGB")








                    if take_photo_button:
                        st.session_state["photo"] = frame_rgb  # Save the captured frame
                        st.session_state["photo_taken"] = True
                        st.session_state["return_to_camera"] = True
                        cap.release()
                        frame_placeholder.empty()  # Clear the live feed
                        break








            # Function to send the image to the OpenAI API for analysis
            def send_image_to_openai(image):
                base64_image = encode_image(image)








                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }








                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Here is a picture of food. Return only a string of comma separated values based on an approximate serving size estimate. If there are multiple food items, return multiple strings. follow this format: Food item (include brand if applicable) (string), calories (int), sugar, fat, protein, carbohydrates, vitamin D, calcium, iron, postassium. DO NOT INCLUDE UNITS, ONLY NUMBERS. If there is no observable food in the picture, respond with No food detected. Here is an example of a response: Yogurt, all its nutrition info \n Jelly Beans, all its nutrition info You should return nothing else besides these strings."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 300
                }








                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
           
                if response.status_code == 200:
                    response_data = response.json()
                    message_content = response_data['choices'][0]['message']['content']
                    return message_content
                else:




                    log_message = "Failed to get response from API: " + response.status_code
                   
                    st.markdown("""
                    <div style="color: black; background-color: #f5b227; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                        <strong>Error: """ + log_message + """</strong>
                    </div>
                    """, unsafe_allow_html=True)




                    return None




            if "photo_saved" not in st.session_state:
                st.session_state["photo_saved"] = False




               
            # Start the live camera preview if no photo is taken
            if not st.session_state["photo_taken"]:
                live_camera_preview()








            # If a photo was taken, display and save it
            if st.session_state["photo_taken"] and not st.session_state["photo_saved"]:
                st.image(st.session_state["photo"], caption="")








                # Save the image with a timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                file_name = f'photo_{timestamp}.png'
           
                cv2.imwrite(file_name, cv2.cvtColor(st.session_state["photo"], cv2.COLOR_RGB2BGR))




                log_message = "Photo saved as " + file_name




                st.markdown("""
                    <div style="color: black; background-color: #d1ffbd; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                        <strong>""" + log_message + """</strong>
                    </div>
                    """, unsafe_allow_html=True)




                # Send the image to the OpenAI API and display the response
                if st.button("Analyze Image"):
                    st.write(":gray[API Response:]")
                    st.session_state["api_response"] = send_image_to_openai(st.session_state["photo"])
                    if st.session_state["api_response"]:
                        st.write(f":gray[{st.session_state.api_response}]")




                        log_to_file_and_update_totals(st.session_state["api_response"])




                        st.session_state["photo_saved"] = True




                if st.session_state["return_to_camera"]:
                    if st.button("Return to Camera"):
                        st.session_state["photo_taken"] = False
                        st.session_state["photo"] = None
                        st.session_state["take_photo_clicked"] = False
                        st.session_state["return_to_camera"] = False
                        st.session_state["api_response"] = None
                        st.session_state["photo_saved"] = False
                        st.cache_data.clear()
                        st.rerun()




    elif st.session_state.page == "Diary":
            st.title("Diary")


            st.markdown("""
            <div style="display: flex; align-items: center;">
                <span style="color: black;">The closer to green the color is, the closer you met your goal.</span>
            </div>
            """, unsafe_allow_html=True)


            # Load calorie log data
            calorie_data = read_calorie_log()
       
            # Assume the calorie goal is retrieved from user profile or session state
            calorie_goal = st.session_state.get("calorie_goal", 2000)


            st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <span style="color: black;">Here is the calorie goal you set: {calorie_goal} </span>
            </div>
            """, unsafe_allow_html=True)


            # Plot the calendar with the color-coded days
            plot_calendar(calorie_data, calorie_goal)








    elif st.session_state.page == "Recipes":
        st.title("Recipes Page")
            # User selects the type of meal and flavor
        meal_type = st.selectbox(":gray[Select Meal Type:]", ["Anything", "Snack", "Breakfast", "Lunch", "Dinner"])
        flavor_type = st.selectbox(":gray[Select Flavor Type:]", ["Anything", "Sweet", "Savory", "Spicy"])








        st.subheader(":gray[Take a picture of your ingredients or inside your fridge:]")








        # Initialize session state for capturing the photo
        if "photo_taken" not in st.session_state:
            st.session_state["photo_taken"] = False
        if "photo" not in st.session_state:
            st.session_state["photo"] = None




        # Function to encode the image to base64
        def encode_image(image):
            _, buffer = cv2.imencode('.jpg', image)
            return base64.b64encode(buffer).decode('utf-8')








        # Function to open the camera and display the preview
        def live_camera_preview():
            cap = cv2.VideoCapture(0)
            frame_placeholder = st.empty()  # Placeholder for the video stream
            take_photo_button = st.button("Take Photo")  # Create the "Take Photo" button








            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("Could not get frame from the camera.")
                    break








                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB")








                if take_photo_button:
                    st.session_state["photo"] = frame_rgb  # Save the captured frame
                    st.session_state["photo_taken"] = True
                    cap.release()
                    frame_placeholder.empty()  # Clear the live feed
                    break








        # Function to send the image and user inputs to OpenAI for meal suggestions
        def send_image_to_openai(image, meal_type, flavor_type):
            base64_image = encode_image(image)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            prompt = (f"Here is a picture of ingredients. Suggest a meal for {meal_type} with a {flavor_type} flavor. "
                    "Output the response in this format:\n"
                    ":gray[Meal Name: [name]]\n\n"
                    ":gray[Ingredients:]\n- [ingredient1]\n- [ingredient2]\n...\n"
                    ":gray[Instructions:]\n1. [instruction1]\n2. [instruction2]\n...\n"
                    "Do not include anything else.")
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": f"data:image/jpeg;base64,{base64_image}"}
                ],
                "max_tokens": 500
            }








            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['choices'][0]['message']['content']
            else:
                st.error(f"Failed to get response from API: {response.status_code}")
                return None








        # Display the camera preview if no photo is taken
        if not st.session_state["photo_taken"]:
            live_camera_preview()








        # If a photo was taken, display and save it
        if st.session_state["photo_taken"]:
            st.image(st.session_state["photo"], caption="Captured Ingredients")








            # Send the image and selections to OpenAI when "Get Recipe" is clicked
            if st.button("Get Recipe"):
                api_response = send_image_to_openai(st.session_state["photo"], meal_type, flavor_type)
                if api_response:
                    # Display the suggested meal
                    st.write("### Suggested Meal")
                    st.write(api_response)  # Display the entire output from the API








                    # Save the recipe to the text file
                    if st.button("Save Recipe"):
                        save_recipe(api_response)








        # Display saved recipes dropdown
        st.write("### Saved Recipes")
        display_saved_recipes()




           
    elif st.session_state.page == "Profile":
            st.warning(":gray[For best experience, ensure dark mode is on. (On top bar > click ⋮ > Settings > Choose app theme, colors and fonts > Dark mode)]", icon="⚠️")
            st.title("Profile Page")
            if "handle" in st.session_state:
                st.subheader(f"Welcome, {st.session_state['handle']}!")
            else:
                st.subheader("Welcome!")




            st.write(":gray[Set your personal details here.]")




            # Input for age, height, weight, and gender
            age = st.number_input(":gray[Age]", min_value=1, max_value=120, value=25)
            height = st.number_input(":gray[Height (in cm)]", min_value=50, max_value=250, value=170)
            weight = st.number_input(":gray[Weight (in kg)]", min_value=20, max_value=300, value=70)
            gender = st.selectbox(":gray[Sex]", ["Male", "Female"])
            activity_level = st.selectbox(":gray[Activity Level]", ["Sedentary", "Lightly active", "Moderately active", "Very active", "Super active"])




            if age > 0 and height > 0 and weight > 0 and gender and activity_level:
                calorie_goal = round(calculate_bmr(age, height, weight, gender, activity_level))
                st.write(f":gray[Your daily calorie goal is: {calorie_goal} calories]")




            # Save Profile button
            if st.button("Save Profile"):
                try:
                    user_id = user['localId']  # Get user ID
                    # st.write(f":blue[{user_id}]")




                    # Update profile information in Firebase (replacing old data)
                    profile_data = {
                        "age": age,
                        "height": height,
                        "weight": weight,
                        "gender": gender,
                        "activity_level": activity_level,
                        "calorie_goal": calorie_goal
                    }




                    # Log the data being sent
                    # st.write(":blue[Profile data being sent to Firebase:]", profile_data)
                   
                    # Send data to Firebase
                    result = db.child(user_id).child("profile").set(profile_data)




                    # Log the result from Firebase
                    # st.write("Firebase response:", result)




                    # Store profile data in session state for local use
                    st.session_state["age"] = age
                    st.session_state["height"] = height
                    st.session_state["weight"] = weight
                    st.session_state["gender"] = gender
                    st.session_state["activity_level"] = activity_level
                    st.session_state["calorie_goal"] = calorie_goal




                    st.markdown("""
                    <div style="color: black; background-color: #d1ffbd; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                    <strong>Profile saved successfully!</strong>
                    </div>
                    """, unsafe_allow_html=True)




                except Exception as e:
                    st.markdown(f"""
                    <div style="color: black; background-color: #f5b227; padding: 10px; border: 1px solid #ffeeba; border-radius: 5px;">
                        <strong>Make sure to log in first!</strong>
                    </div>
                    """, unsafe_allow_html=True)



