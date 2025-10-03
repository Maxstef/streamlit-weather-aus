import pandas as pd
import streamlit as st
import numpy as np

def get_weather_stats(show_all=True, features=['Humidity3pm', 'Pressure3pm', 'MinTemp', 'MaxTemp']):
    raw_df = pd.read_csv('data/weatherAUS.csv')
    raw_df.dropna(subset=['RainTomorrow'], inplace=True)

    # 1. Convert RainTomorrow to boolean
    raw_df['RainTomorrow_bool'] = (raw_df['RainTomorrow'] == 'Yes').astype(int)
    
    # 2. Percentage of RainTomorrow = Yes
    rain_percentage = raw_df.groupby('Location')['RainTomorrow_bool'].mean() * 100
    
    # 3. Compute averages of features split by RainTomorrow
    averages = (
        raw_df.groupby(['Location', 'RainTomorrow'])[features]
          .mean()
          .unstack()   # Creates separate Yes/No columns
    )
    
    # Rename columns for clarity
    averages.columns = [f"{col}_{val}" for col, val in averages.columns]
    
    # 4. Combine everything into one DataFrame
    result = pd.concat([rain_percentage, averages], axis=1).reset_index()
    
    # Rename RainTomorrow percentage column
    result.rename(columns={'RainTomorrow_bool': 'RainTomorrow_Yes_Percentage'}, inplace=True)
    
    # Round for readability
    result = result.round(2)

    if (not show_all):
        return result
    
    # Compute totals across all locations
    total_rain_percentage = raw_df['RainTomorrow_bool'].mean() * 100
    total_avgs = (
        raw_df.groupby('RainTomorrow')[features]
          .mean()
          .unstack()
    )
    
    # Flatten columns
    total_avgs.index = [f"{col}_{val}" for col, val in total_avgs.index]
    
    # Combine into single Series
    total_row = pd.concat([pd.Series({'Location': 'ALL',
                                      'RainTomorrow_Yes_Percentage': total_rain_percentage}),
                           total_avgs])
    
    # Append to result
    result_with_total = pd.concat([result, total_row.to_frame().T], ignore_index=True)
    
    # Round values
    result_with_total = result_with_total.round(2)
    
    return result_with_total


def get_st_column_config():
    return {
        "Location": st.column_config.TextColumn(
            "📍 Location",
            help="Weather station location in Australia",
            width="medium"
        ),
        "RainTomorrow_Yes_Percentage": st.column_config.ProgressColumn(
            "🌧️ Rain Tomorrow (%)",
            help="Percentage of days with rain tomorrow",
            min_value=0,
            max_value=100,
            format="%.2f"
        ),
        "Humidity3pm_Yes": st.column_config.NumberColumn(
            "💧 Humidity (Rainy)", format="%.1f"
        ),
        "Humidity3pm_No": st.column_config.NumberColumn(
            "💧 Humidity (Dry)", format="%.1f"
        ),
        "Pressure3pm_Yes": st.column_config.NumberColumn(
            "🌬️ Pressure (Rainy)", format="%.1f"
        ),
        "Pressure3pm_No": st.column_config.NumberColumn(
            "🌬️ Pressure (Dry)", format="%.1f"
        ),
        "MinTemp_Yes": st.column_config.NumberColumn(
            "🌡️ Min Temp (Rainy)", format="%.1f °C"
        ),
        "MinTemp_No": st.column_config.NumberColumn(
            "🌡️ Min Temp (Dry)", format="%.1f °C"
        ),
        "MaxTemp_Yes": st.column_config.NumberColumn(
            "🔥 Max Temp (Rainy)", format="%.1f °C"
        ),
        "MaxTemp_No": st.column_config.NumberColumn(
            "🔥 Max Temp (Dry)", format="%.1f °C"
        ),
    }
