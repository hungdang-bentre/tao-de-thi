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
.question-box { background-color: #f8fafc; padding: 15px; border-left: 5px solid #0284c7; border-radius: 5px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. Khoi tao ket noi AI va Tu dong quet mo hinh
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected_model = available_models[0] 
    
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

# --- DUY TRÌ TRẠNG THÁI (SESSION STATE) ---
if "generated_result" not in st.session_state:
    st.session_state.generated_result = ""

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Chọn độ khó cho đề mới:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.info("💡 Tính năng mới: Đã thêm Tab 'Kho Đề Ôn Tập' với các chủ đề Toán cao cấp, Cơ học và Kỹ thuật lập trình.")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán học, Vật lý & Kỹ thuật (Kèm Lời Giải)</div>', unsafe_allow_html=True)

# Ham ra lenh cho AI (Đã mở rộng thêm các môn Kỹ thuật/Lập trình)
def get_prompt(level, text_input):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên về Khoa học tự nhiên (Toán, Lý) và Kỹ thuật/Khoa học máy tính.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán, Vật lý, hoặc Kỹ thuật/Lập trình, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
    
    PHẦN 2: TẠO ĐỀ VÀ GIẢI CHI TIẾT
    Hãy tạo đề thi mới với độ khó: {level}. Dựa vào văn bản đề thi/chủ đề gốc dưới đây, hãy thay đổi các số liệu, ma trận, hàm số, cấu trúc code hoặc tham số vật lý nhưng giữ nguyên bản chất cốt lõi.
    
    YÊU CẦU BẮT BUỘC VỀ TRÌNH BÀY:
    1. Trình bày các công thức toán học bằng chuẩn LaTeX. Nếu là bài tập lập trình, hãy dùng block code chuẩn.
    2. PHẢI trình bày kết quả thành 2 phần rõ rệt bằng cách sử dụng tiêu đề in đậm:
       - **ĐỀ BÀI MỚI**: Ghi nội dung câu hỏi bạn vừa sáng tạo ra.
       - **LỜI GIẢI CHI TIẾT**: Trình bày cách giải từng bước một một cách logic và chính xác tuyệt đối.
    
    Đây là đề thi/chủ đề gốc:
    {text_input}
    """

# 6. KHO DỮ LIỆU ĐỀ MẪU (BẠN CÓ THỂ TỰ THÊM VÀO ĐÂY)
kho_de = {
    "Toán - Giải tích": "Tính tích phân xác định sau: $\\int_{0}^{\\pi/2} x \\cos(x) dx$. Ứng dụng phương pháp tích phân từng phần.",
    "Toán - Đại số tuyến tính": "Cho ma trận A kích thước 3x3. Hãy tìm các giá trị riêng (eigenvalues) và vectơ riêng (eigenvectors) tương ứng của ma trận đó, biết A = [[2, 0, 0], [1, 2, -1], [1, 3, -2]].",
    "Vật lý - Cơ học": "Một vật khối lượng m = 5kg đang đứng yên trên mặt phẳng ngang. Tác dụng một lực kéo F = 20N hợp với phương ngang một góc 30 độ. Hệ số ma sát trượt là 0.1. Áp dụng định luật 2 Newton, tính gia tốc của vật.",
    "Lập trình - C++ & OOP": "Viết một chương trình C++ minh họa tính Kế thừa và Đóng gói trong Lập trình hướng đối tượng (OOP). Tạo một lớp cơ sở 'Shape' và lớp dẫn xuất 'Rectangle'.",
    "Kỹ thuật - Robot Arduino": "Thiết kế sơ đồ thuật toán điều khiển cho một Robot dò line (line-following robot) sử dụng 2 cảm biến hồng ngoại trái/phải. Viết đoạn mã Arduino cơ bản để điều khiển 2 động cơ DC dựa trên trạng thái cảm biến."
}

# 7. CHIA TAB GIAO DIỆN
tab1, tab2 = st.tabs(["📝 Tạo Đề Tự Do (Copy/Paste)", "📚 Kho Đề Ôn Tập (Chủ đề có sẵn)"])

# --- TAB 1: GIAO DIỆN CŨ ---
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📥 Đầu vào tự do")
        existing_text = st.text_area("Dán nội dung đề thi của bạn vào đây:", height=300)
        if st.button("🚀 Tạo Đề & Lời Giải Mới", key="btn_tab1"):
            if not existing_text.strip():
                st.warning("⚠️ Vui lòng dán nội dung đề thi vào ô trống trước!")
            else:
                with st.spinner("🔬 AI đang sinh đề mới..."):
                    try:
                        prompt = get_prompt(difficulty, existing_text)
                        response = model.generate_content(prompt)
                        st.session_state.generated_result = response.text
                    except Exception as e:
                        st.error(f"Lỗi hệ thống: {e}")

    with col2:
        st.markdown("### 📤 Kết quả")
        if st.session_state.generated_result:
            if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                st.error("❌ Xin lỗi, hệ thống chỉ hỗ trợ phân tích Toán, Vật lý và Kỹ thuật!")
            else:
                st.success("✅ Đã tạo thành công!")
                st.markdown(st.session_state.generated_result)

# --- TAB 2: KHO ĐỀ ÔN TẬP ---
with tab2:
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown("### 🗂️ Lựa chọn Chủ đề")
        selected_category = st.selectbox("Chọn một dạng bài tập có sẵn trong kho:", list(kho_de.keys()))
        
        st.markdown("**Nội dung đề gốc trong kho:**")
        st.markdown(f'<div class="question-box">{kho_de[selected_category]}</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Tạo Biến Thể & Giải Chi Tiết", key="btn_tab2"):
            with st.spinner(f"🔬 AI đang tạo một bài '{selected_category}' mới tương tự..."):
                try:
                    prompt = get_prompt(difficulty, kho_de[selected_category])
                    response = model.generate_content(prompt)
                    st.session_state.generated_result = response.text
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")

    with col4:
        st.markdown("### 📤 Kết quả Ôn tập")
        if st.session_state.generated_result:
            if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                st.error("❌ Lỗi chủ đề!")
            else:
                st.success("✅ Đã tạo bài ôn tập thành công!")
                st.markdown(st.session_state.generated_result)
