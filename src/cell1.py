#@title 📦 Bước 1 — Cài đặt (chạy một lần, ~2 phút) { display-mode: "form" }

# Bắt buộc bật GPU: Runtime > Change runtime type > T4 GPU
# -U là bắt buộc với gradio: Colab cài sẵn bản cũ, thiếu -U thì pip lặng lẽ bỏ qua.
!pip install -q -U gradio yt-dlp
!pip install -q faster-whisper transformers accelerate

import subprocess, gradio, torch

ff = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
print(ff.stdout.splitlines()[0] if ff.returncode == 0 else "⚠️ Không tìm thấy ffmpeg")

print("gradio", gradio.__version__)
if int(gradio.__version__.split(".")[0]) < 4:
    print("⚠️ Gradio quá cũ. Vào Runtime > Restart session rồi chạy lại cell này.")

if torch.cuda.is_available():
    print("✅ GPU:", torch.cuda.get_device_name(0))
else:
    print("⚠️ KHÔNG CÓ GPU — vào Runtime > Change runtime type > T4 GPU rồi chạy lại cell này.")
