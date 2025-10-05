import streamlit as st
import pandas as pd
import numpy as np
import joblib

class RainPredictor:
    def __init__(self):
        self.raw_df = self._load_raw_df()
        self.skip_features_state = {}
        self.input_features = {}

        self._init_mandatory_features()
        self._init_optional_features()

    def _load_raw_df(self):
        return pd.read_csv('data/weatherAUS.csv')

    def _init_mandatory_features(self):
        self.mandatory_features = ['Location']

    def _init_optional_features(self):
        self.skippable_features = [
            'Humidity9am', 'Humidity3pm', 'Evaporation', 'Rainfall',
            'WindGustDir', 'WindGustSpeed', 'WindDir9am', 'WindDir3pm', 'WindSpeed9am', 'WindSpeed3pm',
            'MinTemp', 'MaxTemp', 'Temp9am', 'Temp3pm', 'Sunshine',
            'Pressure9am', 'Pressure3pm', 'Cloud9am', 'Cloud3pm', 'RainToday'
        ]

    def render_predict_form(self):
        for feature in self.mandatory_features:
            self._render_feature_input(feature)
        
        for feature in self.skippable_features:
            self._render_feature_input(feature, optional=True)

        # st.write('You entered:')
        # st.json(self.input_features)
        self._render_predict_button()

    def _render_feature_input(self, feature, optional=False):
        if (optional):
            self.skip_features_state[feature] = st.checkbox(f'Skip {feature} value?')
        else:
            self.skip_features_state[feature] = False
            
        if self.raw_df[feature].dtype == 'object':  # categorical
            self._render_categorical_input(feature)
        elif self.raw_df[feature].dtype in ['int64', 'float64']:  # numeric
            self._render_numeric_input(feature)
        # st.divider()

    def _render_categorical_input(self, feature):
        if (self.skip_features_state[feature] == True):
            self.input_features[feature] = None
        else: 
            self.input_features[feature] = st.selectbox(f'Select {feature}', options=self.raw_df[feature].dropna().unique())

    def _render_numeric_input(self, feature):
        if (self.skip_features_state[feature]):
            self.input_features[feature] = None
        else:
            min_val = self.raw_df[feature].min()

            # ignore outliers values for some columns
            if (feature in ['Rainfall', 'Evaporation']):
                max_val = self.raw_df[feature].quantile(0.98)
            else:
                max_val = self.raw_df[feature].max()

            default_val = self.raw_df[feature].mean()
            
            self.input_features[feature] = st.slider(
                label=f'{feature}',
                min_value=float(min_val),
                max_value=float(max_val),
                value=float(default_val)
            )

    def _render_predict_button(self):
        if st.button('Predict Rain Tomorrow'):
            result = self._predict()
            st.markdown(
                f'Rain Tomorrow: {result["prediction"]}<br/>with probability {result["probability"]}%',
                unsafe_allow_html=True
            )

            conditions_markdown = 'Provided Conditions:<br/>'
            for feature in self.input_features:
                if (type(self.input_features[feature]) == float):
                    conditions_markdown += feature + ': ' + str(round(self.input_features[feature], 2)) + '<br/>'
                else:
                    conditions_markdown += feature + ': ' + str(self.input_features[feature]) + '<br/>'
                
            st.markdown(conditions_markdown, unsafe_allow_html=True)

    def _predict(self):   
        # load model and all nessesary data transformers
        model, imputer, scaler, encoder, input_cols, numeric_cols, categorical_cols = self._load_model_data()

        # sort input features as require for prediction and create data frame with one row of inputed data
        input_features_normalized_list = []

        for input_col in input_cols:
            input_features_normalized_list.append(self.input_features[input_col])

        input_features_np = np.expand_dims(np.array(input_features_normalized_list), axis=0)
        input_features_df = pd.DataFrame(input_features_np, columns=input_cols)

        # impute and scale numeric columns
        input_features_df[numeric_cols] = imputer.transform(input_features_df[numeric_cols])
        input_features_df[numeric_cols] = scaler.transform(input_features_df[numeric_cols])

        # encode categorical columns
        encoded_cols = list(encoder.get_feature_names_out(categorical_cols))
        input_features_df[encoded_cols] = encoder.transform(input_features_df[categorical_cols])

        # predict
        predict_input = input_features_df[numeric_cols + encoded_cols]
        predictions = model.predict(predict_input)
        probabilities = model.predict_proba(predict_input)

        return {
            'prediction': predictions[0],
            'probability': (max(probabilities[0]) * 100).round(2)
        }

    def _load_model_data(self):
        model_data = joblib.load('./models/rf_model.joblib')
        return (
            model_data['model'],
            model_data['imputer'],
            model_data['scaler'],
            model_data['encoder'],
            model_data['input_cols'],
            model_data['numeric_cols'],
            model_data['categorical_cols']
        )

