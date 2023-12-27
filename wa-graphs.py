### Grafiekjes obv de csv output van wa-stats.py

## Waar gaan we mee klooien?
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import timedelta
import glob
import os
import numpy as np
import statsmodels.api as sm
from wordcloud import WordCloud
# import networkx as nx
import emoji
from textblob import TextBlob
import nltk
import re
import argparse

## Load the data
# Add argument parser to get the file path from the command line
parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="The path to the .txt file")
args = parser.parse_args()

# Get the directory of the input file and the name of the input file without the extension
input_dir = os.path.dirname(args.file_path)
input_file_name = os.path.splitext(os.path.basename(args.file_path))[0]

# Define the output directory
output_dir = os.path.join(input_dir, input_file_name, 'output')

# Find the most recent CSV file in the output directory
list_of_files = glob.glob(os.path.join(output_dir, 'raw-data.csv')) 
latest_file = max(list_of_files, key=os.path.getctime)

# Read the CSV file
df = pd.read_csv(latest_file)

## Convert 'Date' and 'Time' to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time

################
#### Graphs ####
################

## Message Frequency Over Time
# Convert 'Date' to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
# Calculate message counts per date
date_counts = df['Date'].value_counts().sort_index().reset_index()
date_counts.columns = ['Date', 'Count']
# Convert dates to numeric format (number of days since the first date)
date_counts['Days'] = (date_counts['Date'] - date_counts['Date'][0]).dt.days
# Plotting
plt.figure(figsize=(10, 6))
# Scatter plot
plt.scatter(date_counts['Date'], date_counts['Count'], s=5, color='blue')
# LOWESS fit
lowess = sm.nonparametric.lowess(date_counts['Count'], date_counts['Days'], frac=0.1)
plt.plot(date_counts['Date'], lowess[:, 1], color='red')
plt.title('Message Frequency Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Messages')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'messages_over_time.png'))
plt.close()

## Most Active Times
df['Hour'] = df['Time'].apply(lambda x: x.hour)
df['Quarter'] = df['Date'].dt.quarter
df.groupby(['Hour', 'Quarter']).size().unstack().plot(kind='line')
plt.title('Most Active Times')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Messages')
plt.savefig(os.path.join(output_dir, 'most_active_times.png'))
plt.close()

## Conversation Starters
df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
df['Time_Diff'] = df['Datetime'].diff()
df['Conversation_Starter'] = df['Time_Diff'] > timedelta(hours=1)
conversation_starters = df[df['Conversation_Starter']]['Person'].value_counts()
conversation_starters.plot(kind='bar')
plt.title('Conversation Starters')
plt.xlabel('Person')
plt.ylabel('Number of Conversations Started')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'conversation_starters.png'))
plt.close()

## Message Length Distribution
# Calculate the message lengths
df['Message_Length'] = df['Message'].apply(len)
# Determine a sensible cutoff for the message length to avoid a long tail in the histogram
cutoff_percentile = 95
cutoff_length = np.percentile(df['Message_Length'], cutoff_percentile)
# Plotting the histogram
plt.figure(figsize=(10, 6))
df['Message_Length'].plot(kind='hist', bins=30, range=(0, cutoff_length))
plt.title('Message Length Distribution')
plt.xlabel('Message Length')
plt.ylabel('Frequency')
plt.savefig(os.path.join(output_dir, 'message_length_distribution.png'))
plt.close()

## Word Cloud
# Combine all messages into one large text
text = ' '.join(df['Message'])
# Define stopwords
# nltk.download('stopwords') # Download stopwords if not already downloaded
from nltk.corpus import stopwords
dutch_stops = set(stopwords.words('dutch'))
custom_stops = {'Media', 'weggelaten', 'youtu.be', 'youtu', 'watch', 'alleen', 'html', 'denk', 'V', 'be', 'http', 'https', 'we', 'gaan', 'zeg', 'zegt', 'zeggen', 'wel', 'even', 'gaat', 'weer', 'zien', 'komt', 'kom', 'komen', 'zal', 'mee', 'www', 'nl', 'com', 'youtube', 'goed'}
custom_stops.update(dutch_stops)  # Combine with Dutch stopwords
# Generate the word cloud
wordcloud = WordCloud(stopwords=custom_stops, width=800, height=400).generate(text)
# Display the word cloud
plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig(os.path.join(output_dir, 'wordcloud.png'))
plt.close()

## Emoji Analysis
# Define a function to extract emojis from text
def extract_emojis(s):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251"  # Enclosed characters
                           "]+", flags=re.UNICODE)
    return emoji_pattern.findall(s)

# Apply the corrected function
df['Emojis'] = df['Message'].apply(extract_emojis)

# Flatten the list of emojis and count them
all_emojis = sum(df['Emojis'], [])
emoji_counts = pd.Series(all_emojis).value_counts().head(10)

# Replace the emoji characters with their textual description in the bar chart
emoji_counts.index = [emoji.demojize(e).replace(":", "").replace("_", " ") for e in emoji_counts.index]

# Plotting top 10 emojis with descriptions
emoji_counts.plot(kind='bar', figsize=(10, 6))
plt.title('Top 10 Emojis')
# plt.xlabel('Emoji')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
# plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'top_emojis.png'), bbox_inches='tight')
plt.close()

## Sentiment analysis
df['Polarity'] = df['Message'].apply(lambda message: TextBlob(message).sentiment.polarity)
# Updated rolling window size
df['Polarity_Rolling'] = df['Polarity'].rolling(window=500, center=True).mean()

# Plotting with a timeline and only years as x-axis labels
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df.index, df['Polarity'], label='Polarity', alpha=0.5)
ax.plot(df.index, df['Polarity_Rolling'], label='Trend', color='red', linewidth=2)
ax.set_title('Sentiment Over Time')
ax.set_xlabel('Message index')
ax.set_ylabel('Sentiment Polarity')
ax.legend()
ax.grid(True)

# Set x-axis with only years
# ax.xaxis.set_major_locator(mdates.YearLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Improve y-axis with annotations
ax.annotate('Positive', xy=(0.1, 0.9), xycoords='axes fraction', color='green')
ax.annotate('Negative', xy=(0.1, 0.1), xycoords='axes fraction', color='red')

plt.savefig(os.path.join(output_dir, 'sentiment.png'), bbox_inches='tight')
plt.close()