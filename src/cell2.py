#@title 🎙️ Bước 2 — Mở giao diện bóc băng { display-mode: "form" }

import gc, re, shutil, subprocess, unicodedata
from pathlib import Path

import gradio as gr
import torch

WORK = Path("/content/stt_work")
WORK.mkdir(parents=True, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODELS = {
    "Whisper large-v3-turbo — nhanh (mặc định)": "turbo",
    "PhoWhisper-large — chính xác hơn với giọng vùng miền": "pho",
}

_loaded = {}
COOKIES = {"path": None}


# ---------------------------------------------------------------- models
def _free_except(keep):
    """Colab T4 chỉ đủ VRAM cho một model — bỏ model cũ trước khi nạp model mới."""
    for k in list(_loaded):
        if k != keep:
            del _loaded[k]
    gc.collect()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()


def get_model(key):
    if key in _loaded:
        return _loaded[key]
    _free_except(key)
    if key == "turbo":
        from faster_whisper import WhisperModel

        _loaded[key] = WhisperModel(
            "large-v3-turbo",
            device=DEVICE,
            compute_type="float16" if DEVICE == "cuda" else "int8",
        )
    else:
        from transformers import pipeline

        _loaded[key] = pipeline(
            "automatic-speech-recognition",
            model="vinai/PhoWhisper-large",
            device=0 if DEVICE == "cuda" else -1,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            chunk_length_s=30,
            stride_length_s=5,
            return_timestamps=True,
        )
    return _loaded[key]


# ------------------------------------------------------------- tải audio
def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def safe_name(s, fallback="transcript"):
    s = unicodedata.normalize("NFC", (s or "").strip())
    s = re.sub(r"[\\/:*?\"<>|\n\r\t]+", "_", s)
    s = re.sub(r"\s+", " ", s).strip(" ._")
    return s[:80] or fallback


def fetch_audio(url):
    for f in WORK.glob("src.*"):
        f.unlink()
    title_file = WORK / "title.txt"
    title_file.unlink(missing_ok=True)

    cmd = [
        "yt-dlp", "-f", "bestaudio/best", "--no-playlist", "--force-overwrites",
        "-o", str(WORK / "src.%(ext)s"),
        "--print-to-file", "%(title)s", str(title_file),
    ]
    if COOKIES.get("path"):
        cmd += ["--cookies", COOKIES["path"]]
    cmd.append(url)

    code, out = _run(cmd)
    if code != 0:
        tail = "\n".join(out.strip().splitlines()[-12:])
        hint = ""
        low = out.lower()
        if "sign in to confirm" in low or "not a bot" in low or "cookies" in low:
            hint = (
                "\n\n👉 YouTube đang chặn IP của Colab. Cách xử lý: cài tiện ích "
                "'Get cookies.txt LOCALLY' trên trình duyệt, xuất cookies của youtube.com, "
                "rồi upload file đó vào ô Cookies. Hoặc đơn giản hơn: tải video về máy "
                "rồi dùng ô 'Tải file lên'."
            )
        raise gr.Error("yt-dlp thất bại:\n" + tail + hint)

    found = list(WORK.glob("src.*"))
    if not found:
        raise gr.Error("yt-dlp báo thành công nhưng không thấy file audio nào.")
    title = title_file.read_text(encoding="utf-8").strip() if title_file.exists() else ""
    return found[0], safe_name(title)


def to_wav(src):
    wav = WORK / "audio16k.wav"
    wav.unlink(missing_ok=True)
    code, out = _run([
        "ffmpeg", "-y", "-i", str(src), "-vn",
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav),
    ])
    if code != 0 or not wav.exists():
        tail = "\n".join(out.strip().splitlines()[-10:])
        raise gr.Error("ffmpeg không chuyển được audio:\n" + tail)
    return wav


# -------------------------------------------------------------- bóc băng
def transcribe(wav, key):
    model = get_model(key)
    segs = []

    if key == "turbo":
        # vad_filter cắt khoảng lặng; condition_on_previous_text=False chống lặp câu
        it, _info = model.transcribe(
            str(wav),
            language="vi",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            condition_on_previous_text=False,
        )
        for s in it:
            t = s.text.strip()
            if t:
                segs.append({"start": s.start, "end": s.end, "text": t})
    else:
        out = model(str(wav))
        chunks = out.get("chunks") or []
        if not chunks:
            t = (out.get("text") or "").strip()
            return [{"start": 0.0, "end": 0.0, "text": t}] if t else []
        prev = 0.0
        for c in chunks:
            t = (c.get("text") or "").strip()
            if not t:
                continue
            ts = c.get("timestamp") or (None, None)
            st = float(ts[0]) if ts[0] is not None else prev
            en = float(ts[1]) if ts[1] is not None else st + 3.0
            segs.append({"start": st, "end": en, "text": t})
            prev = en
    return segs


