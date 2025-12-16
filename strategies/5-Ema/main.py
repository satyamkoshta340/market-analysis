import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
# Signal: Low of any candle doesn't touch 5 ema line
# Entry: When low of the signal candle is taken out
# SL: High of signal candle
# Target: two times the body of signal candle


def find_signals(dp: pd.DataFrame):
    data = dp['Close']
    ema = data.ewm(span=5, adjust=False).mean()
    len = data.size

    signals = []

    for i in range(1, len):
        if dp['Low'][i-1] > ema[i-1] and dp['Low'][i] < ema[i]:
            signal = {}
            signal_candle_low = dp['Low'][i]
            signal_candle_high = dp['High'][i]
            signal_candle_body = abs(dp['Close'][i] - dp['Open'][i])
            
            signal['index'] = i
            signal['Date'] = dp['Date'][i] if 'Date' in dp else None
            signal['Time'] = dp['Time'][i] if 'Time' in dp else None
            signal['entry'] = signal_candle_low
            signal['stop_loss'] = signal_candle_high
            signal['target'] = signal['entry'] - 2 * signal_candle_body
            signal['Low'] = dp['Low'][i]
            signal['EMA_5'] = ema[i]

            # print(f"Signal: {signal}")
            signals.append(signal)
    return pd.DataFrame(signals)


def analyze_signals(dp: pd.DataFrame, signals_df: pd.DataFrame):
    # We'll split the analyses into two focused helper functions below.
    outdir = os.path.join(os.getcwd(), 'strategies', '5-Ema', 'output')
    os.makedirs(outdir, exist_ok=True)

    if signals_df is None or signals_df.empty:
        print('No signals found. Nothing to analyze.')
        return

    # Ensure we have a datetime column in signals_df. Try several fallbacks.
    if 'datetime' not in signals_df.columns:
        # Preferred: Date + Time present in signals_df
        if 'Date' in signals_df.columns and 'Time' in signals_df.columns:
            signals_df['datetime'] = pd.to_datetime(
                signals_df['Date'].astype(str) + ' ' + signals_df['Time'].astype(str),
                dayfirst=True, errors='coerce')
        # Fallback: use indexes referencing dp (signals store an 'index' column)
        elif 'index' in signals_df.columns and 'Date' in dp.columns and 'Time' in dp.columns:
            idx = signals_df['index'].astype(int)
            dt = pd.to_datetime(dp.loc[idx, 'Date'].astype(str) + ' ' + dp.loc[idx, 'Time'].astype(str),
                                dayfirst=True, errors='coerce').reset_index(drop=True)
            signals_df = signals_df.reset_index(drop=True)
            signals_df['datetime'] = dt
        else:
            for col in signals_df.columns:
                if ('date' in col.lower() and 'time' in col.lower()) or 'datetime' in col.lower():
                    signals_df['datetime'] = pd.to_datetime(signals_df[col], errors='coerce')
                    break

    # Ensure datetime dtype and drop missing
    signals_df['datetime'] = pd.to_datetime(signals_df.get('datetime'), errors='coerce')
    missing_dt = signals_df['datetime'].isna().sum()
    if missing_dt > 0:
        print(f"Warning: {missing_dt} signals have no parsable datetime and will be excluded from time-based analysis.")
    signals_df = signals_df.dropna(subset=['datetime']).copy()
    if signals_df.empty:
        print('After removing entries with missing datetime, no signals remain.')
        return

    # delegate to the two specialized analyzers
    freq_summary = analyze_frequency(signals_df, outdir)
    interval_summary = analyze_intervals(signals_df, outdir)

    # Save signals with datetime for reference
    signals_df.to_csv(os.path.join(outdir, 'signals_with_datetime.csv'), index=False)

    # Print combined summary
    print('--- Signal analysis summary ---')
    print(f"Total signals analyzed: {freq_summary.get('total_signals', 0)}")
    print(f"Days with signals: {freq_summary.get('days_with_signals', 0)}, mean signals/day: {freq_summary.get('mean_per_day', 0):.2f}")
    if freq_summary.get('max_day'):
        md = freq_summary['max_day']
        print(f"Max signals in a single day: {md['count']} on {md['date']}")
    if interval_summary.get('interval_stats'):
        isd = interval_summary['interval_stats']
        print('Interval stats between consecutive signals (minutes):')
        print(f"  mean={isd['mean_min']:.2f}, median={isd['median_min']:.2f}, min={isd['min_min']:.2f}, max={isd['max_min']:.2f}")
    print(f'Output files (CSVs + PNGs) written to: {outdir}')


