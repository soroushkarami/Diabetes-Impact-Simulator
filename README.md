# Diabetes Impact Simulator

Django app that predicts diabetes risk using a trained ML pipeline and allows real-time "What-If" simulation via UI sliders. Also includes a PHQ-9 mental health screening.

## Setup
    pip install -r requirements.txt
    cd diabetes_simulator
    python manage.py migrate
    python manage.py runserver

Open http://127.0.0.1:8000

## Structure
- `Trained Model/` — Training notebooks, ML pipeline artifacts, and extracted mathematical parameters for the simulator.
- `diabetes_simulator/` — Django app (views, predictor service, template).

## How the Simulator Works
Instead of running a heavy model on every slider drag, the app extracts the Logistic Regression coefficients into `model_params.json`. The frontend calculates the risk dynamically using simple math (`z = b + Σ(w * x)`).