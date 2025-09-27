import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import traceback

st.title("CORD-19 Data Explorer")
st.write("Simple exploration of COVID-19 research papers")

CSV_PATH = r"C:\Users\charles\project2\Frameworks_assignment\data\metadata.csv"

@st.cache_data
def load_csv(path, chunksize=100000):
    try:
        chunks = []
        for chunk in pd.read_csv(path, low_memory=False, chunksize=chunksize, encoding='utf-8'):
            chunks.append(chunk)
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.DataFrame()
        return df
    except UnicodeDecodeError:
        # fallback to different encoding
        chunks = []
        for chunk in pd.read_csv(path, low_memory=False, chunksize=chunksize, encoding='ISO-8859-1'):
            chunks.append(chunk)
        return pd.concat(chunks, ignore_index=True)
    except Exception as e:
        # show full traceback in the app for debugging
        st.error("Failed to load CSV — see details below.")
        st.text(traceback.format_exc())
        raise

# Attempt load
try:
    df = load_csv(CSV_PATH)
except Exception:
    st.stop()

if df.empty:
    st.warning("Loaded dataframe is empty. Check the CSV path and that the file isn't corrupted.")
    st.stop()

# Safe publish_time -> year conversion
df['publish_time'] = pd.to_datetime(df.get('publish_time', pd.Series([])), errors='coerce')
years = df['publish_time'].dt.year.dropna().astype(int)

if years.empty:
    # fallback: allow a reasonable slider range
    current_year = datetime.now().year
    min_year, max_year = 2019, current_year
    st.warning("No valid publication years found; using fallback year range.")
else:
    min_year, max_year = int(years.min()), int(years.max())

# Ensure slider defaults are within bounds
default_range = (min_year, max_year)
year_range = st.slider("Select Year Range", min_year, max_year, default_range)

# Filter safely using publish_time (not df['year'] to avoid NaN-int casting)
mask = df['publish_time'].dt.year.between(year_range[0], year_range[1])
filtered_df = df[mask]

st.write(f"Number of papers: {len(filtered_df)}")
st.dataframe(filtered_df.head())

# Plot publications by year (compute from filtered_df)
year_counts = filtered_df['publish_time'].dt.year.value_counts().sort_index()
fig, ax = plt.subplots()
sns.barplot(x=year_counts.index.astype(int), y=year_counts.values, ax=ax)
ax.set_title('Publications by Year')
ax.set_xlabel('Year')
ax.set_ylabel('Count')
plt.tight_layout()
st.pyplot(fig)
