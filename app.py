import streamlit as st
import google.generativeai as genai
import PyPDF2 # Thư viện mới để đọc PDF

# Tải API key một cách bảo mật
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Tải mô hình AI
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# --- GIAO DIỆN TRANG WEB ---
st.title("Hệ thống Tạo đề thi Toán & Vật lý AI") 
st.write("Tải lên file PDF đề thi gốc của bạn. AI sẽ phân tích và tạo ra một phiên bản đề thi mới với các con số, phương trình và ngữ cảnh khác.")

# 1. Tạo nút tải file PDF
uploaded_file = st.file_uploader("Tải file PDF đề thi lên đây", type="pdf")
existing_exam = ""

# 2. Xử lý file PDF khi người dùng tải lên
if uploaded_file is not None:
    # Đọc nội dung file PDF
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        # Rút trích văn bản từ từng trang
        text = page.extract_text()
        if text:
            existing_exam += text
    
    st.success("Đã đọc thành công nội dung từ file PDF!")

button_clicked = st.button("Tạo Đề Thi Mới")
# --- KẾT THÚC GIAO DIỆN ---

if button_clicked:
    if existing_exam:
        with st.spinner("Đang khởi tạo câu hỏi mới. Quá trình này có thể mất vài chục giây..."):
            prompt = f"""
            Bạn là một chuyên gia giáo dục xuất sắc chuyên về các bộ môn Toán học và Vật lý (đặc biệt là Giải tích, Đại số tuyến tính và Cơ học). 
            Hãy tạo ra một đề thi mới dựa trên định dạng, độ khó và chủ đề của đề thi gốc dưới đây. 
            Nhiệm vụ của bạn là thay đổi các con số cụ thể, phương trình, biến số và ngữ cảnh của bài toán, nhưng phải giữ nguyên vẹn các khái niệm cốt lõi và mục tiêu học tập. Đảm bảo đáp án của các bài toán mới là hợp lý và có thể giải được.
            
            Đây là đề thi gốc:
            {existing_exam}
            """
            
            response = model.generate_content(prompt)
            
            st.subheader("Đề Thi Mới Của Bạn:")
            st.write(response.text)
    else:
        st.warning("Vui lòng tải lên một file PDF có chứa chữ trước! (Lưu ý: Hệ thống chưa đọc được PDF dạng hình ảnh scan).")
