import pickle
import pandas as pd
import numpy as np
#load the stacking model

file_path = './model/stacking_pipeline.pkl'


try:
    # Open and load the pickle file
    with open(file_path, 'rb') as file:
        loaded_data = pickle.load(file)
except FileNotFoundError:
    print(f"File '{file_path}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")

def make_prediction(features:pd.DataFrame):
    '''
    Predict car price given feature
    '''
    bin_features = ['apple_carplay', 'backup_camera_assist', 'bluetooth', 'heated_seats',
                'hill_assist_system', 'keyless_entry', 'keyless_ignition', 'multimedia_telematics', 'premium_sound_system',
                'satellite_radio', 'sunroof_moonroof', 'leather_seats', 'power_seats', 'traction_control',
                'driver_assistance_confidence_pkg', 'head-up_display', 'lane_departure_warning', 'navigation_system',
                'remote_start', 'blind_spot_monitor', 'lane_assist', 'parking_assist_system', 'stability_control', 
                'adaptive_cruise_control', 'alloy_wheels', 'cooled_seats', 'full_self-driving_capability',
                'third_row_seating', 'tow_hitch_package', 'rear_seat_entertainment']
    
    cols = ['type', 'make', 'year', 'model', 'miles_driven', 'doors', 'engine',
       'transmission', 'drive_type', 'fuel', 'apple_carplay',
       'backup_camera_assist', 'bluetooth', 'heated_seats',
       'hill_assist_system', 'keyless_entry', 'keyless_ignition',
       'multimedia_telematics', 'premium_sound_system', 'satellite_radio',
       'sunroof_moonroof', 'leather_seats', 'power_seats', 'traction_control',
       'driver_assistance_confidence_pkg', 'head-up_display',
       'lane_departure_warning', 'navigation_system', 'remote_start',
       'blind_spot_monitor', 'lane_assist', 'parking_assist_system',
       'stability_control', 'adaptive_cruise_control', 'alloy_wheels',
       'cooled_seats', 'full_self-driving_capability', 'third_row_seating',
       'tow_hitch_package', 'rear_seat_entertainment', 'avg_mpg']
    features = features[cols]
    features['type'] = features.type.str.lower()
    features['year'] = features.year.astype(int)
    #features['doors'] = features.doors.astype(int)
    features['miles_driven'] = features.doors.astype(float)
    for feat in features.columns:
        features[feat] = features[feat].map(lambda x : 0 if x=='' else x)
    print(features.iloc[0])
    print(features.dtypes)
    prediction = loaded_data.predict(features)
    return np.round(prediction[0],3)