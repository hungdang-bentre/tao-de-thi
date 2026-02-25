import streamlit as st
import google.generativeai as genai
from PIL import Image

1. Cấu hình trang (Mở rộng toàn màn hình, thêm icon)
st.set_page_config(page_title="AI Exam Pro", page_icon="⚛️", layout="wide")

2. Trang trí bằng CSS (Tạo màu sắc và nút bấm 3D)
st.markdown("""

<style>
.main-header { font-size: 38px; color: #1E3A8A; font-weight: 800; text-align: center; margin-bottom: 5px; }
.sub-header { font-size: 18px; color: #0284c7; text-align: center; margin-bottom: 30px; font-style: italic; }
div.stButton > button:first-child { background-color: #2563EB; color: white; border-radius: 8px; font-weight: bold; padding: 10px; width: 100%; transition: all 0.3s ease; }
div.stButton > button:first-child:hover { background-color: #1D4ED8; transform: scale(1.02); }
</style>

""", unsafe_allow_html=True)

3. Khởi tạo kết nối AI
try:
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình.")
st.stop()

4. THANH CÔNG CỤ BÊN TRÁI (SIDEBAR)
with st.sidebar:
st.title("⚙️ Tùy chỉnh Đề thi")
difficulty = st.selectbox("Chọn độ khó cho đề mới:", ["Giữ nguyên mức độ gốc", "Dễ hơn một chút", "Nâng cao / Khó hơn"])
st.markdown("---")
st.info("💡 Mẹo Khoa học: Hệ thống tự động nhận dạng cấu trúc ma trận, công thức tích phân và đồ thị lực từ ảnh chụp. Kết quả sẽ được định dạng bằng chuẩn LaTeX.")

5. TIÊU ĐỀ CHÍNH
st.markdown('<div class="main-header">⚛️ Hệ Thống Tạo Đề Thi AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tối ưu hóa chuyên sâu cho Toán học (Giải tích, Đại số tuyến tính) & Vật lý</div>', unsafe_allow_html=True)

Lệnh điều khiển AI dùng chung
def get_prompt(mode, level):
return f"""
Bạn là chuyên gia giáo dục xuất sắc chuyên về Toán học (Giải tích, Đại số...) và Vật lý (Cơ học...).
PHẦN 1: Bắt buộc kiểm tra nội dung. Nếu KHÔNG PHẢI Toán hoặc Vật lý, chỉ được trả lời: "TỪ_CHỐI_MÔN_HỌC".
PHẦN 2: Tạo đề thi mới với độ khó: {level}.
Thay đổi các số liệu, phương trình, hệ trục tọa độ nhưng giữ nguyên bản chất vật lý/toán học. Trình bày công thức bằng chuẩn LaTeX tuyệt đẹp.
"""

6. PHÂN CHIA TAB & CỘT
tab1, tab2 = st.tabs(["📸 TẠO ĐỀ TỪ ẢNH (Khuyên dùng)", "📝 TẠO ĐỀ TỪ VĂN BẢN"])

with tab1:
col1, col2 = st.columns([1, 1]) # Chia 2 cột tỷ lệ 50:50
with col1:
st.markdown("### 📥 Đầu vào (Ảnh)")
uploaded_file = st.file_uploader("Kéo thả hoặc dán (Ctrl+V) ảnh đề thi vào đây:", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
image = Image.open(uploaded_file)
st.image(image, caption="Bản gốc", use_container_width=True)
btn_img = st.button("🚀 Xử lý Ảnh & Tạo Đề", key="btn1")

with tab2:
col3, col4 = st.columns([1, 1])
with col3:
st.markdown("### 📥 Đầu vào (Văn bản)")
existing_exam = st.text_area("Dán nội dung chữ của đề thi vào đây:", height=250)
btn_txt = st.button("🚀 Xử lý Văn bản & Tạo Đề", key="btn2")
