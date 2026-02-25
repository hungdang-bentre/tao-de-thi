import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Cau hinh trang
st.set_page_config(page_title="AI Exam Pro", page_icon="⚛️", layout="wide")

# 2. Trang tri bang CSS
st.markdown("""
<style>
.main-header { font-size: 38px; color: #1E3A8A; font-weight: 800; text-align: center; margin-bottom: 5px; }
.sub-header { font-size: 18px; color: #0284c7; text-align: center; margin-bottom: 30px; font-style: italic; }
div.stButton > button:first-child { background-color: #2563EB; color: white; border-radius: 8px; font-weight: bold; padding: 10px; width: 100%; transition: all 0.3s ease; }
div.stButton > button:first-child:hover { background-color: #1D4ED8; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# 3. Khoi tao ket noi AI
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Su dung ban latest de khong bi loi 404
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình.")
    st.stop()

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Chọn độ khó cho đề mới:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.info("💡 Cập nhật mới: Gửi trực tiếp nguyên bản file PDF cho AI. Đảm bảo giữ nguyên vẹn 100% công thức Toán (tích phân, ma trận, vectơ...).")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán học & Vật lý</div>', unsafe_allow_html=True)

def get_prompt(level):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên về Toán học và Vật lý.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
    PHẦN 2: Tạo đề thi mới với độ khó: {level}.
    Dựa vào file PDF, văn bản hoặc hình ảnh được cung cấp, hãy thay đổi các số liệu, phương trình, toạ độ, hệ vectơ nhưng giữ nguyên bản chất.
    Bắt buộc trình bày các công thức toán học, ký hiệu vectơ bằng chuẩn LaTeX tuyệt đẹp.
    """

# 6. Giao dien chinh chia 2 cot
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📥 Đầu vào (Tài liệu gốc)")
    
    # AI se doc truc tiep file PDF nay
    pdf_file = st.file_uploader("1. Tải file PDF trực tiếp (Khuyên dùng để giữ nguyên công thức):", type=["pdf"])
            
    existing_text = st.text_area("2. Nội dung văn bản bổ sung (Tự gõ hoặc Copy/Paste):", height=150)
    
    img_file = st.file_uploader("3. Tải lên hoặc dán (Ctrl+V) ảnh hình học/đồ thị bổ sung:", type=["png", "jpg", "jpeg"])
    if img_file is not None:
        image = Image.open(img_file)
        st.image(image, caption="Ảnh đính kèm", width=250)
        
    btn_generate = st.button("🚀 AI Đọc Dữ liệu & Tạo Đề Mới", key="btn_gen")

with col2:
    st.markdown("### 📤 Kết quả (AI Sinh ra)")
    if btn_generate:
        if not existing_text.strip() and img_file is None and pdf_file is None:
            st.warning("⚠️ Vui lòng cung cấp ít nhất 1 loại dữ liệu (PDF, Văn bản, hoặc Ảnh)!")
        else:
            with st.spinner("🔬 AI đang đọc trực tiếp dữ liệu gốc và suy luận logic..."):
                try:
                    contents_to_send = [get_prompt(difficulty)]
                    
                    if pdf_file is not None:
                        contents_to_send.append({
                            "mime_type": "application/pdf",
                            "data": pdf_file.getvalue()
                        })
                    
                    if existing_text.strip():
                        contents_to_send.append(f"Văn bản bổ sung:\n{existing_text}")
                        
                    if img_file is not None:
                        contents_to_send.append(image)

                    response = model.generate_content(contents_to_send)
                    
                    if "TỪ_CHỐI_MÔN_HỌC" in response.text:
                        st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ phân tích môn Toán và Vật lý!")
                    else:
                        st.success("✅ Đã tạo thành công!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
