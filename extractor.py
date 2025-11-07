# import re
# import pandas as pd
# from pypdf import PdfReader
# import streamlit as st
# from io import BytesIO

# def extract_usage_and_service_from_pdf(pdf_bytes):
#     """Extract Account Number, Usage Charges, and Service Rental from a PDF."""
#     reader = PdfReader(pdf_bytes)
#     text = "".join([page.extract_text() or "" for page in reader.pages])

#     # Regex patterns
#     account_match = re.search(r"Account Number[:\s]*([0-9]+)", text, re.IGNORECASE)
#     usage_match = re.search(r"Usage Charges\s*([\d.,]+)", text, re.IGNORECASE)
#     service_rental_match = re.search(r"Service Rentals?\s*([\d.,]+)", text, re.IGNORECASE)

#     if account_match and (usage_match or service_rental_match):
#         account_number = account_match.group(1)
#         if len(account_number) > 3:
#             account_number = account_number[:3] + "-" + account_number[3:]
#         usage_amount = float(usage_match.group(1).replace(",", "")) if usage_match else 0.0
#         service_rental = float(service_rental_match.group(1).replace(",", "")) if service_rental_match else 0.0
#         return account_number, usage_amount, service_rental

#     return None, None, None


# # ------------------- Streamlit UI -------------------
# st.set_page_config(page_title="Usage & Service Extractor", page_icon="📄", layout="centered")

# st.title("📊 Bill Extractor")
# st.markdown("Upload one or multiple Etisalat PDF bills to extract **Account Number**, **Usage Charges**, and **Service Rentals** — and directly add **comments** in the table below.")

# uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

# if uploaded_files:
#     extracted_data = []

#     with st.spinner("Processing PDFs..."):
#         for pdf in uploaded_files:
#             try:
#                 account, usage, service = extract_usage_and_service_from_pdf(pdf)
#                 if account and (usage > 0 or service > 0):
#                     extracted_data.append({
#                         "Account Number": account,
#                         "Usage Charges (AED)": usage,
#                         "Service Rental (AED)": service,
#                         "Comment": ""  # editable later
#                     })
#             except Exception as e:
#                 st.warning(f"Error reading {pdf.name}: {e}")

#     if extracted_data:
#         df = pd.DataFrame(extracted_data)
#         st.success(f"✅ Extracted {len(df)} record(s) successfully.")

#         # Editable data table
#         st.markdown("### 📝 Review and Add Comments")
#         edited_df = st.data_editor(
#             df,
#             use_container_width=True,
#             num_rows="fixed",  # disable adding/removing rows
#             key="editable_table"
#         )

#         # Convert to Excel for download
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine="openpyxl") as writer:
#             edited_df.to_excel(writer, index=False, sheet_name="Usage_Service_Report")

#         st.download_button(
#             label="⬇️ Download Excel Report",
#             data=output.getvalue(),
#             file_name="usage_service_report.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     else:
#         st.warning("⚠️ No valid data found with Usage or Service Rental > 0.")
# else:
#     st.info("📁 Please upload one or more PDF files to begin.")


