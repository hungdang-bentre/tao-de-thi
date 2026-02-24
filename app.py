import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện
st.set_page_config(page_title="Tạo Đề Thi AI", layout="centered")

# 1. Kiểm tra API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình trên Streamlit (Advanced Settings -> Secrets).")
    st.stop()

# --- KHẮC PHỤC LỖI 404: TỰ ĐỘNG QUÉT VÀ CHỌN MÔ HÌNH ---
st.title("Hệ thống Tạo đề thi Toán & Vật lý AI") 

try:
    # Quét tất cả các mô hình mà API Key này được phép dùng
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Logic tự động chọn mô hình tốt nhất hiện có
    selected_model = available_models[0] # Khởi tạo mặc định
    
    # Ưu tiên tìm bản flash mới nhất, nếu không có thì lùi về bản pro hoặc bản tiêu chuẩn
    for name in available_models:
        if "gemini-1.5-flash" in name:
            selected_model = name
            break
        elif "gemini-1.5-pro" in name:
            selected_model = name
        elif "gemini-pro" in name and "1.5" not in selected_model:
            selected_model = name
            
    st.success(f"Đã tự động nhận diện và kết nối thành công với AI: {selected_model}")
    model = genai.GenerativeModel(selected_model)
    
except Exception as e:
    st.error(f"Lỗi khi quét danh sách mô hình từ Google: {e}")
    st.stop()

# --- GIAO DIỆN NHẬP ĐỀ THI ---
st.write("Dán nội dung đề thi gốc của bạn vào ô bên dưới. AI sẽ phân tích và tạo ra phiên bản mới.")

existing_exam = st.text_area("Dán Đề Thi Gốc Vào Đây (Giải tích, Đại số tuyến tính, Cơ học...):", height=300)

button_clicked = st.button("Tạo Đề Thi Mới")

if button_clicked:
    if existing_exam.strip():
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
