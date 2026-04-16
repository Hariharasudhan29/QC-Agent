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
    """
    Mock function for Expected Values. 
    In production, this would use GoogleAdsClient to fetch live data.
    """
    data = {
        'ID': ['CAM-01', 'CAM-02', 'CAM-03', 'CAM-04', 'CAM-05'],
        'Expected': [1200.50, 4500.00, 300.00, 1500.00, 890.20]
    }
    return pd.DataFrame(data)

# --- 3. QC ENGINE LOGIC ---
def run_qc_process(expected_df, actual_df, limit):
    # Join the datasets on ID
    merged = pd.merge(expected_df, actual_df, on='ID', how='inner')
    
    # Calculate Variance
    merged['Variance'] = merged['Actual'] - merged['Expected']
    merged['Variance_%'] = (merged['Variance'] / merged['Expected']) * 100
    
    # Validation Logic
    merged['QC_Result'] = np.where(
        merged['Variance_%'].abs() <= limit, 
        '✅ PASS', 
        '⚠️ FAIL'
    )
    return merged

# --- 4. STREAMLIT DASHBOARD UI ---
def main():
    st.set_page_config(page_title="AI QC Agent", layout="wide")
    st.title("🛡️ QC AI Agent: Variance Validator")

    # Sidebar
    st.sidebar.header("Agent Settings")
    threshold = st.sidebar.slider("Tolerance Threshold (%)", 0.0, 15.0, 5.0)
    
    # API Status Warning
    if not HAS_GOOGLE_ADS:
        st.sidebar.warning("Note: Google Ads Library not detected. Running in Mock Mode.")

    uploaded_file = st.sidebar.file_uploader("Upload Actual Values (CSV)", type="csv")

    if uploaded_file:
        # Load Data
        expected_df = get_expected_data()
        actual_df = pd.read_csv(uploaded_file)
        
        # Check Columns
        if 'ID' in actual_df.columns and 'Actual' in actual_df.columns:
            results = run_qc_process(expected_df, actual_df, threshold)
            
            # Metrics
            fails = len(results[results['QC_Result'] == '⚠️ FAIL'])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Records", len(results))
            c2.metric("Discrepancies", fails, delta=f"{fails} alerts", delta_color="inverse")
            c3.metric("Threshold", f"{threshold}%")

            # Result Table
            st.subheader("QC Validation Results")
            st.dataframe(
                results.style.format({
                    'Expected': '${:,.2f}', 
                    'Actual': '${:,.2f}', 
                    'Variance': '${:,.2f}', 
                    'Variance_%': '{:.2f}%'
                })
            )
            
            # Export
            csv_output = results.to_csv(index=False).encode('utf-8')
            st.download_button("Download QC Report", csv_output, "qc_results.csv", "text/csv")
        else:
            st.error("CSV error: Please ensure headers 'ID' and 'Actual' are present.")
    else:
        st.info("👋 Upload your 'actual.csv' to begin the QC check.")

if __name__ == "__main__":
    main()