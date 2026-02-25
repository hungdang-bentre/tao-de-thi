import streamlit as st
import google.generativeai as genai

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
    # Su dung ban latest de dam bao luon chay on dinh
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình.")
    st.stop()

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Chọn độ khó cho đề mới:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.info("💡 Chế độ: Nhập văn bản thuần túy. Rất ổn định, phù hợp khi bạn copy đề từ file Word hoặc gõ trực tiếp.")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán học & Vật lý (Chế độ Văn bản)</div>', unsafe_allow_html=True)

def get_prompt(level, text_input):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên về Toán học và Vật lý.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
    PHẦN 2: Tạo đề thi mới với độ khó: {level}.
    Dựa vào văn bản đề thi gốc dưới đây, hãy thay đổi các số liệu, phương trình, toạ độ, biến số nhưng giữ nguyên bản chất và cấu trúc bài toán.
    Bắt buộc trình bày các công thức toán học bằng chuẩn LaTeX tuyệt đẹp.
    
    Đây là đề thi gốc:
    {text_input}
    """

# 6. Giao dien chinh chia 2 cot
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📥 Đầu vào (Văn bản)")
    existing_text = st.text_area("Dán nội dung đề thi vào đây (Tự gõ hoặc Copy/Paste):", height=400)
    btn_generate = st.button("🚀 Xử lý Văn bản & Tạo Đề Mới", key="btn_gen")

with col2:
    st.markdown("### 📤 Kết quả (AI Sinh ra)")
    if btn_generate:
        if not existing_text.strip():
            st.warning("⚠️ Vui lòng dán nội dung đề thi vào ô trống trước!")
        else:
            with st.spinner("🔬 AI đang đọc văn bản và suy luận logic..."):
                try:
                    prompt = get_prompt(difficulty, existing_text)
                    response = model.generate_content(prompt)
                    
                    if "TỪ_CHỐI_MÔN_HỌC" in response.text:
                        st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ phân tích môn Toán và Vật lý!")
                    else:
                        st.success("✅ Đã tạo thành công!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
