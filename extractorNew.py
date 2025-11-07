import re
import pandas as pd
from pypdf import PdfReader
import streamlit as st
from io import BytesIO

# ---------- PDF Extraction ----------
def extract_usage_and_service_from_pdf(pdf_bytes):
    """Extract Account Number, Usage Charges, and Service Rental from a PDF."""
    reader = PdfReader(pdf_bytes)
    text = "".join([page.extract_text() or "" for page in reader.pages])

    # Regex patterns
    account_match = re.search(r"Account Number[:\s]*([0-9]+)", text, re.IGNORECASE)
    usage_match = re.search(r"Usage Charges\s*([\d.,]+)", text, re.IGNORECASE)
    service_rental_match = re.search(r"Service Rentals?\s*([\d.,]+)", text, re.IGNORECASE)

    if account_match and (usage_match or service_rental_match):
        account_number = account_match.group(1)
        if len(account_number) > 3:
            account_number = account_number[:3] + "-" + account_number[3:]
        usage_amount = float(usage_match.group(1).replace(",", "")) if usage_match else 0.0
        service_rental = float(service_rental_match.group(1).replace(",", "")) if service_rental_match else 0.0
        return account_number, usage_amount, service_rental

    return None, None, None


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Usage & Service Extractor", page_icon="📄", layout="centered")

st.title("📊 Bill Extractor with Account Names")
st.markdown("""
Upload:
1. **Etisalat PDF bills** → to extract *Account Number*, *Usage Charges*, and *Service Rentals*  
2. **Excel file** → containing *Account Number* and *Account Name*  

You’ll get a merged table with editable **Comments**.
""")

# Uploaders
excel_file = st.file_uploader("📋 Upload Excel with Account Numbers & Names", type=["xlsx", "xls"])
uploaded_pdfs = st.file_uploader("📄 Upload PDF Bills", type="pdf", accept_multiple_files=True)

if excel_file and uploaded_pdfs:
    try:
        # Read Excel
        names_df = pd.read_excel(excel_file)
        names_df.columns = names_df.columns.str.strip()  # clean column names
        # Expecting columns: Account Number, Account Name (adjust below if needed)
        if not {"Account Number", "Account Name"}.issubset(names_df.columns):
            st.error("Excel must contain columns: **Account Number** and **Account Name**.")
        else:
            extracted_data = []

            with st.spinner("Extracting data from PDFs..."):
                for pdf in uploaded_pdfs:
                    try:
                        account, usage, service = extract_usage_and_service_from_pdf(pdf)
                        if account and (usage > 0 or service > 0):
                            extracted_data.append({
                                "Account Number": account,
                                "Usage Charges (AED)": usage,
                                "Service Rental (AED)": service
                            })
                    except Exception as e:
                        st.warning(f"Error reading {pdf.name}: {e}")

            if extracted_data:
                df = pd.DataFrame(extracted_data)

                # Merge with Excel names
                merged_df = pd.merge(df, names_df, on="Account Number", how="left")

                # Reorder columns
                merged_df = merged_df[["Account Name", "Account Number", "Usage Charges (AED)", "Service Rental (AED)"]]
                merged_df["Comment"] = ""  # Add editable comment column

                st.success(f"✅ Extracted and matched {len(merged_df)} record(s) successfully.")

                # Editable data table
                st.markdown("### 📝 Review and Add Comments")
                edited_df = st.data_editor(
                    merged_df,
                    use_container_width=True,
                    num_rows="fixed",
                    key="editable_table"
                )

                # Convert to Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    edited_df.to_excel(writer, index=False, sheet_name="Usage_Service_Report")

                st.download_button(
                    label="⬇️ Download Excel Report",
                    data=output.getvalue(),
                    file_name="usage_service_report_with_names.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ No valid data found in the uploaded PDFs.")

    except Exception as e:
        st.error(f"Error processing Excel or PDFs: {e}")

elif not excel_file:
    st.info("📁 Please upload the Excel file first.")
elif not uploaded_pdfs:
    st.info("📄 Please upload one or more PDF files.")
