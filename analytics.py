import os
import pandas as pd
import matplotlib.pyplot as plt
from config import DATA_DIR

# Load data from CSV
def load_data(filename='results.csv'):
    """
    Loads data from a CSV file in the data directory.
    Returns a pandas DataFrame.
    """
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# Generate a simple sales chart
def generate_sales_chart(df, output_file='sales_chart.png'):
    """
    Generates a bar chart of sales by client and saves it to the data directory.
    """
    if 'client' in df.columns and 'amount' in df.columns:
        sales = df.groupby('client')['amount'].sum()
        plt.figure(figsize=(8, 4))
        sales.plot(kind='bar')
        plt.title('Sales by Client')
        plt.ylabel('Amount')
        plt.tight_layout()
        chart_path = os.path.join(DATA_DIR, output_file)
        plt.savefig(chart_path)
        plt.close()
        return chart_path
    return None 