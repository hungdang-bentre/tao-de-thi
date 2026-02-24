import streamlit as st
import google.generativeai as genai

# Tải API key một cách bảo mật
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Tải mô hình AI
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PHẦN GIAO DIỆN TRANG WEB (BẠN CÓ THỂ ĐỔI CHỮ TRONG NGOẶC KÉP) ---
st.title("Hệ thống Tạo đề thi Toán & Vật lý AI") 
st.write("Dán các câu hỏi Giải tích, Đại số tuyến tính, Cơ học hoặc bất kỳ môn nào của bạn vào đây. AI sẽ phân tích và tạo ra một phiên bản đề thi mới với các con số, phương trình và ngữ cảnh khác nhưng vẫn giữ nguyên cấu trúc, độ khó và mục tiêu kiểm tra.")

existing_exam = st.text_area("Dán Đề Thi Gốc Vào Đây:", height=250)

button_clicked = st.button("Tạo Đề Thi Mới")
# --- KẾT THÚC PHẦN GIAO DIỆN ---

if button_clicked:
    if existing_exam:
        with st.spinner("Đang khởi tạo câu hỏi mới..."):
            # Lệnh hướng dẫn AI cách làm việc
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
        st.warning("Vui lòng dán nội dung đề thi vào ô trống trước!")
