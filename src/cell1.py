#@title 📦 Bước 1 — Cài đặt (chạy một lần, ~2 phút) { display-mode: "form" }

# Bắt buộc bật GPU: Runtime > Change runtime type > T4 GPU
!pip install -q -U yt-dlp
!pip install -q faster-whisper gradio transformers accelerate

import subprocess, torch

ff = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
print(ff.stdout.splitlines()[0] if ff.returncode == 0 else "⚠️ Không tìm thấy ffmpeg")

if torch.cuda.is_available():
    print("✅ GPU:", torch.cuda.get_device_name(0))
else:
    print("⚠️ KHÔNG CÓ GPU — vào Runtime > Change runtime type > T4 GPU rồi chạy lại cell này.")
