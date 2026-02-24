import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện trang web rộng rãi hơn
st.set_page_config(page_title="Tạo Đề Thi AI", layout="wide")

# Kiểm tra xem API Key đã được cài đặt chưa
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại Bước cài đặt Advanced Settings -> Secrets trên Streamlit.")
    st.stop()

# Tải mô hình AI chuẩn xác nhất
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- GIAO DIỆN TRANG WEB ---
st.title("Hệ thống Tạo đề thi Toán & Vật lý AI") 
st.write("Tải lên file PDF đề thi gốc. Hệ thống có khả năng nhận diện hình vẽ cơ học, đồ thị và các công thức toán phức tạp trực tiếp từ file.")

uploaded_file = st.file_uploader("Tải file PDF đề thi lên đây", type="pdf")

button_clicked = st.button("Tạo Đề Thi Mới")
# --- KẾT THÚC GIAO DIỆN ---

if button_clicked:
    if uploaded_file is not None:
        with st.spinner("AI đang đọc trực tiếp file PDF và phân tích... Quá trình này có thể mất 30-60 giây..."):
            try:
                # Đóng gói file PDF nguyên bản để gửi cho AI
                pdf_data = {
                    "mime_type": "application/pdf",
                    "data": uploaded_file.getvalue()
                }
                
                # Hướng dẫn chi tiết cho AI
                prompt = """
                Bạn là một chuyên gia giáo dục xuất sắc chuyên về các bộ môn Khoa học tự nhiên. 
                Hãy đọc trực tiếp file PDF đề thi đính kèm (bao gồm cả công thức và hình ảnh nếu có) và tạo ra một đề thi mới. 
                Nhiệm vụ của bạn là thay đổi các con số cụ thể, phương trình, biến số và ngữ cảnh của bài toán, nhưng phải giữ nguyên vẹn các khái niệm cốt lõi, độ khó và mục tiêu học tập. 
                Đảm bảo đáp án của các bài toán mới là hợp lý và có thể giải được. Hãy trình bày rõ ràng, giữ nguyên số lượng và cấu trúc câu hỏi.
                """
                
                # Gửi CẢ file PDF và câu lệnh cho AI cùng một lúc
                response = model.generate_content([prompt, pdf_data])
                
                st.subheader("Đề Thi Mới Của Bạn:")
                st.write(response.text)
                
            except Exception as e:
                # Nếu có lỗi, in thẳng ra màn hình để bắt bệnh
                st.error(f"Đã xảy ra lỗi từ phía Google AI. Chi tiết lỗi:\n {e}")
    else:
        st.warning("Vui lòng tải lên một file PDF trước khi bấm nút!")
