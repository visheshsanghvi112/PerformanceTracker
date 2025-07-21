from datasets import load_dataset
import pandas as pd

# Load dataset
dataset = load_dataset("imdb")
df = pd.DataFrame(dataset["train"])

def get_reviews_for_movie(movie_name, limit=30):
    filt = df[df["text"].str.contains(movie_name, case=False, na=False)]
    return filt.head(limit).copy()
