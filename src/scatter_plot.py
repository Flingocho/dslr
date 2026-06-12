import sys
import pandas as pd
import matplotlib.pyplot as plt

HOUSES = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
COLORS = ['#c0392b', '#e67e22', '#2980b9', '#27ae60']

DEFAULT_X = 'Astronomy'
DEFAULT_Y = 'Defense Against the Dark Arts'


def get_values(series):
    return [float(v) for v in series if v == v]


def plot_scatter(path, feature_x, feature_y):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: file not found '{path}'")
        sys.exit(1)

    num_cols = [c for c in df.columns if df[c].dtype == 'float64']

    for feat in (feature_x, feature_y):
        if feat not in num_cols:
            print(f"Error: feature '{feat}' not found. Available features:")
            for c in num_cols:
                print(f"  {c}")
            sys.exit(1)

    plt.style.use('seaborn-v0_8-whitegrid')

    fig, ax = plt.subplots(figsize=(9, 7))

    for house, color in zip(HOUSES, COLORS):
        mask = df['Hogwarts House'] == house
        both = df[mask][[feature_x, feature_y]].dropna()
        x = get_values(both[feature_x])
        y = get_values(both[feature_y])
        ax.scatter(x, y, c=color, label=house, alpha=0.65, s=18, edgecolors='none')

    # Compute correlation
    both = df[[feature_x, feature_y]].dropna()
    x_all = get_values(both[feature_x])
    y_all = get_values(both[feature_y])
    n = len(x_all)
    mx = sum(x_all) / n
    my = sum(y_all) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x_all, y_all))
    dx = sum((xi - mx) ** 2 for xi in x_all) ** 0.5
    dy = sum((yi - my) ** 2 for yi in y_all) ** 0.5
    r = num / (dx * dy) if dx and dy else 0.0

    ax.set_xlabel(feature_x, fontsize=12, labelpad=8)
    ax.set_ylabel(feature_y, fontsize=12, labelpad=8)
    ax.set_title(f'{feature_x}  vs  {feature_y}', fontsize=14, fontweight='bold', pad=14)
    ax.annotate(
        f'Correlation r = {r:.4f}',
        xy=(0.05, 0.95), xycoords='axes fraction',
        fontsize=9, va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0f0f0', edgecolor='#cccccc', alpha=0.9)
    )
    ax.legend(title='House', fontsize=10, title_fontsize=10, framealpha=0.85)
    ax.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) not in (2, 4):
        print(f"Usage: {sys.argv[0]} <dataset.csv> [feature_x feature_y]")
        sys.exit(1)
    fx = sys.argv[2] if len(sys.argv) == 4 else DEFAULT_X
    fy = sys.argv[3] if len(sys.argv) == 4 else DEFAULT_Y
    plot_scatter(sys.argv[1], fx, fy)
