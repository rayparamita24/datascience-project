# -*- coding: utf-8 -*-
"""Election Result_prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/167WkqFx4IGojB7O2ZDh6zeGZxRidefyH
"""

# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load Data
data = pd.read_csv("/content/election_data.csv")  # Replace with your file path

# Check unique parties in the original data before encoding
print("Unique Parties in Dataset:", data['party'].unique())

# Step 2: Preprocess Data
# Convert 'state' and 'party' categorical variables to dummy/indicator variables
data = pd.get_dummies(data, columns=['state', 'party'], drop_first=False)

# Define features and target
X = data[['like_count', 'poll_percentage'] + [col for col in data.columns if 'state_' in col or 'party_' in col]]
y = data['result_prediction']  # Target variable

# Handle Missing Values in Target Variable (y)
# Remove rows with missing values in the target variable
data = data.dropna(subset=['result_prediction'])

# Update X and y after removing rows
X = data[['like_count', 'poll_percentage'] + [col for col in data.columns if 'state_' in col or 'party_' in col]]
y = data['result_prediction']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Impute missing values in features using the mean strategy
imputer = SimpleImputer(strategy='mean')
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

# Convert X_test back to DataFrame with original column names for easier handling
X_test = pd.DataFrame(X_test, columns=X.columns)

# Step 3: Train the Support Vector Regressor
svr_model = SVR(kernel='rbf', C=100, epsilon=0.1)
svr_model.fit(X_train, y_train)

# Step 4: Predict Results
y_pred = svr_model.predict(X_test)

# Add Actual and Predicted Results to X_test DataFrame for visualization
X_test['Actual Result'] = y_test.reset_index(drop=True)
X_test['Predicted Result'] = y_pred

# Calculate evaluation metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r_squared = r2_score(y_test, y_pred)

# Print the evaluation metrics
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R-squared (R²): {r_squared:.2f}")

# Reconstruct 'Party' labels from dummy columns
party_columns = [col for col in data.columns if 'party_' in col]

# Check if all expected party columns are present in X_test
party_columns_in_X_test = [col for col in party_columns if col in X_test.columns]

# Reconstruct party labels from dummy columns
if party_columns_in_X_test:
    X_test['Party'] = X_test[party_columns_in_X_test].idxmax(axis=1).str.replace('party_', '')
else:
    print("No party columns found in X_test. Cannot reconstruct 'Party' labels.")

# Debugging Check: Check if Party reconstruction was successful
if 'Party' in X_test.columns:
    unique_parties = X_test['Party'].unique()
    print("Parties in Test Set after Reconstruction:", unique_parties)

    # Ensure the party_colors dictionary includes all unique parties
    party_colors = {
        'Communist': 'blue',  # Replace with actual party names
        'BJP': 'red',
        'IND': 'green',
        'OTHER': 'orange',
        # Add more parties and their corresponding colors as needed
    }

    # Check for missing party colors
    for party in unique_parties:
        if party not in party_colors:
            print(f"Warning: No color defined for party '{party}'")
            # Optionally assign a default color
            party_colors[party] = 'gray'  # Assign gray to any party not in the color dictionary
else:
    print("Party column is missing from the test set.")

# Add a color column to X_test based on the Party column
X_test['Color'] = X_test['Party'].map(party_colors)

# Step 6: Visualize Results with Defined Colors
plt.figure(figsize=(12, 8))
sns.scatterplot(
    x=X_test['Actual Result'],
    y=X_test['Predicted Result'],
    hue=X_test['Party'],  # Use Party directly for proper coloring
    palette=party_colors,
    alpha=0.7,
    s=100
)

# Add labels and title
plt.xlabel("Actual Election Result")
plt.ylabel("Predicted Election Result")
plt.title("Election Result Predictions by Party with Support Vector Regression")
plt.legend(title="Party", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='black', linestyle='--')  # Diagonal line
plt.grid(True)

# Show plot
plt.show()