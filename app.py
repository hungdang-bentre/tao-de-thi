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
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình.")
    st.stop()

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Chọn độ khó cho đề mới:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.info("💡 Hệ thống tự động nhận dạng ma trận, tích phân và đồ thị từ ảnh chụp.")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán học & Vật lý</div>', unsafe_allow_html=True)

def get_prompt(mode, level):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên về Toán học và Vật lý.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
    PHẦN 2: Tạo đề thi mới với độ khó: {level}. 
    Thay đổi các số liệu, phương trình nhưng giữ nguyên bản chất. Trình bày công thức bằng chuẩn LaTeX tuyệt đẹp.
    """

# 6. Phan chia Tab va Cot
tab1, tab2 = st.tabs(["📸 TẠO ĐỀ TỪ ẢNH (Khuyên dùng)", "📝 TẠO ĐỀ TỪ VĂN BẢN"])

with tab1:
    col1, col2 = st.columns([1, 1]) 
    with col1:
        st.markdown("### 📥 Đầu vào (Ảnh)")
        uploaded_file = st.file_uploader("Kéo thả hoặc dán (Ctrl+V) ảnh đề thi vào đây:", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Bản gốc", use_container_width=True)
        btn_img = st.button("🚀 Xử lý Ảnh & Tạo Đề", key="btn1")
        
    with col2:
        st.markdown("### 📤 Kết quả (AI Sinh ra)")
        if btn_img and uploaded_file:
            with st.spinner("🔬 Đang phân tích đồ thị và phương trình..."):
                try:
                    response = model.generate_content([get_prompt("ảnh", difficulty), image])
                    if "TỪ_CHỐI_MÔN_HỌC" in response.text:
                        st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ môn Toán và Vật lý!")
                    else:
                        st.success("✅ Đã tạo thành công!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi: {e}")

with tab2:
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown("### 📥 Đầu vào (Văn bản)")
        existing_exam = st.text_area("Dán nội dung chữ của đề thi vào đây:", height=250)
        btn_txt = st.button("🚀 Xử lý Văn bản & Tạo Đề", key="btn2")
        
    with col4:
        st.markdown("### 📤 Kết quả (AI Sinh ra)")
        if btn_txt and existing_exam.strip():
            with st.spinner("🔬 Đang suy luận logic bài toán..."):
                try:
                    prompt_text = get_prompt("chữ", difficulty) + f"\nĐề gốc:\n{existing_exam}"
                    response = model.generate_content(prompt_text)
                    if "TỪ_CHỐI_MÔN_HỌC" in response.text:
                        st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ môn Toán và Vật lý!")
                    else:
                        st.success("✅ Đã tạo thành công!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi: {e}")
