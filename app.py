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
.question-box { background-color: #f8fafc; padding: 15px; border-left: 5px solid #0284c7; border-radius: 5px; margin-bottom: 20px; font-family: monospace; white-space: pre-wrap; }
</style>
""", unsafe_allow_html=True)

# 3. Khoi tao ket noi AI
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

# --- DUY TRÌ BỘ NHỚ KHO ĐỀ (SESSION STATE) ---
if "kho_de" not in st.session_state:
    # Một vài đề mẫu ban đầu để kho không bị trống
    st.session_state.kho_de = [
        {"loai": "THPT Quốc Gia", "mon": "Toán", "ten": "Đề mẫu: Khảo sát Hàm số (VD)", "noi_dung": "Cho hàm số y = x^3 - 3x^2 + 2. Tìm các khoảng đồng biến, nghịch biến và điểm cực đại, cực tiểu của hàm số."},
        {"loai": "Học Sinh Giỏi", "mon": "Vật lý", "ten": "Đề mẫu: Động lực học vật rắn (VD)", "noi_dung": "Một khối trụ đặc đồng chất khối lượng M, bán kính R lăn không trượt trên mặt phẳng nghiêng góc alpha so với phương ngang. Hãy thiết lập phương trình động lực học và tính gia tốc tịnh tiến của khối tâm trụ."}
    ]

if "generated_result" not in st.session_state:
    st.session_state.generated_result = ""

# 4. Thanh cong cu ben trai
with st.sidebar:
    st.title("⚙️ Tùy chỉnh Đề thi")
    difficulty = st.selectbox("Độ khó sinh ra:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
    st.markdown("---")
    st.info("💡 **Tính năng mới:** Đã chia kho đề thành THPT Quốc Gia và HSG. Bạn có thể tự dán thêm đề mới vào kho ở Tab 2.")

# 5. Tieu de chinh
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa cho Toán & Vật lý (THPT Quốc Gia & HSG)</div>', unsafe_allow_html=True)

def get_prompt(level, text_input):
    return f"""
    Bạn là chuyên gia giáo dục xuất sắc chuyên ra đề thi Toán và Vật lý cấp THPT (bao gồm thi THPT Quốc Gia và thi Học Sinh Giỏi).
    PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ trả lời: "TỪ_CHỐI_MÔN_HỌC".
    
    PHẦN 2: TẠO ĐỀ VÀ GIẢI CHI TIẾT
    Tạo một đề thi mới với độ khó: {level} dựa trên cấu trúc, phong cách của đề gốc dưới đây.
    
    YÊU CẦU:
    1. Trình bày công thức bằng chuẩn LaTeX.
    2. Trình bày kết quả thành 2 phần rõ rệt:
       - **ĐỀ BÀI MỚI**: Ghi nội dung câu hỏi mới.
       - **LỜI GIẢI CHI TIẾT**: Giải từng bước, suy luận logic, chặt chẽ tới đáp án cuối.
    
    Đề gốc:
    {text_input}
    """

# 6. CHIA TAB GIAO DIỆN
tab1, tab2 = st.tabs(["📝 Tạo Đề Tự Do (Dán trực tiếp)", "📚 Ngân Hàng Đề Thi (THPTQG & HSG)"])

# --- TAB 1: GIAO DIỆN NHẬP TỰ DO ---
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📥 Đầu vào tự do")
        existing_text = st.text_area("Dán bài tập bất kỳ vào đây:", height=300)
        if st.button("🚀 Tạo Đề & Lời Giải", key="btn_tab1"):
            if not existing_text.strip():
                st.warning("⚠️ Vui lòng dán đề vào ô trống!")
            else:
                with st.spinner("🔬 AI đang sinh đề mới..."):
                    try:
                        response = model.generate_content(get_prompt(difficulty, existing_text))
                        st.session_state.generated_result = response.text
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    with col2:
        st.markdown("### 📤 Kết quả")
        if st.session_state.generated_result:
            if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                st.error("❌ Chỉ hỗ trợ Toán và Vật lý!")
            else:
                st.success("✅ Đã tạo thành công!")
                st.markdown(st.session_state.generated_result)

# --- TAB 2: NGÂN HÀNG ĐỀ THI ---
with tab2:
    # Chia tab nhỏ bên trong tab 2 để tách biệt khu vực "Xem kho" và "Thêm vào kho"
    sub_tab_xem, sub_tab_them = st.tabs(["🔎 Duyệt & Chọn Đề Trong Kho", "➕ Tự Đưa Đề Mới Vào Kho"])
    
    with sub_tab_them:
        st.markdown("### 📥 Thêm đề của bạn vào hệ thống")
        with st.form("form_them_de"):
            col_a, col_b = st.columns(2)
            with col_a:
                loai_de_moi = st.selectbox("Phân loại kỳ thi:", ["THPT Quốc Gia", "Học Sinh Giỏi"])
            with col_b:
                mon_de_moi = st.selectbox("Môn học:", ["Toán", "Vật lý"])
                
            ten_de_moi = st.text_input("Tên bài / Chủ đề (Ví dụ: Câu 45 Đề Toán HN 2024):")
            noi_dung_moi = st.text_area("Dán nội dung câu hỏi/đề bài vào đây:", height=150)
            
            submit_btn = st.form_submit_button("💾 Lưu Trữ Vào Kho Đề")
            
            if submit_btn:
                if ten_de_moi.strip() and noi_dung_moi.strip():
                    # Thêm dữ liệu vào kho lưu trữ
                    st.session_state.kho_de.append({
                        "loai": loai_de_moi,
                        "mon": mon_de_moi,
                        "ten": ten_de_moi,
                        "noi_dung": noi_dung_moi
                    })
                    st.success(f"🎉 Đã thêm thành công '{ten_de_moi}' vào kho! Bạn có thể sang tab 'Duyệt Kho' để sử dụng ngay.")
                else:
                    st.error("⚠️ Vui lòng nhập Tên bài và Nội dung!")

    with sub_tab_xem:
        col3, col4 = st.columns([1, 1])
        with col3:
            st.markdown("### 🗂️ Bộ Lọc Đề Thi")
            col_c, col_d = st.columns(2)
            with col_c:
                loc_loai = st.selectbox("Lọc theo Kỳ thi:", ["Tất cả", "THPT Quốc Gia", "Học Sinh Giỏi"])
            with col_d:
                loc_mon = st.selectbox("Lọc theo Môn:", ["Tất cả", "Toán", "Vật lý"])
            
            # Lọc danh sách đề trong kho dựa trên lựa chọn
            de_phu_hop = [de for de in st.session_state.kho_de if (loc_loai == "Tất cả" or de["loai"] == loc_loai) and (loc_mon == "Tất cả" or de["mon"] == loc_mon)]
            
            if not de_phu_hop:
                st.warning("⚠️ Chưa có đề nào trong thư mục này. Hãy sang thẻ 'Thêm Đề Mới' để cập nhật nhé!")
            else:
                danh_sach_ten = [de["ten"] for de in de_phu_hop]
                selected_ten = st.selectbox("📌 Chọn bài để luyện tập:", danh_sach_ten)
                
                # Lấy nội dung của đề đang chọn
                de_dang_chon = next(de for de in de_phu_hop if de["ten"] == selected_ten)
                st.markdown("**Nội dung đề gốc:**")
                st.markdown(f'<div class="question-box">{de_dang_chon["noi_dung"]}</div>', unsafe_allow_html=True)
                
                if st.button("🔄 AI Tạo Đề Mới Tương Tự & Giải", key="btn_tab2"):
                    with st.spinner(f"🔬 AI đang phân tích và tạo bài tương tự..."):
                        try:
                            response = model.generate_content(get_prompt(difficulty, de_dang_chon["noi_dung"]))
                            st.session_state.generated_result = response.text
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

        with col4:
            st.markdown("### 📤 Đáp Án Chi Tiết")
            if st.session_state.generated_result:
                if "TỪ_CHỐI_MÔN_HỌC" in st.session_state.generated_result:
                    st.error("❌ Lỗi chủ đề!")
                else:
                    st.success("✅ Đã tạo thành công!")
                    st.markdown(st.session_state.generated_result)
