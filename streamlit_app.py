# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Title and description
st.title(":cup_with_straw: Customize your smoothie!")
name_on_order = st.text_input("Name of Smoothie")
st.write("The name on your order is ", name_on_order)

# Fetch Snowflake connection details from secrets
snowflake_secrets = st.secrets["snowflake"]

# Check if the secrets are properly set by displaying (for debug purposes)
# Remove this in production code for security
st.write(snowflake_secrets)

# Attempt to create a Snowflake session
try:
    session = Session.builder.configs({
        "account": snowflake_secrets["account"],
        "user": snowflake_secrets["user"],
        "password": snowflake_secrets["password"],
        "role": snowflake_secrets["role"],
        "warehouse": snowflake_secrets["warehouse"],
        "database": snowflake_secrets["database"],
        "schema": snowflake_secrets["schema"],
        "client_session_keep_alive": snowflake_secrets.get("client_session_keep_alive", True)  # Default to True if not set
    }).create()

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
                st.error(f"Error occurred: {e}")

except Exception as e:
    # Handle connection errors
    st.error(f"Failed to connect to Snowflake: {e}")

finally:
    # Close the session if it was created
    if 'session' in locals():
        session.close()
