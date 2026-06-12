import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

HOUSES = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
COLORS = ['#c0392b', '#e67e22', '#2980b9', '#27ae60']


def get_values(series):
    return [float(v) for v in series if v == v]


def plot_histograms(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: file not found '{path}'")
        sys.exit(1)

    plt.style.use('seaborn-v0_8-whitegrid')

    courses = [c for c in df.columns if df[c].dtype == 'float64']
    n_courses = len(courses)
    n_cols = 4
    n_rows = (n_courses + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(20, n_rows * 4 + 1.5))
    fig.suptitle(
        'Score distribution per course and house\n'
        'Arithmancy shows the most homogeneous distribution across all four houses',
        fontsize=14, fontweight='bold', y=0.98
    )

    gs = gridspec.GridSpec(n_rows, n_cols, figure=fig, hspace=0.55, wspace=0.35)

    for i, course in enumerate(courses):
        row, col = divmod(i, n_cols)
        ax = fig.add_subplot(gs[row, col])

        for house, color in zip(HOUSES, COLORS):
            vals = get_values(df[df['Hogwarts House'] == house][course])
            ax.hist(vals, bins=20, alpha=0.55, color=color, label=house, density=True, edgecolor='none')

        is_answer = course == 'Arithmancy'
        ax.set_title(
            course,
            fontsize=9,
            fontweight='bold' if is_answer else 'normal',
            color='#c0392b' if is_answer else 'black',
            pad=6
        )
        ax.set_xlabel('Score', fontsize=8)
        ax.set_ylabel('Density', fontsize=8)
        ax.tick_params(labelsize=7)
        ax.spines[['top', 'right']].set_visible(False)

        if i == 0:
            ax.legend(fontsize=7.5, framealpha=0.8, loc='upper right')

    # Hide unused subplots
    for j in range(i + 1, n_rows * n_cols):
        r, c = divmod(j, n_cols)
        fig.add_subplot(gs[r, c]).set_visible(False)

    plt.show()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dataset.csv>")
        sys.exit(1)
    plot_histograms(sys.argv[1])
