import re
import pandas as pd
from pypdf import PdfReader
import streamlit as st
from io import BytesIO


# ------------------- PDF Extraction Logic -------------------
def extract_usage_from_pdf(pdf_bytes):
    """Extract Usage Charges and Account Number from a PDF file."""
    reader = PdfReader(pdf_bytes)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    usage_match = re.search(r"Usage Charges\s*([\d.,]+)", text, re.IGNORECASE)
    account_match = re.search(r"Account Number[:\s]*([0-9]+)", text, re.IGNORECASE)

    if usage_match and account_match:
        try:
            usage_amount = float(usage_match.group(1).replace(",", ""))
        except ValueError:
            return None, None
        account_number = account_match.group(1)
        return account_number, usage_amount
    return None, None


# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Usage Charges Extractor", page_icon="📊", layout="centered")

st.title("📊 Etisalat Usage Charges Extractor")
st.markdown("Upload one or multiple Etisalat PDF bills to extract **Usage Charges** and **Account Numbers**.")

uploaded_files = st.file_uploader("📂 Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    extracted_data = []

    with st.spinner("Processing PDFs..."):
        for pdf in uploaded_files:
            account, usage = extract_usage_from_pdf(pdf)
            if account and usage is not None and usage > 0:
                extracted_data.append({
                    "Account Number": account,
                    "Usage Charges (AED)": usage,
                    "File Name": pdf.name
                })

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        st.success(f" Extracted {len(df)} record(s) with Usage > 0.")

        # Display table
        st.dataframe(df)

        # Convert to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Usage_Report")

        st.download_button(
            label="⬇️ Download Excel Report",
            data=output.getvalue(),
            file_name="usage_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No valid Usage Charges > 0 found in uploaded files.")
else:
    st.info("Please upload one or more PDF files to begin.")
