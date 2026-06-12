import sys
import json
import argparse
import pandas as pd
import numpy as np

HOUSES = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']

FEATURES = [
    'Arithmancy', 'Astronomy', 'Herbology', 'Defense Against the Dark Arts',
    'Divination', 'Muggle Studies', 'Ancient Runes', 'History of Magic',
    'Transfiguration', 'Potions', 'Care of Magical Creatures', 'Charms', 'Flying'
]


# ── numeric utilities (no statistical library functions) ──────────────────

def col_mean(col):
    total, count = 0.0, 0
    for v in col:
        if v == v:  # NaN != NaN in IEEE 754
            total += v
            count += 1
    return total / count if count else 0.0


def col_std(col, mean):
    total, count = 0.0, 0
    for v in col:
        if v == v:
            total += (v - mean) ** 2
            count += 1
    return (total / (count - 1)) ** 0.5 if count > 1 else 1.0


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


# ── preprocessing ─────────────────────────────────────────────────────────

def preprocess(df, features):
    """Return normalized X (m x n) and the normalization parameters (means, stds)."""
    raw = df[features].values.astype(float)

    # 1. Compute column means for NaN imputation
    imp_means = []
    for j in range(raw.shape[1]):
        imp_means.append(col_mean(raw[:, j]))

    # 2. Impute NaN with column means
    for j in range(raw.shape[1]):
        for i in range(raw.shape[0]):
            if raw[i, j] != raw[i, j]:
                raw[i, j] = imp_means[j]

    # 3. Z-score normalization
    norm_means, norm_stds = [], []
    for j in range(raw.shape[1]):
        m = col_mean(raw[:, j])
        s = col_std(raw[:, j], m)
        norm_means.append(m)
        norm_stds.append(s if s != 0 else 1.0)
        raw[:, j] = (raw[:, j] - m) / (s if s != 0 else 1.0)

    return raw, norm_means, norm_stds


# ── gradient descent optimizers ───────────────────────────────────────────

def train_batch(X_b, y, lr, epochs):
    m = X_b.shape[0]
    theta = np.zeros(X_b.shape[1])
    for _ in range(epochs):
        h = sigmoid(X_b @ theta)
        grad = X_b.T @ (h - y) / m
        theta -= lr * grad
    return theta


def train_sgd(X_b, y, lr, epochs):
    m = X_b.shape[0]
    theta = np.zeros(X_b.shape[1])
    for _ in range(epochs):
        idx = np.random.permutation(m)
        for i in idx:
            h = sigmoid(X_b[i] @ theta)
            grad = X_b[i] * (h - y[i])
            theta -= lr * grad
    return theta


def train_minibatch(X_b, y, lr, epochs, batch_size=32):
    m = X_b.shape[0]
    theta = np.zeros(X_b.shape[1])
    for _ in range(epochs):
        idx = np.random.permutation(m)
        for start in range(0, m, batch_size):
            batch = idx[start:start + batch_size]
            h = sigmoid(X_b[batch] @ theta)
            grad = X_b[batch].T @ (h - y[batch]) / len(batch)
            theta -= lr * grad
    return theta


# ── one-vs-all training ───────────────────────────────────────────────────

def train_ova(X, labels, optimizer, lr, epochs, batch_size):
    m = X.shape[0]
    X_b = np.hstack([np.ones((m, 1)), X])  # prepend bias column
    thetas = []
    for house in HOUSES:
        y = (labels == house).astype(float)
        if optimizer == 'batch':
            theta = train_batch(X_b, y, lr, epochs)
        elif optimizer == 'sgd':
            theta = train_sgd(X_b, y, lr, epochs)
        else:
            theta = train_minibatch(X_b, y, lr, epochs, batch_size)
        thetas.append(theta.tolist())
        print(f"  [{house}] trained", flush=True)
    return thetas


# ── main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Train one-vs-all logistic regression')
    parser.add_argument('dataset', help='Path to the training CSV')
    parser.add_argument('--optimizer', choices=['batch', 'sgd', 'mini-batch'],
                        default='batch', help='Optimization algorithm (default: batch)')
    parser.add_argument('--lr', type=float, default=0.1, help='Learning rate (default: 0.1)')
    parser.add_argument('--epochs', type=int, default=1000, help='Number of epochs (default: 1000)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Mini-batch size, only for --optimizer mini-batch (default: 32)')
    parser.add_argument('--output', default='weights.json', help='Output file (default: weights.json)')
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.dataset)
    except FileNotFoundError:
        print(f"Error: file not found '{args.dataset}'")
        sys.exit(1)

    print(f"Training with optimizer={args.optimizer}, lr={args.lr}, epochs={args.epochs}")

    X, norm_means, norm_stds = preprocess(df, FEATURES)
    labels = df['Hogwarts House'].values

    thetas = train_ova(X, labels, args.optimizer, args.lr, args.epochs, args.batch_size)

    weights = {
        'houses':     HOUSES,
        'features':   FEATURES,
        'norm_means': norm_means,
        'norm_stds':  norm_stds,
        'thetas':     thetas,
    }
    with open(args.output, 'w') as f:
        json.dump(weights, f, indent=2)

    print(f"Weights saved to '{args.output}'")


if __name__ == '__main__':
    main()
