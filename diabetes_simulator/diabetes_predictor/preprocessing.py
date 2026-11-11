def handle_zeros(X):
    X = X.copy()
    to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in to_fix:
        if col in X.columns:
            notzero_mask = X[col] != 0
            zero_mask = X[col] == 0

            col_med = X.loc[notzero_mask, col].median()
            X.loc[zero_mask, col] = col_med
    return X