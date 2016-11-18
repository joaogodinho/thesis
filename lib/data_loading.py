import pandas as pd


# Load the Headers CSV file into a Pandas dataframe
# and set the date column as the index
def loadHeadersCSV(filename):
    # Read CSV into a pandas dataframe
    df = pd.read_csv(filename)
    # Convert from string to date
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    # Convert file type to string
    df['file_type'] = df['file_type'].astype(str)
    # Set date as index
    df = df.set_index('date')
    return df