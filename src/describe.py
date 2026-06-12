import sys
import pandas as pd


def get_values(series):
    result = []
    for v in series:
        if v == v:  # NaN != NaN in IEEE 754
            result.append(float(v))
    return result


def ft_count(values):
    return float(len(values))


def ft_mean(values):
    if not values:
        return float('nan')
    total = 0.0
    for v in values:
        total += v
    return total / len(values)


def ft_std(values):
    if len(values) < 2:
        return float('nan')
    m = ft_mean(values)
    total = 0.0
    for v in values:
        total += (v - m) ** 2
    return (total / (len(values) - 1)) ** 0.5


def ft_min(values):
    if not values:
        return float('nan')
    m = values[0]
    for v in values[1:]:
        if v < m:
            m = v
    return m


def ft_max(values):
    if not values:
        return float('nan')
    m = values[0]
    for v in values[1:]:
        if v > m:
            m = v
    return m


def ft_percentile(values, p):
    if not values:
        return float('nan')
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    idx = p / 100.0 * (n - 1)
    lo = int(idx)
    hi = lo + 1
    frac = idx - lo
    if hi >= n:
        return float(sorted_vals[lo])
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


def ft_variance(values):
    s = ft_std(values)
    return s * s if s == s else float('nan')


def ft_range(values):
    if not values:
        return float('nan')
    return ft_max(values) - ft_min(values)


def ft_iqr(values):
    if not values:
        return float('nan')
    return ft_percentile(values, 75) - ft_percentile(values, 25)


def ft_skewness(values):
    # Sample skewness with bias correction (matches scipy.stats.skew)
    n = len(values)
    if n < 3:
        return float('nan')
    m = ft_mean(values)
    s = ft_std(values)
    if s == 0:
        return float('nan')
    total = 0.0
    for v in values:
        total += ((v - m) / s) ** 3
    return (n / ((n - 1) * (n - 2))) * total


def ft_kurtosis(values):
    # Excess kurtosis with bias correction (matches scipy.stats.kurtosis)
    n = len(values)
    if n < 4:
        return float('nan')
    m = ft_mean(values)
    s = ft_std(values)
    if s == 0:
        return float('nan')
    total = 0.0
    for v in values:
        total += ((v - m) / s) ** 4
    k = ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * total
    correction = (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return k - correction


def describe(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: file not found '{path}'")
        sys.exit(1)

    num_cols = [
        col for col in df.columns
        if df[col].dtype in ('float64', 'int64') and col != 'Index'
    ]

    stats_order = [
        'Count', 'Mean', 'Std', 'Variance',
        'Min', '25%', '50%', '75%', 'Max',
        'Range', 'IQR', 'Skewness', 'Kurtosis',
    ]

    data = {}
    for col in num_cols:
        vals = get_values(df[col])
        data[col] = {
            'Count':    ft_count(vals),
            'Mean':     ft_mean(vals),
            'Std':      ft_std(vals),
            'Variance': ft_variance(vals),
            'Min':      ft_min(vals),
            '25%':      ft_percentile(vals, 25),
            '50%':      ft_percentile(vals, 50),
            '75%':      ft_percentile(vals, 75),
            'Max':      ft_max(vals),
            'Range':    ft_range(vals),
            'IQR':      ft_iqr(vals),
            'Skewness': ft_skewness(vals),
            'Kurtosis': ft_kurtosis(vals),
        }

    name_w = max(len(c) for c in num_cols)
    stat_w = 12

    int_stats = {'Count'}

    header = f"{'Feature':<{name_w}}"
    for stat in stats_order:
        header += f"  {stat:>{stat_w}}"
    print(header)
    print('-' * (name_w + (stat_w + 2) * len(stats_order)))

    for col in num_cols:
        row = f"{col:<{name_w}}"
        for stat in stats_order:
            v = data[col][stat]
            if stat in int_stats:
                row += f"  {int(v):>{stat_w}}"
            else:
                row += f"  {v:>{stat_w}.2f}"
        print(row)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dataset.csv>")
        sys.exit(1)
    describe(sys.argv[1])
