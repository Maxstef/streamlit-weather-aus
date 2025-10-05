import streamlit as st
from scripts.weather_stats import get_weather_stats, get_st_column_config
from scripts.predict_rain import RainPredictor

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(page_title="Weather in Australia Tomorrow", page_icon="🌦️")

# -------------------------------
# App title and introduction
# -------------------------------
st.title("🌦️ Weather in Australia Tomorrow")
st.markdown(
    """
    Welcome!  
    This simple app explores **rain prediction in Australia** using historical weather data.  
    Below you can find useful statistics by location, which may help explain the patterns behind rainy days.
    """
)
st.image("images/weather-aus.png", use_container_width=True)

# -------------------------------
# Statistical overview
# -------------------------------
st.header("📊 Rain Statistics by Location")
st.markdown(
    """
    The table below shows:
    - **Percentage of rainy days** for each location  
    - **Average humidity, pressure, and temperatures** split by whether it rained the next day or not  

    These features are often correlated with rainfall and can provide useful insights before making predictions.
    """
)

# Display dataframe
st.dataframe(
    get_weather_stats(),
    hide_index=True,
    column_config=get_st_column_config()
)

# -------------------------------
# Prediction
# -------------------------------
# Section title
st.header("Predict Rain Tomorrow")

# Description
st.markdown(
    """
Enter the weather conditions below and click the **Predict Rain** button.  

- Some values are optional — you can skip them.  
- You can provide all available details or only the ones you know.  
- The prediction works with any number of provided inputs, but **more details improve prediction accuracy**.
"""
)

# Render the prediction form
rain_predictor = RainPredictor()
rain_predictor.render_predict_form()
