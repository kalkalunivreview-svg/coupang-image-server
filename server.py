from flask import Flask, send_file, make_response
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, timezone
import io
import os

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))

app = Flask(__name__)


def no_cache_response(img_io):
    """캐시 방지 헤더가 포함된 응답 생성"""
    response = make_response(send_file(img_io, mimetype="image/png"))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

# 설정
IMAGE_PATH = "image_1.png"
FONT_PATH = "Pretendard-Bold.otf"
FONT_SIZE = 62

# 날짜 텍스트 위치 (피그마 좌표 계산 결과)
TEXT_X = 164 + 25  # 텍스트 박스 시작 X (오른쪽으로 25px)
TEXT_Y = 129 - 15  # 텍스트 박스 시작 Y (위로 15px)
TEXT_BOX_WIDTH = 401  # 텍스트 박스 너비
TEXT_COLOR = (255, 59, 48)  # 빨간색


def get_today_text():
    """오늘 날짜를 '12월 9일' 형식으로 반환 (한국 시간 기준)"""
    today = datetime.now(KST)
    return f"{today.month}월 {today.day}일"


def generate_image():
    """날짜가 삽입된 이미지 생성"""
    # 원본 이미지 열기
    img = Image.open(IMAGE_PATH)
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    
    # 오늘 날짜 텍스트
    date_text = get_today_text()
    
    # 텍스트 크기 계산 (가운데 정렬용)
    bbox = draw.textbbox((0, 0), date_text, font=font)
    text_width = bbox[2] - bbox[0]
    
    # 텍스트 박스 내 가운데 정렬
    x = TEXT_X + (TEXT_BOX_WIDTH - text_width) // 2
    y = TEXT_Y
    
    # 텍스트 그리기 (빨간색)
    draw.text((x, y), date_text, font=font, fill=TEXT_COLOR)
    
    return img


@app.route("/")
def serve_image():
    """이미지를 PNG로 서빙 (캐시 방지)"""
    img = generate_image()

    # 메모리에 PNG로 저장
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return no_cache_response(img_io)


@app.route("/download")
def download_image():
    """이미지 다운로드"""
    img = generate_image()
    
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    
    today = datetime.now(KST)
    filename = f"event_{today.month}_{today.day}.png"
    
    return send_file(img_io, mimetype="image/png", as_attachment=True, download_name=filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 서버 시작: http://localhost:{port}")
    print("📷 이미지 보기: /")
    print("⬇️  다운로드: /download")
    app.run(host="0.0.0.0", port=port)

