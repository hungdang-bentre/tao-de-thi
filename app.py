try:
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
except Exception as e:
st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình trên Streamlit (Advanced Settings -> Secrets).")
st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

st.title("Hệ thống Tạo đề thi Toán & Vật lý AI")
st.write("Dán nội dung đề thi gốc của bạn vào ô bên dưới. AI sẽ phân tích và tạo ra một phiên bản đề thi mới.")

existing_exam = st.text_area("Dán Đề Thi Gốc Vào Đây (Chỉ nhận Toán học và Vật lý):", height=300)

button_clicked = st.button("Tạo Đề Thi Mới")

if button_clicked:
if existing_exam.strip():
with st.spinner("AI đang kiểm tra dữ liệu và tạo đề thi mới..."):
try:
prompt = f"""
Bạn là một chuyên gia giáo dục xuất sắc chuyên về Toán học (Giải tích, Đại số tuyến tính...) và Vật lý (Cơ học, Nhiệt động lực học...).
