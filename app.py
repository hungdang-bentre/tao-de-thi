import streamlit as st
import google.generativeai as genai
import docx
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

# 3. Khoi tao ket noi AI (QUÉT THÔNG MINH, KHÔNG TỰ BỊA ĐUÔI SỐ)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Lấy danh sách model thực tế đang tồn tại
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    selected_model = None
    
    # Ưu tiên 1: Tóm ngay bản 1.5 Flash chuẩn đang hiển thị trong danh sách (Né 8b và exp)
    for name in available_models:
        if "gemini-1.5-flash" in name.lower() and "8b" not in name.lower() and "exp" not in name.lower():
            selected_model = name
            break
            
    # Ưu tiên 2: Nếu không có Flash, tóm bản 1.5 Pro
    if not selected_model:
        for name in available_models:
            if "gemini-1.5-pro" in name.lower() and "exp" not in name.lower():
                selected_model = name
                break
                
    # Ưu tiên 3: Có bản 1.5 nào thì lấy bản đó
    if not selected_model:
        for name in available_models:
            if "1.5" in name:
                selected_model = name
                break
                
    # Chốt chặn cuối cùng: Gọi bí danh chung nhất, Google tự điều phối
    if not selected_model:
        selected_model = "gemini-1.5-flash"
        
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

# --- CẤU HÌNH AI ĐỂ CHỐNG LỖI LẶP TỪ ---
ai_config = {
    "temperature": 0.7, 
    "top_p": 0.9,
    "max_output_tokens": 2000 
}

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Độ khó sinh ra:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.success(f"🤖 Đã kết nối an toàn với: **{selected_model.split('/')[-1]}**")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán & Vật lý (Sao chép nội dung siêu tốc)</div>', unsafe_allow_html=True)

