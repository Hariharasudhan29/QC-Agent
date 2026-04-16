import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SAFE IMPORT HANDLER ---
try:
    from google.ads.googleads.client import GoogleAdsClient
    HAS_GOOGLE_ADS = True
except ImportError:
    HAS_GOOGLE_ADS = False

# --- 2. DATA INGESTION ---
def get_expected_data():
    data = {
        'ID': ['CAM-01', 'CAM-02', 'CAM-03', 'CAM-04', 'CAM-05'],
        'Expected': [1200.50, 4500.00, 300.00, 1500.00, 890.20]
    }
    return pd.DataFrame(data)

# --- 3. QC ENGINE LOGIC ---
def run_qc_process(expected_df, actual_df, limit):
    # Standardizing column names to uppercase for internal processing
    actual_df.columns = [str(col).upper() for col in actual_df.columns]
    expected_df.columns = [str(col).upper() for col in expected_df.columns]

    # Merge data
    merged = pd.merge(expected_df, actual_df, on='ID', how='inner')
    
    # Math Logic
    merged['VARIANCE'] = merged['ACTUAL'] - merged['EXPECTED']
    merged['VARIANCE_%'] = (merged['VARIANCE'] / merged['EXPECTED']) * 100
    
    # Status Assignment
    merged['QC_RESULT'] = np.where(
        merged['VARIANCE_%'].abs() <= limit, 
        '✅ PASS', 
        '⚠️ FAIL'
    )
    return merged

# --- 4. STREAMLIT DASHBOARD UI ---
def main():
    st.set_page_config(page_title="AI QC Agent", layout="wide")
    st.title("🛡️ QC AI Agent: Variance Validator")

    st.sidebar.header("Agent Settings")
    threshold = st.sidebar.slider("Tolerance Threshold (%)", 0.0, 15.0, 5.0)
    
    if not HAS_GOOGLE_ADS:
        st.sidebar.warning("Running in Mock Mode (API library missing)")

    uploaded_file = st.sidebar.file_uploader("Upload Actual Values (CSV)", type="csv")

    if uploaded_file:
        expected_df = get_expected_data()
        actual_df = pd.read_csv(uploaded_file)
        
        # --- NEW: AUTO-MAPPING LOGIC ---
        # Look for columns that sound like 'ID' and 'Actual'
        cols = [str(c).upper() for c in actual_df.columns]
        
        if 'ID' in cols and 'ACTUAL' in cols:
            results = run_qc_process(expected_df, actual_df, threshold)
            
            # Dashboard Metrics
            fails = len(results[results['QC_RESULT'] == '⚠️ FAIL'])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Records", len(results))
            c2.metric("Discrepancies", fails, delta=f"{fails} alerts", delta_color="inverse")
            c3.metric("Threshold", f"{threshold}%")

            # Table Output
            st.subheader("Validation Table")
            st.dataframe(
                results.style.format({
                    'EXPECTED': '${:,.2f}', 
                    'ACTUAL': '${:,.2f}', 
                    'VARIANCE': '${:,.2f}', 
                    'VARIANCE_%': '{:.2f}%'
                })
            )
            
            csv_output = results.to_csv(index=False).encode('utf-8')
            st.download_button("Export Results", csv_output, "qc_report.csv", "text/csv")
        else:
            # Helpful error message showing what the app actually sees
            st.error(f"""
            **Error:** Required columns not found. 
            - Looking for: `ID` and `Actual`
            - Found in your file: `{list(actual_df.columns)}`
            """)
            st.info("💡 Please rename your CSV columns to 'ID' and 'Actual' and re-upload.")

if __name__ == "__main__":
    main()