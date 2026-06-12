import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

HOUSES = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
COLORS = ['#c0392b', '#e67e22', '#2980b9', '#27ae60']


def get_values(series):
    return [float(v) for v in series if v == v]


def plot_pair(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: file not found '{path}'")
        sys.exit(1)

    plt.style.use('seaborn-v0_8-whitegrid')

    courses = [c for c in df.columns if df[c].dtype == 'float64']
    n = len(courses)

    # Short labels to fit in the grid
    short = [c if len(c) <= 14 else c[:12] + '.' for c in courses]

    fig, axes = plt.subplots(n, n, figsize=(30, 30))
    fig.subplots_adjust(hspace=0.08, wspace=0.08, top=0.96, bottom=0.06, left=0.07, right=0.93)

    house_data = {h: df[df['Hogwarts House'] == h] for h in HOUSES}

    for row in range(n):
        for col in range(n):
            ax = axes[row][col]
            ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
            ax.set_facecolor('#fafafa')
            for spine in ax.spines.values():
                spine.set_linewidth(0.4)
                spine.set_color('#cccccc')

            if row == col:
                for house, color in zip(HOUSES, COLORS):
                    vals = get_values(house_data[house][courses[row]])
                    ax.hist(vals, bins=15, color=color, alpha=0.5, density=True, edgecolor='none')
                ax.set_facecolor('#f0f4ff')
            else:
                for house, color in zip(HOUSES, COLORS):
                    sub = house_data[house][[courses[col], courses[row]]].dropna()
                    x = get_values(sub[courses[col]])
                    y = get_values(sub[courses[row]])
                    ax.scatter(x, y, c=color, s=1.5, alpha=0.35, edgecolors='none')

            if col == 0:
                ax.set_ylabel(short[row], fontsize=6.5, rotation=40,
                              ha='right', va='center', labelpad=2)
            if row == n - 1:
                ax.set_xlabel(short[col], fontsize=6.5, rotation=40,
                              ha='right', va='top', labelpad=2)

    legend_patches = [mpatches.Patch(color=c, label=h) for h, c in zip(HOUSES, COLORS)]
    fig.legend(
        handles=legend_patches,
        loc='upper right', bbox_to_anchor=(0.97, 0.97),
        fontsize=11, title='House', title_fontsize=11,
        framealpha=0.9, edgecolor='#cccccc'
    )

    fig.suptitle('Pair plot — feature distributions and relationships by house',
                 fontsize=15, fontweight='bold')

    plt.savefig('pair_plot.png', bbox_inches='tight', dpi=120)
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dataset.csv>")
        sys.exit(1)
    plot_pair(sys.argv[1])
