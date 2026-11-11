from pathlib import Path
import json
import math

from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render

from .predictor import DiabetesPredictorModel
from .models import Patient


BASE_DIR = Path(__file__).resolve().parents[2]
params_path = BASE_DIR/'Trained Model'/'nb_pipe'/'model_params.json'

the_model = None
params = None

def predict_view(request):
    global the_model
    if the_model is None:
        the_model = DiabetesPredictorModel()

    pred_info, mental_info = None, None
    error = None
    baseline_features_json = None
    if request.method=='POST':
        # checking blank input
        keys = ['preg', 'glc', 'pressure', 'skin', 'insulin', 'bmi', 'dpfunc', 'age']
        missing = [key for key in keys if request.POST.get(key) == '']

        if missing:
            error = f'Missing values for {", ".join(missing)}'
        else:
            # catching user inputs
            try:
                features = [
                    float(request.POST.get('preg')),
                    float(request.POST.get('glc')),
                    float(request.POST.get('pressure')),
                    float(request.POST.get('skin')),
                    float(request.POST.get('insulin')),
                    float(request.POST.get('bmi')),
                    float(request.POST.get('dpfunc')),
                    float(request.POST.get('age')),
                ]
                ranges = [
                    (0, 30),    # Pregnancies
                    (50, 400),  # Glucose
                    (60, 200),  # BloodPressure
                    (5, 80),    # SkinThickness
                    (2, 900),   # Insulin
                    (14, 65),   # BMI
                    (0.07, 3),  # DiabetesPedigreeFunction
                    (1, 110)    # Age
                ]

                questions = [
                    int(request.POST.get('q1')),
                    int(request.POST.get('q2')),
                    int(request.POST.get('q3')),
                    int(request.POST.get('q4')),
                    int(request.POST.get('q5')),
                    int(request.POST.get('q6')),
                    int(request.POST.get('q7')),
                    int(request.POST.get('q8')),
                    int(request.POST.get('q9')),
                ]

                # checking range
                for val, (low, high) in zip(features, ranges):
                    if not low <= val <= high:
                        error = 'Entered values not in the reasonable range'
                        break

                if error is None:
                    request.session['user_features'] = features
                    baseline_features_json = json.dumps(features)

                    pred_info = the_model.predict(features)

                    # PHQ-9 score
                    score = 0
                    for n in questions:
                        score += n-1
                    mental_info = 1 if score >= 12 else 0

                    # Saving to DB
                    Patient.objects.create(
                    pregnancies=features[0],
                    glucose = features[1],
                    bloodpressure = features[2],
                    skinthickness = features[3],
                    insulin = features[4],
                    bmi = features[5],
                    pedigreefunc = features[6],
                    age = features[7],
                    status = pred_info.get('risk_class', 'N/A'),
                    confidence= pred_info.get('probability', 'N/A'),

                    q1 = questions[0],
                    q2 = questions[1],
                    q3 = questions[2],
                    q4 = questions[3],
                    q5 = questions[4],
                    q6 = questions[5],
                    q7 = questions[6],
                    q8 = questions[7],
                    q9 = questions[8],
                    score = score
                    )

            except (ValueError, TypeError):
                error = 'Entered values are not supported'

    return render(
        request,
        template_name='template.html',
        context={
            'pred_info': pred_info,
            'mental_info': mental_info,
            'error': error,
            'baseline_features': baseline_features_json
        }
    )


def simulate_view(request):
    if request.method != 'POST':    # we don't allow other reqs for this func
        return HttpResponseNotAllowed(['POST'])

    features = request.session.get('user_features')
    if features is None:
        return JsonResponse({'error': 'No baseline prediction found.'}, status=400)
    if len(features) != 8:
        return JsonResponse({'error': 'Invalid baseline'}, status=400)

    try:
        body = json.loads(request.body)     # json.loads() takes a JSON-formatted string and converts it into a dictionary
                                            # here the JSON data is a string
        # request.body is a "string" of bytes sent from the frontend(JavaScript fetch() call)
        # eg '{"updates": {"BMI": -2, "Glucose": -10}}'
        updates = body.get('updates', {})
        if not isinstance(updates, dict):
            raise ValueError('The updates must be a dictionary')
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

    # Load simulation parameters (once)
    global params
    if params is None:
        with open(params_path, 'r', encoding='utf-8') as f:
            params = json.load(f)

    # Extract the pieces
    w = params['w']
    b = params['b'][0] if isinstance(params['b'], list) else params['b']
    m = params['m']
    dev = params['dev']
    feature_names = params['features']  # order of features

    # Apply updates to a copy of the baseline
    modified = list(features)  # make a mutable copy
    for feature, change in updates.items():
        if feature not in feature_names:
            continue  # ignore unknown features
        idx = feature_names.index(feature)
        modified[idx] += change

    # Manual scaling
    scaled = []
    for i in range(8):
        scaled_mdf = (modified[i] - m[i]) / dev[i]
        scaled.append(scaled_mdf)

    # Manual Logistic Regression
    z = b + sum(
        w[k] * scaled[k] for k in range(8)
    )
    prob = 1 / (1 + math.exp(-z))

    # Apply tuned threshold
    threshold = 0.45
    risk_class = 1 if prob >= threshold else 0

    # Compute original probability (for comparison message)
    orig_scaled = [(features[i] - m[i]) / dev[i] for i in range(8)]
    orig_z = b + sum(
        w[i] * orig_scaled[i] for i in range(8)
    )
    orig_prob = 1 / (1 + math.exp(-orig_z))


    change_prc = (prob - orig_prob) * 100
    effect = "increases" if change_prc > 0 else "decreases"
    message = (
        f"With these changes, your diabetes risk {effect} from {orig_prob*100:.2f}% to {prob*100:.2f}% "
        f"({'high' if risk_class == 1 else 'low'} risk)."
    )

    return JsonResponse({
        'probability': round(prob, 4),
        'risk_class': risk_class,
        'original_probability': round(orig_prob, 4),
        'message': message
    })