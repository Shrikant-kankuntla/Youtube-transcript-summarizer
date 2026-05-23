import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure Gemini API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt
prompt = """
You are an expert YouTube video summarizer.

Analyze the transcript carefully and generate:

1. A concise overall summary
2. Important key points in bullet format
3. Main lessons or takeaways
4. Important vocabulary or concepts discussed

Keep the response clean, structured, and easy to read.
"""


def extract_transcript_details(youtube_url):
    try:
        # Extract video ID
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        else:
            st.error("Invalid YouTube URL")
            return None

        ytt_api = YouTubeTranscriptApi()

        # Try multiple languages
        transcript_text = ytt_api.fetch(
            video_id,
            languages=['en', 'hi']
        )

        transcript = ""

        for i in transcript_text:
            transcript += " " + i.text

        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Function to generate summary using Gemini
def generate_summary(transcript_text, prompt):

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt + transcript_text
                }
            ],

            temperature=0.5,

            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:

        st.error(f"Groq Error: {e}")

        return None


# Streamlit UI
st.set_page_config(page_title="YouTube Summarizer")

st.title("YouTube Transcript to Detailed Summary Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")

# Display thumbnail
if youtube_link:
    try:
        if "v=" in youtube_link:
            video_id = youtube_link.split("v=")[1].split("&")[0]

            st.image(
                f"https://img.youtube.com/vi/{video_id}/0.jpg",
                use_container_width=True
            )
    except:
        pass


# Button
if st.button("Get Detailed Notes"):

    if youtube_link == "":
        st.warning("Please enter a YouTube link")

    else:
        with st.spinner("Fetching transcript and generating summary..."):

            transcript_text = extract_transcript_details(youtube_link)

            if transcript_text:

                summary = generate_summary(transcript_text, prompt)

                if summary:
                    st.markdown("## Detailed Notes")
                    st.write(summary)