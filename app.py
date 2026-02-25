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

# 3. Khoi tao ket noi AI va Tu dong quet mo hinh
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Quét tất cả các mô hình mà API Key này được phép dùng
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    selected_model = available_models[0] # Khởi tạo mặc định
    
    # Ưu tiên tìm bản Flash (để lấy hạn mức miễn phí lớn), nếu không có mới lùi về Pro
    for name in available_models:
        if "flash" in name.lower() and "8b" not in name.lower():
            selected_model = name
            break
        elif "pro" in name.lower():
            selected_model = name
            
    model = genai.GenerativeModel(selected_model)
    
except Exception as e:
    st.error(f"Lỗi khi kết nối AI: {e}")
    st.stop()

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Chọn độ khó cho đề mới:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.info("💡 Chế độ: Nhập văn bản. Đã bật tính năng: Tự động sinh Lời giải chi tiết từng bước cho mọi bài toán.")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán học & Vật lý (Kèm Lời Giải Chi Tiết)</div>', unsafe_allow_html=True)

def get_prompt(level, text_input):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên về Toán học và Vật lý.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
    
    PHẦN 2: TẠO ĐỀ VÀ GIẢI CHI TIẾT
    Hãy tạo đề thi mới với độ khó: {level}. Dựa vào văn bản đề thi gốc dưới đây, hãy thay đổi các số liệu, phương trình, toạ độ, biến số nhưng giữ nguyên bản chất bài toán.
    
    YÊU CẦU BẮT BUỘC VỀ TRÌNH BÀY:
    1. Trình bày các công thức toán học bằng chuẩn LaTeX.
    2. Bạn PHẢI trình bày kết quả thành 2 phần rõ rệt bằng cách sử dụng tiêu đề in đậm:
       - **ĐỀ BÀI MỚI**: Ghi nội dung câu hỏi bạn vừa sáng tạo ra.
       - **LỜI GIẢI CHI TIẾT**: Trình bày cách giải từng bước một, giải thích công thức áp dụng và tính ra đáp án cuối cùng. Đảm bảo lời giải logic, chính xác tuyệt đối.
    
    Đây là đề thi gốc:
    {text_input}
    """

# 6. Giao dien chinh chia 2 cot
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📥 Đầu vào (Văn bản)")
    existing_text = st.text_area("Dán nội dung đề thi vào đây (Tự gõ hoặc Copy/Paste):", height=400)
    btn_generate = st.button("🚀 Tạo Đề & Lời Giải Mới", key="btn_gen")

with col2:
    st.markdown("### 📤 Kết quả (AI Sinh ra)")
    if btn_generate:
        if not existing_text.strip():
            st.warning("⚠️ Vui lòng dán nội dung đề thi vào ô trống trước!")
        else:
            with st.spinner("🔬 AI đang sinh đề mới và viết lời giải chi tiết..."):
                try:
                    prompt = get_prompt(difficulty, existing_text)
                    response = model.generate_content(prompt)
                    
                    if "TỪ_CHỐI_MÔN_HỌC" in response.text:
                        st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ phân tích môn Toán và Vật lý!")
                    else:
                        st.success("✅ Đã tạo đề và lời giải thành công!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
