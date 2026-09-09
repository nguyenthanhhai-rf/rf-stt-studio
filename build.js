const fs = require('fs');

const REPO = 'nguyenthanhhai-rf/rf-stt-studio';
const FILE = 'RF_STT_Studio.ipynb';
const COLAB = `https://colab.research.google.com/github/${REPO}/blob/main/${FILE}`;

const md = `<img src="https://img.shields.io/badge/RF-0f172a?style=for-the-badge" alt="RF">

# Bóc băng tiếng Việt

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](${COLAB})

Dán link **YouTube / TikTok / Facebook…** (hoặc tải file lên) → transcript tiếng Việt kèm \`.srt\` / \`.vtt\`.

**Cách dùng**
1. \`Runtime\` → \`Change runtime type\` → chọn **T4 GPU**.
2. Chạy **Bước 1** (cài đặt, ~2 phút).
3. Chạy **Bước 2**, bấm link \`*.gradio.live\` hiện ra.

**Chọn model**

| Model | Khi nào dùng |
|---|---|
| \`Whisper large-v3-turbo\` | Mặc định. Nhanh, dấu câu tốt, timestamp ổn định. |
| \`PhoWhisper-large\` | Giọng vùng miền nặng hoặc thu âm kém. Fine-tune trên 844h tiếng Việt. |

⚠️ **YouTube hay chặn IP của Colab.** Gặp lỗi *"Sign in to confirm you're not a bot"* thì upload \`cookies.txt\` (tiện ích trình duyệt *Get cookies.txt LOCALLY*), hoặc tải video về máy rồi dùng ô **Tải file lên**. TikTok thường không dính.

⚖️ Chỉ bóc băng nội dung bạn có quyền sử dụng.`;

const readme = `<img src="https://img.shields.io/badge/RF-0f172a?style=for-the-badge" alt="RF">

# RF · Bóc băng tiếng Việt

Công cụ Speech-to-Text tiếng Việt chạy trên Google Colab. Dán link YouTube / TikTok / Facebook (hoặc tải file lên) → nhận transcript kèm phụ đề \`.srt\` / \`.vtt\`.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](${COLAB})

> Repo private — lần đầu mở, bật **Include private repos** trong Colab:
> \`File\` → \`Open notebook\` → tab \`GitHub\` → tick ô đó rồi cấp quyền.

## Cách dùng

1. Bấm badge **Open in Colab** ở trên.
2. \`Runtime\` → \`Change runtime type\` → **T4 GPU**.
3. Chạy **Bước 1** (cài đặt, ~2 phút), rồi **Bước 2**.
4. Bấm link \`*.gradio.live\` để mở giao diện.

## Model

| Model | Khi nào dùng |
|---|---|
| \`Whisper large-v3-turbo\` | Mặc định. Nhanh, dấu câu tốt, timestamp ổn định. |
| \`PhoWhisper-large\` | Giọng vùng miền nặng hoặc thu âm kém. Fine-tune trên 844h tiếng Việt. |

Đổi model không cần khởi động lại — model cũ được giải phóng khỏi VRAM trước khi nạp model mới, vì T4 chỉ đủ chỗ cho một cái.

## Đầu ra

\`.txt\` (text thuần) · \`.srt\` · \`.vtt\` — tải trực tiếp từ giao diện.

## Giới hạn đã biết

- **YouTube chặn IP Colab.** Lỗi *"Sign in to confirm you're not a bot"* → upload \`cookies.txt\` xuất từ trình duyệt, hoặc dùng ô **Tải file lên**. TikTok thường không dính.
- Không có tách người nói (diarization) và không xử lý hàng loạt.
- Clip có nhạc nền to hoặc nhiều tiếng ồn sẽ giảm độ chính xác đáng kể.

⚖️ Chỉ dùng cho nội dung bạn có quyền sử dụng.
`;

const cell = (src, type) => ({
  cell_type: type,
  metadata: type === 'code' ? { cellView: 'form' } : {},
  source: src.replace(/\n$/, '').split('\n').map((l, i, a) => (i === a.length - 1 ? l : l + '\n')),
  ...(type === 'code' ? { execution_count: null, outputs: [] } : {}),
});

const nb = {
  nbformat: 4,
  nbformat_minor: 0,
  metadata: {
    colab: { provenance: [], toc_visible: true, name: 'RF · Bóc băng tiếng Việt' },
    kernelspec: { name: 'python3', display_name: 'Python 3' },
    language_info: { name: 'python' },
    accelerator: 'GPU',
  },
  cells: [
    cell(md, 'markdown'),
    cell(fs.readFileSync('src/cell1.py', 'utf8'), 'code'),
    cell(fs.readFileSync('src/cell2.py', 'utf8'), 'code'),
  ],
};

fs.writeFileSync(FILE, JSON.stringify(nb, null, 1), 'utf8');
fs.writeFileSync('README.md', readme, 'utf8');
console.log('OK', FILE, fs.statSync(FILE).size, 'bytes | README.md', fs.statSync('README.md').size, 'bytes');
