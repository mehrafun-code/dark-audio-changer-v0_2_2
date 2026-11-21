# Changelog

## 0.2.2
- Dub ke baad video preview + timeline: upar Original audio waveform, neeche Dub (Hindi) audio waveform
- Timeline pe click/drag se video scrub, zoom, male/female speech blocks, Dub/Original awaaz switch
- Naye API: /api/media/{job}/{dubbed|original_audio|peaks} (Range support)

## 0.2.1
- Windows .exe build (PyInstaller + GitHub Actions), launcher.py, ffmpeg bundled
- .env exe ke saath rakh sakte ho, data/ folder exe ke bagal me banta hai

## 0.2.0
- App ka naam: **Dark Audio Changer**
- Naya sci-fi UI (ember red + gold theme), DarkDeath Evil logo (transparent background) header, hero aur favicon me
- Drag & drop upload, live waveform, 6-step pipeline progress, logo ring animation sirf processing ke time
- Mobile responsive, reduced-motion support
- Download file ka naam: dark_audio_changer_hindi.mp4

## 0.1.0
- Pehla version: upload → English STT (Whisper) → gender detect (pitch) → Hindi translate (Claude/Google) → Hindi TTS (edge-tts, male/female) → merge video
- Web UI, FastAPI backend, Dockerfile, GitHub Actions build