def get_prompt(level, text_input):
    return f"""
    Bạn là một giáo viên chuyên Toán và Vật lý cấp THPT. 
    PHẦN 1: Nếu nội dung dưới đây KHÔNG PHẢI Toán hoặc Vật lý, hãy trả lời: "TỪ_CHỐI_MÔN_HỌC" và dừng lại.
    
    PHẦN 2: TẠO ĐỀ VÀ GIẢI CHI TIẾT
    Hãy tạo một đề thi mới với độ khó: {level} dựa trên đề gốc.
    
    BẠN BẮT BUỘC PHẢI TUÂN THỦ ĐỊNH DẠNG TRÌNH BÀY SAU ĐÂY:
    1. Trình bày công thức bằng chuẩn LaTeX (ví dụ: $x^2 + y^2$).
    2. Phải chia rõ thành 2 phần bằng các dòng chữ in đậm sau:
    
    **ĐỀ BÀI MỚI**
    (Nội dung đề bài)
    
    **LỜI GIẢI CHI TIẾT**
    (Nội dung lời giải từng bước)
    
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
                        response = model.generate_content(
                            get_prompt(difficulty, existing_text),
                            generation_config=ai_config
                        )
                        st.session_state.generated_result = response.text
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    with col2:
        st.markdown("### 📤 Kết quả & Copy")
        if st.session_state.generated_result:
            if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                st.error("❌ Chỉ hỗ trợ các môn Khoa học (Toán, Vật lý)!")
            else:
                st.success("✅ Đã tạo thành công!")
                
                st.markdown("**1. Dưới đây là giao diện xem trước (Preview):**")
                st.markdown(st.session_state.generated_result)
                
                st.markdown("---")
                
                st.markdown("**2. 📋 Click vào biểu tượng Copy ở góc trên bên phải khung xám dưới đây để dán vào Word:**")
                st.code(st.session_state.generated_result, language="markdown")

# --- TAB 2: NGÂN HÀNG ĐỀ THI (BẢO MẬT) ---
with tab2:
    sub_tab_xem, sub_tab_them = st.tabs(["🔎 Duyệt & Chọn Đề Trong Kho", "➕ Tự Đưa Đề Mới Vào Kho (Admin)"])
    
    with sub_tab_them:
        st.markdown("### 📥 Thêm đề của bạn vào hệ thống")
        with st.form("form_them_de"):
            col_a, col_b = st.columns(2)
            with col_a:
                loai_de_moi = st.selectbox("Phân loại kỳ thi:", ["THPT Quốc Gia", "Học Sinh Giỏi"])
            with col_b:
                mon_de_moi = st.selectbox("Môn học:", ["Toán", "Vật lý"])
                
            ten_de_moi = st.text_input("Tên bài / Chủ đề (Ví dụ: Động học chất điểm):")
            noi_dung_moi = st.text_area("Dán nội dung câu hỏi/đề bài vào đây:", height=150)
            
            st.markdown("---")
            admin_pass = st.text_input("🔑 Nhập Mật Khẩu Quản Trị Viên:", type="password")
            
            submit_btn = st.form_submit_button("💾 Xác Nhận & Lưu Trữ Vào Kho")
            
            if submit_btn:
                mat_khau_goc = st.secrets.get("ADMIN_PASSWORD", "admin123")
                if admin_pass != mat_khau_goc:
                    st.error("❌ Mật khẩu không chính xác!")
                elif not ten_de_moi.strip() or not noi_dung_moi.strip():
                    st.warning("⚠️ Vui lòng nhập đầy đủ Tên bài và Nội dung!")
                else:
                    st.session_state.kho_de.append({
                        "loai": loai_de_moi,
                        "mon": mon_de_moi,
                        "ten": ten_de_moi,
                        "noi_dung": noi_dung_moi
                    })
                    st.toast(f"🎉 Đã thêm thành công '{ten_de_moi}' vào kho!", icon="✅")
                    time.sleep(1.2)
                    st.rerun()

    with sub_tab_xem:
        col3, col4 = st.columns([1, 1])
        with col3:
            st.markdown("### 🗂️ Bộ Lọc Đề Thi")
            col_c, col_d = st.columns(2)
            with col_c:
                loc_loai = st.selectbox("Lọc theo Kỳ thi:", ["Tất cả", "THPT Quốc Gia", "Học Sinh Giỏi"])
            with col_d:
                loc_mon = st.selectbox("Lọc theo Môn:", ["Tất cả", "Toán", "Vật lý"])
            
            de_phu_hop = [de for de in st.session_state.kho_de if (loc_loai == "Tất cả" or de["loai"] == loc_loai) and (loc_mon == "Tất cả" or de["mon"] == loc_mon)]
            
            if not de_phu_hop:
                st.warning("⚠️ Chưa có đề nào trong thư mục này.")
            else:
                danh_sach_ten = [de["ten"] for de in de_phu_hop]
                selected_ten = st.selectbox("📌 Chọn bài để luyện tập:", danh_sach_ten)
                
                de_dang_chon = next(de for de in de_phu_hop if de["ten"] == selected_ten)
                st.markdown("**Nội dung đề gốc:**")
                st.markdown(f'<div class="question-box">{de_dang_chon["noi_dung"]}</div>', unsafe_allow_html=True)
                
                if st.button("🔄 AI Tạo Đề Mới Tương Tự & Giải", key="btn_tab2"):
                    with st.spinner(f"🔬 AI đang phân tích và tạo bài tương tự..."):
                        try:
                            response = model.generate_content(
                                get_prompt(difficulty, de_dang_chon["noi_dung"]),
                                generation_config=ai_config
                            )
                            st.session_state.generated_result = response.text
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

        with col4:
            st.markdown("### 📤 Kết quả & Copy")
            if st.session_state.generated_result:
                if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                    st.error("❌ Lỗi chủ đề!")
                else:
                    st.success("✅ Đã tạo thành công!")
                    
                    st.markdown("**1. Dưới đây là giao diện xem trước (Preview):**")
                    st.markdown(st.session_state.generated_result)
                    
                    st.markdown("---")
                    
                    st.markdown("**2. 📋 Click vào biểu tượng Copy ở góc trên bên phải khung xám dưới đây để dán vào Word:**")
                    st.code(st.session_state.generated_result, language="markdown")
