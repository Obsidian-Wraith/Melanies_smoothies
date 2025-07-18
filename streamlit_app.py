import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
import time

# Title and description
st.title(":cup_with_straw: Customize your smoothie!")
name_on_order = st.text_input("Name of Smoothie")
st.write("The name on your order is ", name_on_order)

# Hardcoded Snowflake connection details (for testing only)
snowflake_secrets = {
    "account": "ARFPAGZ-XLB69922",
    "user": "OBSIDIAN",
    "password": "Starlordsanthosh007",  # Be cautious with hardcoding passwords
    "role": "SYSADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "PUBLIC",
    "client_session_keep_alive": True  # Make this a boolean
}

# Attempt to create a Snowflake session
try:
    session = Session.builder.configs(snowflake_secrets).create()

    # Fetch fruit options from Snowflake
    all_fruits = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()['FRUIT_NAME'].tolist()

    # Multi-select for ingredients
    ingredients_list = st.multiselect('Choose up to 5 ingredients:', all_fruits)

    # Limit to 5 ingredients with warning
    if len(ingredients_list) > 5:
        st.warning("You can only select a maximum of 5 ingredients.")
        ingredients_list = ingredients_list[:5]

    # Display selected ingredients and order submission
    if ingredients_list:
        ingredients_string = ', '.join(ingredients_list)
        st.write("Ingredients you chose: ", ingredients_string)

        if st.button('Submit Order'):
            # Prepare SQL insert statement
            my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
            """
            try:
                # Execute the insert statement
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered! Thank you, Melly!', icon="✅")
            except Exception as e:
                # Capture and display any errors that occur during insertion
                st.error(f"Error occurred while placing the order: {e}")

except Exception as e:
    # Handle connection errors
    st.error(f"Failed to connect to Snowflake: {e}")

finally:
    # Close the session if it was created
    if 'session' in locals():
        session.close()

# Fetch data from API with retry logic
url = "https://my.smoothiefroot.com/api/fruit/watermelon"
max_retries = 3
retry_delay = 2  # seconds

for attempt in range(max_retries):
    try:
        smoothiefroot_response = requests.get(url, timeout=10)
        # Check response status code
        if smoothiefroot_response.status_code == 200:
            # Attempt to parse the response as JSON
            data = smoothiefroot_response.json()
            st.text(data)  # Display the JSON data
            break  # Exit the loop if successful
        else:
            st.error(f"Error fetching data from API: {smoothiefroot_response.status_code}, {smoothiefroot_response.text}")
            break  # Exit on non-retryable error

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}. Attempt {attempt + 1} of {max_retries}.")
        time.sleep(retry_delay)  # Wait before retrying
