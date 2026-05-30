from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

def get_transcript(url):
    if "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("URL ไม่ถูกต้อง")

    ytt = YouTubeTranscriptApi()

    try:
        # ลอง manual transcript ก่อน
        fetched = ytt.fetch(video_id, languages=["en", "th"])
    except Exception:
        # ถ้าไม่มีให้ดึง auto-generated แทน
        transcript_list = ytt.list(video_id)
        fetched = transcript_list.find_generated_transcript(["th", "en"]).fetch()

    full_text = " ".join([t.text for t in fetched])
    return full_text

def summarize(transcript):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(f"""สรุปเนื้อหาจาก YouTube video นี้เป็นภาษาไทย
ให้สรุปเป็นข้อๆ ชัดเจน ครอบคลุมประเด็นหลักทั้งหมด

transcript:
{transcript[:4000]}""")

    return response.text

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("วิธีใช้: python main.py <YouTube URL>")
        print("ตัวอย่าง: python main.py https://www.youtube.com/watch?v=aircAruvnKk")
        sys.exit(1)

    url = sys.argv[1]
    print(f"กำลังดึง transcript จาก: {url}")
    transcript = get_transcript(url)

    print("กำลังสรุปด้วย AI...")
    summary = summarize(transcript)

    print("\n===== สรุปเนื้อหา =====")
    print(summary)

    # บันทึกผลเป็นไฟล์
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n\n")
        f.write(summary)
    print("\nบันทึกผลลงไฟล์ summary.txt แล้ว")