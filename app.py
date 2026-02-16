import os
from uuid import uuid4
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.google import Gemini
from agno.tools.firecrawl import FirecrawlTools
from elevenlabs import ElevenLabs
import streamlit as st


# streamlit initialization
st.set_page_config(page_title="Blog to Podcast", page_icon="🎙️")
st.title("Blog to Podcast Agent")


st.sidebar.header("API Keys")
gemini_api_key = st.sidebar.text_input("Gemini API Key",type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type='password')
firecrawl_api_key = st.sidebar.text_input("Firecrawl API Key", type="password")

# blog url input
url = st.text_input("Enter Blog URL:", "")

# Generate pdocast Button
if st.button("Generate Podcast", disabled=not all([gemini_api_key, elevenlabs_api_key, firecrawl_api_key])):
    if not url.strip():
        st.warning("Please enter a valid blog url")

    else:
        with st.spinner("Scrapping blog and generating podcast..."):
            try:
                # set api keys
                os.environ['GEMINI_API_KEY'] = gemini_api_key
                os.environ['FIRECRAWL_API_KEY'] = firecrawl_api_key

                # create agent for scrapping and summmarization
                agent = Agent(
                    name="Blog Summarizer",
                    model = Gemini(id="gemini-2.5-flash-lite"),
                    tools = [FirecrawlTools()],
                    instructions = [
                        "Scrape the blog URL and create a concise, engaging summary (max 2000 characters) suitable for a podcast."
                        "The summary should be conversational and capture the main points."

                    ],


                )

                # Get Summary
                response: RunOutput = agent.run(f"Scrape and summarize this blog for a podcast: {url}")
                summary = response.content if hasattr(response, 'content') else str(response)

                if summary:
                    # initialize elevenlabs client and generate audio
                    client = ElevenLabs(api_key=elevenlabs_api_key)

                    # generate audio using text_to_speech.convert
                    audio_generator = client.text_to_speech.convert(
                        text=summary,
                        voice_id = "026EzMcc9lUpArery1x2",
                        model_id ="eleven_multilingual_v2"
                    )

                    # collect audio chunks if it  is generated
                    audio_chunks =[]
                    for chunk in audio_generator:
                        if chunk:
                            audio_chunks.append(chunk)
                    audio_bytes = b"".join(audio_chunks)

                    # download button
                    st.download_button(
                        "Download Podcast",
                        audio_bytes,
                        "podcast.mp3",
                        "audio/mp3"
                    )

                    # show summary
                    with st.expander(" Podcast Summary"):
                        st.write(summary)

                else:
                    st.error("Failed to generate summary")

            except Exception as e:
                st.error(f"Error: {e}")