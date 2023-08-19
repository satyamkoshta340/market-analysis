import pandas as pd

# Sample data as a dictionary (1-minute candle data)
year = '2021'
data = pd.read_csv('E://Abhishek_Koshta//Personal//Investment//Back Testing//market-analysis//Zerodha//Download Data//BANK_NIFTY_data//BNF_{}.csv'.format(year))

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Combine "date" and "time" columns into a single datetime column
df["timestamp"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"], format="%Y%m%d %H:%M")

# Set the "timestamp" column as the index
df.set_index("timestamp", inplace=True)

# Resample the data to 5-minute intervals
df_resampled = df.resample('5T').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
})

# Look for time between 9:30 AM to 3:20 PM
df_resampled = df_resampled.between_time('9:15', '15:20')
df_resampled.dropna(inplace=True)

# Define the move threshold and move times dictionary
move_threshold = 500
move_times = {}
total_move = {}
max_times = {}
min_times = {}
dates_above_threshold = []

# Analyze the resampled data for trendy days
for date, day_data in df_resampled.groupby(df_resampled.index.date):
    max_time = day_data["high"].idxmax()
    min_time = day_data["low"].idxmin()
    move_time = int((max_time - min_time).total_seconds() / 3600)  # in hours
    max_candle_number = day_data.index.get_loc(max_time)
    min_candle_number = day_data.index.get_loc(min_time)

    high_of_the_day = day_data["high"].max()
    low_of_the_day = day_data["low"].min()
    move = int(high_of_the_day - low_of_the_day)

    if move > move_threshold:
        dates_above_threshold.append(date)
        move_times[date] = move_time
        total_move[date] = move
        max_times[date] = max_time.time()
        min_times[date] = min_time.time()
        # print(date, "may be a potential trendy day with a move of", move, "Move Time:", move_time)

# Calculate the days after which the move was seen again
days_between_moves = {}
prev_date = None
for date in dates_above_threshold:
    if prev_date is not None:
        days_between_moves[date] = (date - prev_date).days
    else:
        days_between_moves[date] = 0
    prev_date = date

# Create a DataFrame to store the information
result_df = pd.DataFrame({
    'Date': list(move_times.keys()),
    'Total Move': list(total_move.values()),
    'High Made': list(max_times.values()),
    'Low Made': list(min_times.values()),
    'Move Time (Hours)': list(move_times.values()),
    'Days Between Moves': list(days_between_moves.values())
})

# Add additional columns for month, move type, and week of the day
result_df['Date'] = pd.to_datetime(result_df['Date'].astype(str), format='%Y-%m-%d')
result_df['Move Type'] = result_df['Move Time (Hours)'].apply(lambda x: 'Up' if x > 0 else 'Down')
result_df['Weekday'] = result_df['Date'].dt.strftime('%A')
result_df['Day_of_month'] = result_df['Date'].dt.strftime('%d')
result_df['Month'] = result_df['Date'].dt.strftime('%B')
result_df['Year'] = result_df['Date'].dt.strftime('%Y')

# Print the resulting DataFrame
print(result_df)
result_df.to_csv('BNF_Stats_{}.csv'.format(year))