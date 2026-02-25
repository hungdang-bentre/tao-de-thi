import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2

# 1. Cau hinh trang 
st.set_page_config(page_title="AI Exam Pro", page_icon="⚛️", layout="wide")

# Khoi tao bien luu tru chu de doc tu PDF
if "exam_text" not in st.session_state:
    st.session_state.exam_text = ""

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
    st.info("💡 **Tính năng mới:** Kết hợp gửi cả văn bản, chữ trích xuất từ PDF và Ảnh chụp đồ thị cùng một lúc cho AI.")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán học & Vật lý</div>', unsafe_allow_html=True)

def get_prompt(level):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên về Toán học và Vật lý.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
    PHẦN 2: Tạo đề thi mới với độ khó: {level}. 
    Dựa vào CẢ phần văn bản và hình ảnh (nếu có) được cung cấp dưới đây, hãy thay đổi các số liệu, phương trình nhưng giữ nguyên bản chất. Trình bày công thức bằng chuẩn LaTeX tuyệt đẹp.
    """

# 6. Giao dien chinh chia 2 cot
col1, col2 = st.columns([1, 1]) 

with col1:
    st.markdown("### 📥 Đầu vào (Tài liệu gốc)")
    
    # Khu vuc 1: Đọc PDF
    pdf_file = st.file_uploader("1. Tải file PDF để trích xuất chữ (Tùy chọn):", type=["pdf"])
    if pdf_file is not None:
        if st.button("📄 Rút trích chữ từ PDF"):
            extracted_text = ""
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            st.session_state.exam_text = extracted_text
            st.rerun() # Tai lai trang de hien thi chu vao o ben duoi
            
    # Khu vuc 2: O nhap chu
    st.session_state.exam_text = st.text_area("2. Nội dung văn bản (Tự gõ hoặc lấy từ PDF):", value=st.session_state.exam_text, height=200)
    
    # Khu vuc 3: O dan anh
    img_file = st.file_uploader("3. Tải lên hoặc dán (Ctrl+V) ảnh hình học/đồ thị bổ sung:", type=["png", "jpg", "jpeg"])
    if img_file is not None:
        image = Image.open(img_file)
        st.image(image, caption="Ảnh đính kèm", width=250)
        
    btn_generate = st.button("🚀 Xử lý Dữ liệu & Tạo Đề Mới", key="btn_gen")

with col2:
    st.markdown("### 📤 Kết quả (AI Sinh ra)")
    if btn_generate:
        if not st.session_state.exam_text.strip() and img_file is None:
            st.warning("⚠️ Vui lòng nhập ít nhất văn bản hoặc tải một bức ảnh lên!")
        else:
            with st.spinner("🔬 AI đang suy luận logic văn bản và hình ảnh..."):
                try:
                    # Dong goi du lieu de gui cho AI
                    contents_to_send = [get_prompt(difficulty)]
                    
                    if st.session_state.exam_text.strip():
                        contents_to_send.append(f"Văn bản đề thi:\n{st.session_state.exam_text}")
                        
                    if img_file is not None:
                        contents_to_send.append(image)

                    # Gui lenh cho Google AI
                    response = model.generate_content(contents_to_send)
                    
                    if "TỪ_CHỐI_MÔN_HỌC" in response.text:
                        st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ phân tích môn Toán và Vật lý!")
                    else:
                        st.success("✅ Đã tạo thành công!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
