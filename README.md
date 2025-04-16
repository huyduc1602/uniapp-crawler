# Uni-app Docs Crawler + Translator

### Tính năng:
- Crawl toàn bộ tài liệu từ https://uniapp.dcloud.io
- Dịch nội dung HTML từ tiếng Trung sang tiếng Việt qua DeepL API

### Cách sử dụng:
1. Tạo file `.env` với API key:
DEEPL_API_KEY=your_key_here
2. Build & chạy Docker:
```bash
docker-compose up --build
```
3. Kết quả:
- `data/zh/` chứa các trang HTML tiếng Trung
- `data/vi/` chứa bản dịch tiếng Việt