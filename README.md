AttentionX - Automated Content Repurposing Engine

Hackathon Submission - AttentionX AI Hackathon 

What it does
- Upload any long video
- Gemini 1.5 Flash finds emotional peaks
- Automatically creates 5–8 vertical (9:16) shorts
- Adds catchy hook + timed karaoke-style captions
- Downloads ready-to-post Reels/TikTok clips

How to run (local)
1. `pip install -r requirements.txt`
2. Install **ffmpeg** (required by MoviePy):
   - Windows: https://www.gyan.dev/ffmpeg/builds/
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. `streamlit run app.py`

Demo Video
(Record your screen while using the app and put the Google Drive link here)

Tech Stack
- Google Gemini 1.5 Flash (video analysis)
- MoviePy (video editing + captions)
- Streamlit (UI)
- Center-crop smart vertical conversion (full MediaPipe face tracking possible in v2)

Built in one evening for the hackathon. Fully working prototype.
