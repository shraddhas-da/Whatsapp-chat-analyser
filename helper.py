from urlextract import URLExtract
import emoji
from collections import Counter
from wordcloud import WordCloud
extract = URLExtract()
from collections import Counter
import pandas as pd


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Number of messages
    num_messages = df.shape[0]

    # Number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Number of media messages
    num_media_messages = df[df['message'].str.contains('<Media omitted>', na=False)].shape[0]

    # Links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    # Emojis
    emojis = []
    for message in df['message']:
        for char in message:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)

    # Top 100 emojis (WhatsApp-style array)
    emoji_freq = Counter(emojis).most_common(100)
    top_emojis = [e for e, _ in emoji_freq]

    return num_messages, len(words), num_media_messages, len(links), links, len(emojis), top_emojis


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df=(round(df['user'].value_counts() / df.shape[0] * 100, 2)
        .reset_index()
        .rename(columns={'index': 'name', 'user': 'percent'}))
    return x, df


from wordcloud import WordCloud

def create_word_cloud(selected_user, df):
    # Load stopwords
    with open("stop_hinglish.txt", "r") as f:
        stop_words = f.read().split()

    # Filter by user if needed
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove system messages, media placeholders, and deleted messages
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]
    temp = temp[~temp['message'].str.contains('This message was deleted', na=False)]

    # Build clean word list
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if (
                word not in stop_words
                and not word.startswith("<")   # removes <media, <this, etc.
                and not word.endswith(">")     # removes omitted>, edited>, deleted>
            ):
                words.append(word)

    # Generate word cloud from cleaned words
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    wc_img = wc.generate(" ".join(words))
    return wc_img

def most_common_words(selected_user, df):
    # Load stopwords
    with open("stop_hinglish.txt", "r") as f:
        stop_words = f.read().split()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove system messages and media placeholders
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if (
                word not in stop_words
                and word not in ["<media", "omitted>", "<this", "edited>"]
            ):
                words.append(word)

    most_common_df = pd.DataFrame(
        Counter(words).most_common(50), columns=["word", "count"]
    )
    return most_common_df

# Emojis

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove system messages, media placeholders, and deleted messages
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]
    temp = temp[~temp['message'].str.contains('This message was deleted', na=False)]

    emojis = []
    for message in temp['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    # Build DataFrame with proper column names
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))),
                            columns=['emoji', 'count'])
    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time']=time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('date_').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap= df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