# ------------------------------------------------------------- xuất file
def _ts(sec, comma=True):
    total = max(0, int(round(float(sec) * 1000)))
    h, total = divmod(total, 3600000)
    m, total = divmod(total, 60000)
    s, ms = divmod(total, 1000)
    sep = "," if comma else "."
    return "%02d:%02d:%02d%s%03d" % (h, m, s, sep, ms)


def to_srt(segs):
    out = []
    for i, s in enumerate(segs, 1):
        out.append("%d\n%s --> %s\n%s\n" % (i, _ts(s["start"]), _ts(s["end"]), s["text"]))
    return "\n".join(out)


def to_vtt(segs):
    lines = ["WEBVTT", ""]
    for s in segs:
        lines.append("%s --> %s" % (_ts(s["start"], False), _ts(s["end"], False)))
        lines.append(s["text"])
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------ chạy
def set_cookies(path):
    COOKIES["path"] = path
    return "🍪 Đã nạp cookies." if path else ""


def run(url, upload, model_label, progress=gr.Progress()):
    key = MODELS[model_label]
    url = (url or "").strip()
    if not url and not upload:
        raise gr.Error("Dán một link, hoặc tải lên file audio/video.")

    if upload:
        src, name = Path(upload), safe_name(Path(upload).stem)
    else:
        progress(0.10, desc="Đang tải audio…")
        src, name = fetch_audio(url)

    progress(0.30, desc="Đang chuẩn hoá audio về 16kHz…")
    wav = to_wav(src)

    short = model_label.split(" —")[0]
    progress(0.45, desc="Đang bóc băng bằng " + short + "… (lần đầu phải tải model về)")
    segs = transcribe(wav, key)
    if not segs:
        raise gr.Error("Không nhận ra lời thoại nào — audio có thể chỉ có nhạc hoặc im lặng.")

    progress(0.95, desc="Đang xuất file…")
    outdir = WORK / "out"
    shutil.rmtree(outdir, ignore_errors=True)
    outdir.mkdir(parents=True)

    text = "\n".join(s["text"] for s in segs)
    paths = []
    for ext, content in (("txt", text), ("srt", to_srt(segs)), ("vtt", to_vtt(segs))):
        p = outdir / (name + "." + ext)
        p.write_text(content, encoding="utf-8")
        paths.append(str(p))

    mins = segs[-1]["end"] / 60
    status = "✅ **%d đoạn · ~%.1f phút** · %s" % (len(segs), mins, short)
    return text, paths, status


# -------------------------------------------------------------------- UI
HEADER = """
<div style="display:flex;align-items:center;gap:14px;padding:2px 0 10px">
  <div style="width:46px;height:46px;border-radius:11px;background:#0f172a;color:#fff;
              display:flex;align-items:center;justify-content:center;flex:none;
              font-weight:700;font-size:19px;letter-spacing:1px;font-family:system-ui">RF</div>
  <div style="min-width:0">
    <div style="font-size:20px;font-weight:650;line-height:1.25">Bóc băng tiếng Việt</div>
    <div style="opacity:.6;font-size:13px;line-height:1.4">
      Dán link YouTube / TikTok / Facebook, hoặc tải file lên · xuất .txt .srt .vtt
    </div>
  </div>
</div>
"""

with gr.Blocks(title="RF · Bóc băng tiếng Việt") as demo:
    gr.HTML(HEADER)
    with gr.Row():
        with gr.Column(scale=3):
            url = gr.Textbox(label="Link video", placeholder="https://www.youtube.com/watch?v=…")
            upload = gr.File(label="…hoặc tải file audio/video lên (ưu tiên hơn link)", type="filepath")
            model = gr.Radio(list(MODELS), value=list(MODELS)[0], label="Model")
            btn = gr.Button("Bóc băng", variant="primary")
            with gr.Accordion("Cookies — chỉ mở khi YouTube chặn", open=False):
                cookies = gr.File(label="cookies.txt", type="filepath", file_types=[".txt"])
                cookie_msg = gr.Markdown()
        with gr.Column(scale=4):
            status = gr.Markdown()
            text = gr.Textbox(label="Transcript", lines=22, buttons=["copy"])
            files = gr.Files(label="Tải về")

    cookies.change(set_cookies, cookies, cookie_msg)
    btn.click(run, [url, upload, model], [text, files, status])

demo.launch(share=True)
