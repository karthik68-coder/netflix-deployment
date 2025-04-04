from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import os

# Initialise Flask app
app = Flask(__name__)

# Load trained model
try:
    model = joblib.load('netflix_kmeans_model.pkl')
    model_name = 'K-Means (netflix_kmeans_model.pkl)'
except FileNotFoundError:
    print("Error: Model file not found. Ensure 'netflix_kmeans_model.pkl' exists.")
    exit()

# Load dataset for visualization
try:
    df = pd.read_csv('Netflix_Dataset.csv')
    numeric_data = df.select_dtypes(include=[np.number]).iloc[:, :3]

    if numeric_data.shape[1] < 3:
        raise ValueError("Error: Dataset must have at least 3 numeric columns for clustering.")

    pca = PCA(n_components=2)
    data_2d = pca.fit_transform(numeric_data)
    labels = model.predict(numeric_data.values)
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        features = [float(request.form[f'feature{i}']) for i in range(1, 4)]
        
        if len(features) != 3:
            raise ValueError("Please provide exactly 3 features.")

        prediction = model.predict([features])[0]
        result = f'Cluster {prediction} (Model: {model_name})'
    except Exception as e:
        result = f"Error: {e}"
    return render_template('result.html', prediction=result)

@app.route('/visualize')
def visualize():
    try:
        plt.figure(figsize=(8, 6))
        plt.scatter(data_2d[:, 0], data_2d[:, 1], c=labels, cmap='viridis')
        plt.title('Cluster Visualization using PCA')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.colorbar(label='Cluster')

        # Ensure static directory exists
        if not os.path.exists('static'):
            os.makedirs('static')

        # Save the image
        image_path = 'static/cluster_plot.png'
        plt.savefig(image_path)
        plt.close()

        return render_template('visualize.html', image_path=image_path, model_name=model_name)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
