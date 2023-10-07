import streamlit as st
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# Create a function to fetch comments from the YouTube video
def fetch_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100  # Adjust as needed
    )

    while request:
        response = request.execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        
        request = youtube.commentThreads().list_next(request, response)
    
    return comments

# Create a Streamlit app
def main():
    st.title("YouTube Comment Word Cloud Generator")

    # Input fields for Video ID and API Key
    video_id = st.text_input("Enter YouTube Video ID:")
    api_key = st.text_input("Enter YouTube Data API Key:")

    # Customization options
    st.sidebar.subheader("Word Cloud Customization")
    font = st.sidebar.selectbox("Font", ["serif", "sans-serif", "monospace"])
    font_size = st.sidebar.slider("Font Size", min_value=10, max_value=100, value=40)
    background_color = st.sidebar.color_picker("Background Color", "#ffffff")
    wordcloud_color = st.sidebar.color_picker("Word Cloud Color", "#000000")
    
    if st.button("Generate Word Cloud"):
        if not video_id or not api_key:
            st.error("Please enter a valid Video ID and API Key.")
        else:
            st.info("Fetching comments...")

            try:
                comments = fetch_comments(api_key, video_id)
                
                if comments:
                    comment_text = ' '.join(comments)
                    
                    # Generate the word cloud with customization options
                    wordcloud = WordCloud(
                        width=800,
                        height=400,
                        background_color=background_color,
                        colormap=wordcloud_color,
                        font_path=None if font == "sans-serif" else font,
                        font_step=font_size,
                    ).generate(comment_text)
                    
                    # Display the word cloud
                    st.image(wordcloud.to_array(), use_container_width=True)

                    # Option to save the word cloud as an image
                    save_button = st.button("Save Word Cloud")
                    if save_button:
                        buffer = io.BytesIO()
                        plt.figure(figsize=(8, 4))
                        plt.imshow(wordcloud, interpolation="bilinear")
                        plt.axis("off")
                        plt.savefig(buffer, format="png")
                        st.markdown(
                            f"### [Download Word Cloud](data:application/octet-stream;base64,{base64.b64encode(buffer.getvalue()).decode()})"
                        )

                else:
                    st.warning("No comments found for this video.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
