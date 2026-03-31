import streamlit as st
import preprocessor
import helper
import emoji
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import zipfile
import io
import matplotlib as mpl

# Set page config for better layout
st.set_page_config(layout="wide")

st.sidebar.title('WhatsApp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader('Choose a file')

if uploaded_file is not None:
    # Check if uploaded file is a zip
    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue()), "r") as z:
            # WhatsApp exports usually contain one .txt file
            txt_files = [f for f in z.namelist() if f.endswith(".txt")]
            if txt_files:
                data = z.read(txt_files[0]).decode("utf-8")
            else:
                st.error("No .txt file found inside the zip.")
                st.stop()
    else:
        # Normal text file
        data = uploaded_file.getvalue().decode("utf-8")

    # Preprocess into DataFrame
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, 'Overall')

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    # Sidebar trigger
    if st.sidebar.button("Show Analysis"):
        try:
            # Stats Fetching
            num_messages, words, num_media_messages, num_links, links, num_emojis, top_emojis = helper.fetch_stats(
                selected_user, df)

            st.title('Top Statistics')
            # Create 4 columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Messages", num_messages)

            with col2:
                st.metric("Total Words", words)

            with col3:
                st.metric("Media Shared", num_media_messages)

            with col4:
                emoji_df = helper.emoji_helper(selected_user, df)
                total_emojis = emoji_df['count'].sum() if not emoji_df.empty else 0
                st.metric("Emojis Used", total_emojis)

            # Links below stats
            st.write(f"**Links Shared:** {num_links}")

            # Convert links list into a dataset
            links_df = pd.DataFrame(links, columns=["Link"])
            with st.expander("Show All Links"):
                st.dataframe(links_df)

            # Monthly Timeline
            st.title('Monthly Timeline')
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='#F52780')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Daily Timeline
            st.title('Daily Timeline')
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['date_'], daily_timeline['message'], color='#128012')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Activity Map
            st.title('Activity Map')
            col1, col2 = st.columns(2)
            with col1:
                st.header("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='#F52780')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='#1142F5')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title('Weekly Activity Map')
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(user_heatmap, annot=False, fmt=".1f", cmap="YlOrRd", ax=ax)
            st.pyplot(fig)

            # Finding the busiest users (group level)
            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                col1, col2 = st.columns(2)
                with col1:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='#F527D6')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # WordCloud
            st.title('Wordcloud')
            df_wc = helper.create_word_cloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # Most Common Words
            st.title('Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 9))
            ax.barh(most_common_df['word'], most_common_df['count'], color='#9F27F5')
            plt.xticks(rotation='vertical')
            plt.tight_layout(pad=2.0)
            st.pyplot(fig)

            # Emoji Analysis (Fixed location and indentation)
            emoji_df = helper.emoji_helper(selected_user, df)
            st.title('Emojis Analysis')
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                # Set emoji-compatible font
                mpl.rcParams['font.family'] = 'Segoe UI Emoji'
               
                fig, ax = plt.subplots()

                ax.pie(
                    emoji_df['count'],
                    labels=emoji_df['emoji'],
                    autopct='%1.1f%%',
                    textprops={'fontsize': 14}
                )
                st.pyplot(fig)

        except ModuleNotFoundError as e:
            st.error(f"Missing Library Error: {e}. Please ensure 'urlextract' is in requirements.txt")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
