import shutil
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .pipeline import process

app = FastAPI(title="Dark Audio Changer", version=config.VERSION)
JOBS: dict[str, dict] = {}
STATIC = Path(__file__).parent / "static"


def _work(job_id: str, video: Path):
    def progress(msg, pct):
        JOBS[job_id].update(status="processing", message=msg, progress=pct)
    try:
        out, segs = process(video, config.DATA_DIR / job_id, progress)
        JOBS[job_id].update(status="done", output=str(out), segments=segs, progress=100)
    except Exception as e:
        JOBS[job_id].update(status="error", message=str(e))


@app.get("/api/version")
def version():
    return {"version": config.VERSION}


@app.post("/api/dub")
async def dub(bg: BackgroundTasks, file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:12]
    folder = config.DATA_DIR / job_id
    folder.mkdir(parents=True, exist_ok=True)
    video = folder / ("input" + Path(file.filename or "v.mp4").suffix)
    with open(video, "wb") as f:
        shutil.copyfileobj(file.file, f)
    JOBS[job_id] = {"status": "queued", "message": "Queue me hai", "progress": 0}
    bg.add_task(_work, job_id, video)
    return {"job_id": job_id}


@app.get("/api/status/{job_id}")
def status(job_id: str):
    j = JOBS.get(job_id)
    if not j:
        raise HTTPException(404, "Job nahi mila")
    return {k: v for k, v in j.items() if k != "output"}


@app.get("/api/download/{job_id}")
def download(job_id: str):
    j = JOBS.get(job_id)
    if not j or j.get("status") != "done":
        raise HTTPException(404, "Abhi ready nahi")
    return FileResponse(j["output"], media_type="video/mp4", filename="dark_audio_changer_hindi.mp4")


MEDIA = {
    "dubbed": ("output.mp4", "video/mp4"),
    "original_audio": ("audio.wav", "audio/wav"),
    "peaks": ("peaks.json", "application/json"),
}


def _ranged(path: Path, request: Request, media_type: str):
    """Range support, taaki browser video me aage-peeche seek kar sake."""
    size = path.stat().st_size
    start, end, code = 0, size - 1, 200
    rng = request.headers.get("range", "")
    if rng.startswith("bytes="):
        try:
            a, _, b = rng[6:].split(",")[0].partition("-")
            if a:
                start = int(a)
                end = int(b) if b else size - 1
            else:
                start = max(size - int(b), 0)
            end = min(end, size - 1)
            if start > end:
                raise ValueError
            code = 206
        except ValueError:
            raise HTTPException(416, "Bad range")

    def chunks():
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                data = f.read(min(1 << 20, left))
                if not data:
                    break
                left -= len(data)
                yield data

    headers = {"Accept-Ranges": "bytes", "Content-Length": str(end - start + 1)}
    if code == 206:
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    return StreamingResponse(chunks(), status_code=code, media_type=media_type, headers=headers)


@app.get("/api/media/{job_id}/{kind}")
def media(job_id: str, kind: str, request: Request):
    j = JOBS.get(job_id)
    if not j or j.get("status") != "done" or kind not in MEDIA:
        raise HTTPException(404, "Nahi mila")
    name, mt = MEDIA[kind]
    path = config.DATA_DIR / job_id / name
    if not path.exists():
        raise HTTPException(404, "File nahi mili")
    return _ranged(path, request, mt)


app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
