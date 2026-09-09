<img src="https://img.shields.io/badge/RF-0f172a?style=for-the-badge" alt="RF">

# RF · Bóc băng tiếng Việt

Công cụ Speech-to-Text tiếng Việt chạy trên Google Colab. Dán link YouTube / TikTok / Facebook (hoặc tải file lên) → nhận transcript kèm phụ đề `.srt` / `.vtt`.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nguyenthanhhai-rf/rf-stt-studio/blob/main/RF_STT_Studio.ipynb)

> Repo private — lần đầu mở, bật **Include private repos** trong Colab:
> `File` → `Open notebook` → tab `GitHub` → tick ô đó rồi cấp quyền.

## Cách dùng

1. Bấm badge **Open in Colab** ở trên.
2. `Runtime` → `Change runtime type` → **T4 GPU**.
3. Chạy **Bước 1** (cài đặt, ~2 phút), rồi **Bước 2**.
4. Bấm link `*.gradio.live` để mở giao diện.

## Model

| Model | Khi nào dùng |
|---|---|
| `Whisper large-v3-turbo` | Mặc định. Nhanh, dấu câu tốt, timestamp ổn định. |
| `PhoWhisper-large` | Giọng vùng miền nặng hoặc thu âm kém. Fine-tune trên 844h tiếng Việt. |

Đổi model không cần khởi động lại — model cũ được giải phóng khỏi VRAM trước khi nạp model mới, vì T4 chỉ đủ chỗ cho một cái.

## Đầu ra

`.txt` (text thuần) · `.srt` · `.vtt` — tải trực tiếp từ giao diện.

## Giới hạn đã biết

- **YouTube chặn IP Colab.** Lỗi *"Sign in to confirm you're not a bot"* → upload `cookies.txt` xuất từ trình duyệt, hoặc dùng ô **Tải file lên**. TikTok thường không dính.
- Không có tách người nói (diarization) và không xử lý hàng loạt.
- Clip có nhạc nền to hoặc nhiều tiếng ồn sẽ giảm độ chính xác đáng kể.

⚖️ Chỉ dùng cho nội dung bạn có quyền sử dụng.
