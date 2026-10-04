import io
import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(
    page_title="ค้นหาเกียรติบัตร", page_icon="📜", layout="centered"
)
st.title("📜 ระบบค้นหาและดาวน์โหลดเกียรติบัตร")

# รายชื่อไฟล์ PDF ทั้ง 4 งาน
PDF_FILES = ["job1.pdf", "job2.pdf", "job3.pdf", "job4.pdf"]

# ช่องกรอกค้นหา
col1, col2 = st.columns(2)
with col1:
    search_name = st.text_input("กรอกชื่อ-นามสกุล:")
with col2:
    search_school = st.text_input("กรอกชื่อโรงเรียน (ระบุหรือไม่ก็ได้):")

if st.button("🔍 ค้นหาเกียรติบัตร"):
    clean_name = search_name.replace(" ", "").strip()
    clean_school = search_school.replace(" ", "").strip()

    if not clean_name and not clean_school:
        st.warning("กรุณาระบุชื่อ-นามสกุล หรือชื่อโรงเรียนอย่างน้อย 1 ช่อง")
    else:
        total_found = 0

        # ระบบจะค้นหาจากไฟล์ทั้ง 4 งานพร้อมกัน
        for pdf_file in PDF_FILES:
            try:
                doc = fitz.open(pdf_file)
            except Exception:
                continue

            for page_index in range(len(doc)):
                page = doc[page_index]
                page_text = page.get_text().replace(" ", "").strip()

                name_match = (clean_name in page_text) if clean_name else True
                school_match = (
                    (clean_school in page_text) if clean_school else True
                )

                if name_match and school_match:
                    total_found += 1

                    # แสดงภาพตัวอย่าง Preview
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")

                    st.markdown(f"### 📄 เกียรติบัตรใบที่ {total_found}")
                    st.image(
                        img_bytes,
                        caption=f"หน้า {page_index + 1}",
                        use_container_width=True,
                    )

                    # สร้างไฟล์ PDF เพื่อดาวน์โหลดเฉพาะใบ
                    single_doc = fitz.open()
                    single_doc.insert_pdf(
                        doc, from_page=page_index, to_page=page_index
                    )

                    pdf_buffer = io.BytesIO()
                    single_doc.save(pdf_buffer)
                    single_doc.close()

                    label_name = clean_name if clean_name else clean_school
                    st.download_button(
                        label=f"⬇️ คลิกดาวน์โหลดเกียรติบัตรใบที่ {total_found} (.pdf)",
                        data=pdf_buffer.getvalue(),
                        file_name=f"เกียรติบัตร_{label_name}_ใบที่{total_found}.pdf",
                        mime="application/pdf",
                        key=f"download_{pdf_file}_{page_index}",
                    )
                    st.divider()

            doc.close()

        if total_found == 0:
            st.error(
                "ไม่พบข้อมูลเกียรติบัตรตามเงื่อนไขที่ระบุ โปรดตรวจสอบตัวสะกด"
            )
        else:
            st.success(f"พบเกียรติบัตรทั้งหมด {total_found} รายการ")
