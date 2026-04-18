import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import tempfile
import os
import json
import time
import zipfile
from datetime import timedelta

st.set_page_config(page_title="AttentionX - AI Content Repurposing", layout="wide")
st.title("🚀 AttentionX AI Hackathon")
st.subheader("Automated Content Repurposing Engine")
st.caption("Upload a long video → Get 5–8 ready-to-post vertical Reels/TikToks with smart crop + dynamic captions")

# Sidebar
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", value="", placeholder="Paste your key here")
st.sidebar.markdown("[Get free API key →](https://aistudio.google.com/app/apikey)")
st.sidebar.info("Use a short video (3-15 min) for fast demo. Longer videos work but take more time.")

if not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to continue.")
    st.stop()

genai.configure(api_key=api_key)

# Upload
uploaded_file = st.file_uploader("Upload long-form video (MP4)", type=["mp4", "mov"])

if uploaded_file:
    # Save uploaded video temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded_file.getbuffer())
        video_path = tmp.name

    st.video(uploaded_file)

    if st.button("🔥 Generate Viral Shorts", type="primary", use_container_width=True):
        with st.spinner("1/3 Uploading video to Gemini..."):
            video_file = genai.upload_file(path=video_path)
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(5)
                video_file = genai.get_file(video_file.name)

        with st.spinner("2/3 Analyzing emotional peaks & generating captions..."):
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = """
            You are an expert short-form content editor.
            Analyze the entire video and return ONLY valid JSON (no extra text).
            Find 5-8 high-energy "emotional peaks" (best 60-second moments).
            For each clip return:
            - start: start time in seconds (integer)
            - end: end time in seconds (integer)
            - hook: catchy 1-line headline (max 8 words)
            - captions: array of timed karaoke-style captions (each caption max 6-8 words)

            Example output format:
            {
              "clips": [
                {
                  "start": 45,
                  "end": 105,
                  "hook": "The mindset shift that changed everything",
                  "captions": [
                    {"start": 0, "end": 4, "text": "Wait for this..."},
                    {"start": 4, "end": 9, "text": "This one change..."},
                    ...
                  ]
                }
              ]
            }

            Make captions punchy, high-contrast style perfect for Reels/TikTok.
            """
            response = model.generate_content([video_file, prompt])
            
            try:
                result = json.loads(response.text.strip().strip("```json").strip("```"))
            except:
                st.error("Gemini did not return valid JSON. Try again or use a different video.")
                st.stop()

        clips_data = result.get("clips", [])

        with st.spinner("3/3 Creating vertical shorts with captions..."):
            output_clips = []
            progress_bar = st.progress(0)

            for i, clip_info in enumerate(clips_data):
                start = clip_info["start"]
                end = clip_info["end"]
                hook = clip_info["hook"]
                captions = clip_info.get("captions", [])

                # Cut original clip
                clip = VideoFileClip(video_path).subclip(start, end)

                # Smart-Crop to Vertical 9:16 (center crop for MVP)
                w, h = clip.size
                target_w = int(h * 9 / 16)
                if target_w < w:
                    x1 = (w - target_w) // 2
                    clip = clip.crop(x1=x1, x2=x1 + target_w)

                # Add Hook title (big text at top for first 3 seconds)
                if hook:
                    title_clip = TextClip(hook, fontsize=60, color='white', bg_color='black', stroke_color='yellow', stroke_width=3, font='Arial-Bold')
                    title_clip = title_clip.set_position(('center', 50)).set_duration(3)
                    clip = CompositeVideoClip([clip, title_clip])

                # Add karaoke-style captions
                caption_clips = []
                for cap in captions:
                    txt_clip = TextClip(cap["text"], fontsize=50, color='white', bg_color='rgba(0,0,0,0.7)', stroke_color='black', stroke_width=2, font='Arial-Bold')
                    txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(cap["start"]).set_duration(cap["end"] - cap["start"])
                    caption_clips.append(txt_clip)

                if caption_clips:
                    final_clip = CompositeVideoClip([clip] + caption_clips)
                else:
                    final_clip = clip

                # Save clip
                output_path = f"short_{i+1}_{int(start)}_{int(end)}.mp4"
                final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", threads=4, preset="fast")
                output_clips.append(output_path)
                progress_bar.progress((i + 1) / len(clips_data))

            # Create ZIP
            zip_path = "attentionx_viral_shorts.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in output_clips:
                    zipf.write(file)
                    os.remove(file)  # clean up individual files

            st.success("✅ Done! Here are your viral shorts")
            st.download_button("📥 Download All Shorts (ZIP)", data=open(zip_path, "rb"), file_name=zip_path, mime="application/zip")

            # Show first clip as preview
            if output_clips:
                st.video(output_clips[0])

            # Cleanup
            os.remove(video_path)
            if os.path.exists(zip_path):
                os.remove(zip_path)  