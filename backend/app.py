from flask import Flask, request, jsonify

from flask_cors import CORS

import pickle

from preprocess import clean_text

# Create Flask App
app = Flask(__name__)

# Enable CORS
CORS(app)

# Load trained ML model
model = pickle.load(open("model.pkl", "rb"))

# Load TF-IDF vectorizer
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Home Route
@app.route('/')

def home():

    return "Complaint Categorization API Running"


# Prediction Route
@app.route('/predict', methods=['POST'])

def predict():

    try:

        # Get JSON data
        data = request.get_json()

        complaint = data['complaint']

        # Preprocess text
        cleaned_text = clean_text(complaint)

        # Convert text into vector
        vector = vectorizer.transform([cleaned_text])

        # Predict category
        prediction = model.predict(vector)[0]

        # Return response
        return jsonify({
            "success": True,
            "category": prediction
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


# Run Flask Server
if __name__ == '__main__':

    app.run(debug=True)