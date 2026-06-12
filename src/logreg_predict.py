import sys
import json
import pandas as pd
import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def preprocess(df, features, norm_means, norm_stds):
    raw = df[features].values.astype(float)

    # Impute NaN with training means
    for j in range(raw.shape[1]):
        for i in range(raw.shape[0]):
            if raw[i, j] != raw[i, j]:
                raw[i, j] = norm_means[j]

    # Normalize using training parameters
    for j in range(raw.shape[1]):
        raw[:, j] = (raw[:, j] - norm_means[j]) / norm_stds[j]

    return raw


def predict(dataset_path, weights_path):
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"Error: file not found '{dataset_path}'")
        sys.exit(1)

    try:
        with open(weights_path) as f:
            w = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found '{weights_path}'")
        sys.exit(1)

    features   = w['features']
    houses     = w['houses']
    norm_means = w['norm_means']
    norm_stds  = w['norm_stds']
    thetas     = [np.array(t) for t in w['thetas']]

    X = preprocess(df, features, norm_means, norm_stds)
    m = X.shape[0]
    X_b = np.hstack([np.ones((m, 1)), X])

    # Score each house and pick the highest probability
    scores = np.array([sigmoid(X_b @ theta) for theta in thetas])
    predictions = [houses[i] for i in np.argmax(scores, axis=0)]

    with open('houses.csv', 'w') as f:
        f.write('Index,Hogwarts House\n')
        for idx, house in enumerate(predictions):
            f.write(f'{idx},{house}\n')

    print(f"Predictions saved to 'houses.csv' ({m} students)")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <dataset_test.csv> <weights.json>")
        sys.exit(1)
    predict(sys.argv[1], sys.argv[2])
