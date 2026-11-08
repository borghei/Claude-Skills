# Deliberately vulnerable model-serving app: input for ai_threat_scanner.py (expect exit 1).
# Not meant to be run.
import pickle

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")
DEBUG = True


@app.post("/predict")
def predict():
    model = pickle.loads(request.data)
    user_input = request.json["text"]
    prompt = f"Answer the customer: {user_input}"
    scores = model.predict_proba([prompt])
    return {"label": model.predict([prompt])[0], "confidence": scores.tolist()}


@app.post("/calc")
def calc():
    return {"result": eval(request.args["user_expr"])}
