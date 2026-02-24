import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện
st.set_page_config(page_title="Tạo Đề Thi AI", layout="centered")

# Kiểm tra API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình trên Streamlit (Advanced Settings -> Secrets).")
    st.stop()

# Khởi tạo mô hình AI (Sử dụng bản Flash chuẩn nhất)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- GIAO DIỆN TRANG WEB ---
st.title("Hệ thống Tạo đề thi Toán & Vật lý AI") 
st.write("Dán nội dung đề thi gốc của bạn vào ô bên dưới. AI sẽ phân tích và tạo ra một phiên bản đề thi mới với các con số, phương trình và ngữ cảnh khác.")

existing_exam = st.text_area("Dán Đề Thi Gốc Vào Đây (Giải tích, Đại số, Cơ học...):", height=300)

button_clicked = st.button("Tạo Đề Thi Mới")
# --- KẾT THÚC GIAO DIỆN ---

if button_clicked:
    if existing_exam.strip(): # Kiểm tra xem người dùng có nhập chữ không
        with st.spinner("AI đang tạo đề thi mới... Quá trình này có thể mất vài chục giây..."):
            try:
                # Chỉ thị chi tiết cho AI
                prompt = f"""
                Bạn là một chuyên gia giáo dục xuất sắc chuyên về các bộ môn Khoa học tự nhiên (đặc biệt là Giải tích, Đại số tuyến tính, Cơ học). 
                Hãy tạo ra một đề thi mới dựa trên định dạng, độ khó và chủ đề của đề thi gốc dưới đây. 
                Nhiệm vụ của bạn là thay đổi các con số cụ thể, phương trình, biến số và ngữ cảnh của bài toán, nhưng phải giữ nguyên vẹn các khái niệm cốt lõi và mục tiêu học tập. Đảm bảo đáp án của các bài toán mới là hợp lý và có thể giải được.
                
                Đây là đề thi gốc:
                {existing_exam}
                """
                
                response = model.generate_content(prompt)
                
                st.subheader("Đề Thi Mới Của Bạn:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi từ phía Google AI. Chi tiết lỗi:\n {e}")
    else:
        st.warning("Vui lòng dán nội dung đề thi vào ô trống trước!")