def analyze_frequency(signals_df: pd.DataFrame, outdir: str) -> dict:
    """Analyze frequency of signals per day and by time-of-day.

    Returns a small summary dict with keys: total_signals, days_with_signals, mean_per_day, max_day
    Also writes CSVs and PNGs to outdir.
    """
    # 1) Frequency per day
    signals_df['date'] = signals_df['datetime'].dt.date
    signals_per_day = signals_df.groupby('date').size().reset_index(name='count').sort_values('date')
    signals_per_day.to_csv(os.path.join(outdir, 'signals_per_day.csv'), index=False)

    total_signals = len(signals_df)
    days_with_signals = signals_per_day.shape[0]
    mean_per_day = signals_per_day['count'].mean() if days_with_signals > 0 else 0
    max_day = signals_per_day.loc[signals_per_day['count'].idxmax()].to_dict() if days_with_signals > 0 else None

    # Counts by exact time of day (HH:MM)
    signals_df['time_str'] = signals_df['datetime'].dt.strftime('%H:%M')
    signals_by_time = signals_df.groupby('time_str').size().reset_index(name='count').sort_values('time_str')
    signals_by_time.to_csv(os.path.join(outdir, 'signals_by_time.csv'), index=False)

    # Plot: signals per day
    try:
        sns.set_style('whitegrid')
        plt.figure(figsize=(10, 4))
        sns.barplot(x='date', y='count', data=signals_per_day, color='tab:blue')
        plt.xticks(rotation=45, ha='right')
        plt.title('Signals per day')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'plot_signals_per_day.png'))
        plt.close()
    except Exception as e:
        print('Could not plot signals_per_day:', e)

    # Plot: signals by time of day (HH:MM)
    try:
        plt.figure(figsize=(12, 4))
        sns.barplot(x='time_str', y='count', data=signals_by_time, color='tab:green')
        plt.xticks(rotation=90)
        plt.xlabel('Time of day')
        plt.title('Signals by time of day')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'plot_signals_by_time.png'))
        plt.close()
    except Exception as e:
        print('Could not plot signals_by_time:', e)

    return {
        'total_signals': int(total_signals),
        'days_with_signals': int(days_with_signals),
        'mean_per_day': float(mean_per_day),
        'max_day': max_day,
    }


def analyze_intervals(signals_df: pd.DataFrame, outdir: str) -> dict:
    """Analyze time intervals between consecutive signals.

    Returns a dict with interval_stats and writes CSVs and plots to outdir.
    """
    signals_sorted = signals_df.sort_values('datetime').reset_index(drop=True)
    signals_sorted['delta_min'] = signals_sorted['datetime'].diff().dt.total_seconds() / 60.0

    intervals = signals_sorted['delta_min'].dropna()
    interval_stats = {}
    if not intervals.empty:
        interval_stats = {
            'count_intervals': int(intervals.size),
            'min_min': float(intervals.min()),
            'median_min': float(intervals.median()),
            'mean_min': float(intervals.mean()),
            'max_min': float(intervals.max()),
            '25%': float(intervals.quantile(0.25)),
            '75%': float(intervals.quantile(0.75)),
        }

    # Average interval per day
    avg_interval_per_day = signals_sorted.groupby(signals_sorted['datetime'].dt.date)['delta_min'].mean().reset_index(name='avg_interval_min')
    avg_interval_per_day.to_csv(os.path.join(outdir, 'avg_interval_per_day.csv'), index=False)

    # Save full interval series
    signals_sorted.to_csv(os.path.join(outdir, 'signal_intervals.csv'), index=False)

    # Plot: average interval per day
    try:
        plt.figure(figsize=(10, 4))
        sns.lineplot(x='datetime', y='delta_min', data=signals_sorted, marker='o')
        # format x axis if many dates
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Interval (min)')
        plt.title('Intervals between consecutive signals (time series)')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'plot_intervals_timeseries.png'))
        plt.close()
    except Exception as e:
        print('Could not plot intervals timeseries:', e)

    # Plot: distribution of intervals between consecutive signals
    try:
        plt.figure(figsize=(8, 4))
        if not intervals.empty:
            sns.histplot(intervals, bins=30, kde=True, color='tab:orange')
        plt.xlabel('Interval between signals (minutes)')
        plt.title('Distribution of intervals between consecutive signals')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'plot_intervals_hist.png'))
        plt.close()
    except Exception as e:
        print('Could not plot intervals histogram:', e)

    return {
        'interval_stats': interval_stats,
        'avg_interval_per_day': avg_interval_per_day,
    }
    


def main():
    dp = pd.read_csv( os.getcwd()+"/assets/BANK_NIFTY_5_MIN_2020.csv")
    print(dp.head())
    signals_df = find_signals(dp)
    print(signals_df.head())
    # run the analysis on the detected signals
    analyze_signals(dp, signals_df)


if __name__ == "__main__":
    main()