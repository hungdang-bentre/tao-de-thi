import streamlit as st
import google.generativeai as genai
import docx
from io import BytesIO 
import time

# 1. Cau hinh trang
st.set_page_config(page_title="AI Exam Pro", page_icon="⚛️", layout="wide")

# 2. Trang tri bang CSS
st.markdown("""
<style>
.main-header { font-size: 38px; color: #1E3A8A; font-weight: 800; text-align: center; margin-bottom: 5px; }
.sub-header { font-size: 18px; color: #0284c7; text-align: center; margin-bottom: 30px; font-style: italic; }
div.stButton > button:first-child { background-color: #2563EB; color: white; border-radius: 8px; font-weight: bold; padding: 10px; width: 100%; transition: all 0.3s ease; }
div.stButton > button:first-child:hover { background-color: #1D4ED8; transform: scale(1.02); }
.question-box { background-color: #f8fafc; padding: 15px; border-left: 5px solid #0284c7; border-radius: 5px; margin-bottom: 20px; font-family: monospace; white-space: pre-wrap; }
</style>
""", unsafe_allow_html=True)

# 3. Khoi tao ket noi AI (THUẬT TOÁN QUÉT VÀ LỌC THÔNG MINH)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Hỏi Google danh sách các mô hình đang TỒN TẠI THỰC TẾ (Chống lỗi 404)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    selected_model = None
    
    # BƯỚC 1: Tìm bản 1.5 flash chuẩn, né bản 8b và bản thử nghiệm (exp)
    for name in available_models:
        if "1.5-flash" in name.lower() and "8b" not in name.lower() and "exp" not in name.lower():
            selected_model = name
            break
            
    # BƯỚC 2: Nếu Google giấu bản flash, lùi về bản 1.5 pro
    if not selected_model:
        for name in available_models:
            if "1.5-pro" in name.lower() and "exp" not in name.lower():
                selected_model = name
                break
                
    # BƯỚC 3: Chốt chặn an toàn (Chống lỗi 429) - Chọn bất kỳ bản nào KHÔNG PHẢI 2.0 hay 2.5
    if not selected_model:
        for name in available_models:
            if "2.0" not in name and "2.5" not in name:
                selected_model = name
                break
                
    model = genai.GenerativeModel(selected_model)
    
except Exception as e:
    st.error(f"Lỗi khi kết nối AI: {e}")
    st.stop()

# --- DUY TRÌ BỘ NHỚ ---
if "kho_de" not in st.session_state:
    st.session_state.kho_de = [
        {"loai": "THPT Quốc Gia", "mon": "Toán", "ten": "Đề mẫu: Khảo sát Hàm số (VD)", "noi_dung": "Cho hàm số y = x^3 - 3x^2 + 2. Tìm các khoảng đồng biến, nghịch biến và điểm cực đại, cực tiểu của hàm số."},
        {"loai": "Học Sinh Giỏi", "mon": "Vật lý", "ten": "Đề mẫu: Động lực học vật rắn (VD)", "noi_dung": "Một khối trụ đặc đồng chất khối lượng M, bán kính R lăn không trượt trên mặt phẳng nghiêng góc alpha so với phương ngang. Hãy thiết lập phương trình động lực học và tính gia tốc tịnh tiến của khối tâm trụ."}
    ]

if "generated_result" not in st.session_state:
    st.session_state.generated_result = ""

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# --- HÀM TẠO FILE WORD ĐỂ TẢI VỀ ---
def create_docx(text_content):
    doc = docx.Document()
    doc.add_heading('ĐỀ THI & LỜI GIẢI (AI GENERATED)', 0)
    
    for line in text_content.split('\n'):
        if line.strip():
            if line.strip().startswith('**') and line.strip().endswith('**'):
                clean_text = line.replace('**', '')
                p = doc.add_paragraph()
                run = p.add_run(clean_text)
                run.bold = True
                run.font.size = docx.shared.Pt(13)
            else:
                doc.add_paragraph(line)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Độ khó sinh ra:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.success(f"🤖 Đã kết nối an toàn với: **{selected_model.split('/')[-1]}**")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán & Vật lý (Hỗ trợ Xuất file Word)</div>', unsafe_allow_html=True)

def get_prompt(level, text_input):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên ra đề thi Toán và Vật lý cấp THPT.
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ trả lời: "TỪ_CHỐI_MÔN_HỌC".
    
    PHẦN 2: TẠO ĐỀ VÀ GIẢI CHI TIẾT
    Tạo một đề thi mới với độ khó: {level} dựa trên cấu trúc của đề gốc dưới đây.
    
    YÊU CẦU:
    1. Trình bày công thức bằng chuẩn LaTeX.
    2. Trình bày kết quả thành 2 phần rõ rệt:
       - **ĐỀ BÀI MỚI**
       - **LỜI GIẢI CHI TIẾT**
    
    Đề gốc:
    {text_input}
    """

# 6. CHIA TAB GIAO DIỆN
tab1, tab2 = st.tabs(["📝 Tạo Đề Tự Do (Word / Dán chữ)", "📚 Ngân Hàng Đề Thi (Quản trị viên)"])

# --- TAB 1: GIAO DIỆN NHẬP TỰ DO & ĐỌC WORD ---
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📥 Đầu vào tài liệu")
        
        uploaded_word = st.file_uploader("1. Tải lên file Word (.docx) để trích xuất chữ:", type=["docx"])
        if uploaded_word is not None:
            if st.button("📄 Rút trích chữ từ file Word"):
                try:
                    doc = docx.Document(uploaded_word)
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    st.session_state.input_text = "\n".join(full_text)
                    st.rerun() 
                except Exception as e:
                    st.error(f"Lỗi khi đọc file Word: {e}")
        
        existing_text = st.text_area("2. Nội dung đề bài (Chỉnh sửa tự do):", value=st.session_state.input_text, height=250)
        
        if st.button("🚀 AI Tạo Đề & Lời Giải", key="btn_tab1"):
            st.session_state.input_text = existing_text 
            if not existing_text.strip():
                st.warning("⚠️ Vui lòng tải file Word hoặc dán chữ vào ô trống!")
            else:
                with st.spinner("🔬 AI đang phân tích dữ liệu và sinh đề mới..."):
                    try:
                        response = model.generate_content(get_prompt(difficulty, existing_text))
                        st.session_state.generated_result = response.text
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    with col2:
        st.markdown("### 📤 Kết quả & Tải về")
        if st.session_state.generated_result:
            if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                st.error("❌ Chỉ hỗ trợ các môn Khoa học (Toán, Vật lý)!")
            else:
                st.success("✅ Đã tạo thành công!")
                
                docx_file = create_docx(st.session_
