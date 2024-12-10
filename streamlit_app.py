# 📚 Import các thư viện cần thiết
import streamlit as st
import pandas as pd
import csv
import time
import random
from jobspy import scrape_jobs

# 🔍 Tiêu đề của ứng dụng
st.title('🔍 Tìm kiếm công việc IT tại Việt Nam')

# 📦 Nhập từ khóa tìm kiếm từ người dùng (không cho chỉnh địa điểm)
st.sidebar.header('Nhập từ khóa công việc bạn muốn tìm')
search_term = st.sidebar.text_input('Nhập từ khóa công việc:', 'Cybersecurity Analyst')

# Cố định địa điểm tìm kiếm là "Vietnam"
location = 'Vietnam'

# Nút bấm để bắt đầu tìm kiếm
if st.sidebar.button('Tìm kiếm công việc'):
    st.info(f'⏳ Đang tìm kiếm công việc với từ khóa **"{search_term}"** tại **"Vietnam"**. Vui lòng đợi trong giây lát...')

    # 🕒 Giảm tần suất gửi yêu cầu để tránh lỗi 429
    time.sleep(random.randint(10, 30))  # Đợi ngẫu nhiên từ 10 đến 30 giây

    # 📦 Thu thập dữ liệu từ các trang web tuyển dụng
    try:
        all_jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "glassdoor", "google"],  # Các trang web cần thu thập
            search_term=search_term,  # Từ khóa tìm kiếm
            google_search_term=f"{search_term} jobs in {location}",  # Từ khóa tìm kiếm trên Google
            location=location,  # Địa điểm cố định là Vietnam
            results_wanted=30,  # Số lượng kết quả mong muốn
            hours_old=720,  # Giới hạn thời gian đăng tin (30 ngày = 720 giờ)
            country_indeed='vietnam',  # Mã quốc gia cho Indeed
            linkedin_fetch_description=True  # Lấy thêm mô tả công việc từ LinkedIn
        )
    except Exception as e:
        st.error(f"❌ Đã xảy ra lỗi trong quá trình thu thập công việc: {e}")
        all_jobs = []

    # 📊 Hiển thị số công việc tìm thấy
    st.success(f"✅ Tìm thấy {len(all_jobs)} công việc phù hợp.")

    # 🗂️ Nếu không tìm thấy công việc nào, hiển thị thông báo
    if len(all_jobs) == 0:
        st.warning("⚠️ Không tìm thấy công việc nào. Vui lòng kiểm tra từ khóa hoặc thử lại sau.")
    else:
        try:
            # Tạo DataFrame từ dữ liệu đã thu thập
            df_jobs = pd.DataFrame(all_jobs)

            # 🌟 Chọn các cột quan trọng cho người dùng
            df_jobs_filtered = df_jobs[['title', 'company', 'date_posted', 'location', 'job_type', 'job_url', 'description']]

            # ✂️ Giới hạn số ký tự của mô tả (chỉ lấy 150 ký tự đầu tiên để mô tả ngắn gọn)
            df_jobs_filtered['description'] = df_jobs_filtered['description'].str[:150] + '...'

            # 🗂️ Xóa các dòng dữ liệu trống hoặc không hợp lệ
            df_jobs_filtered = df_jobs_filtered.dropna(subset=['title', 'company', 'job_url'])

            # ✍️ Tạo cột "Xem chi tiết" có chứa link ứng tuyển
            df_jobs_filtered['Xem chi tiết'] = df_jobs_filtered['job_url'].apply(lambda x: f'<a href="{x}" target="_blank">Xem chi tiết</a>')

            # Ẩn cột "job_url" vì đã có "Xem chi tiết"
            df_jobs_filtered = df_jobs_filtered[['title', 'company', 'date_posted', 'location', 'job_type', 'description', 'Xem chi tiết']]

            # 📘 Hiển thị dữ liệu công việc dưới dạng bảng để người dùng có thể dễ dàng đọc
            st.write("### 📋 Danh sách công việc")
            st.markdown(df_jobs_filtered.to_html(escape=False, index=False), unsafe_allow_html=True)

            # 💾 Tải xuống tệp CSV
            csv = df_jobs_filtered.to_csv(index=False)
            st.download_button(
                label="💾 Tải xuống file CSV",
                data=csv,
                file_name='jobs_filtered.csv',
                mime='text/csv',
            )
        except Exception as e:
            st.error(f"❌ Đã xảy ra lỗi khi xử lý dữ liệu công việc: {e}")
