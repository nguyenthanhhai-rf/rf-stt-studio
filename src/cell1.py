#@title 📦 Bước 1 — Cài đặt (chạy một lần, ~2 phút) { display-mode: "form" }

# Bắt buộc bật GPU: Runtime > Change runtime type > T4 GPU
# Ghim gradio ở major 6: bản 6 đã bỏ show_copy_button (thay bằng buttons=["copy"]),
# nên để pip tự nhảy sang major kế tiếp là mời một lỗi giao diện nữa.
!pip install -q -U "gradio>=6,<7" yt-dlp
!pip install -q faster-whisper transformers accelerate

import subprocess, gradio, torch

ff = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
print(ff.stdout.splitlines()[0] if ff.returncode == 0 else "⚠️ Không tìm thấy ffmpeg")

print("gradio", gradio.__version__)
if int(gradio.__version__.split(".")[0]) != 6:
    print("⚠️ Gradio không phải major 6 — Bước 2 nhiều khả năng sẽ lỗi tham số giao diện.")
    print("   Vào Runtime > Restart session rồi chạy lại cell này.")

if torch.cuda.is_available():
    print("✅ GPU:", torch.cuda.get_device_name(0))
else:
    print("⚠️ KHÔNG CÓ GPU — vào Runtime > Change runtime type > T4 GPU rồi chạy lại cell này.")
