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
        'Campaign_ID': ['CAM-01', 'CAM-02', 'CAM-03', 'CAM-04', 'CAM-05'],
        'Expected_Value': [1200.50, 4500.00, 300.00, 1500.00, 890.20]
    }
    return pd.DataFrame(data)

# --- QC ENGINE LOGIC ---
class QCAgent:
    def __init__(self, expected_df, actual_df, threshold):
        self.expected = expected_df
        self.actual = actual_df
        self.threshold = threshold

    def validate(self):
        # Merge data on ID
        merged = pd.merge(self.expected, self.actual, on='Campaign_ID', how='inner')
        
        # Calculations
        merged['Variance'] = merged['Actual_Value'] - merged['Expected_Value']
        merged['Variance_Pct'] = (merged['Variance'] / merged['Expected_Value']) * 100
        
        # Threshold Validation
        merged['QC_Status'] = np.where(
            merged['Variance_Pct'].abs() <= self.threshold, 
            'PASS', 
            'FAIL'
        )
        return merged

# --- STREAMLIT DASHBOARD ---
def main():
    st.set_page_config(page_title="AI QC Checker", layout="wide")
    st.title("🤖 QC AI Agent: Google Ads vs CSV")
    
    st.sidebar.header("Configuration")
    customer_id = st.sidebar.text_input("Google Ads Customer ID", "123-456-7890")
    tolerance = st.sidebar.slider("Tolerance Threshold (%)", 0.0, 20.0, 5.0)
    
    uploaded_file = st.sidebar.file_uploader("Upload Actuals CSV", type="csv")

    if uploaded_file:
        # Load Data
        expected_df = get_expected_values(None, customer_id)
        actual_df = pd.read_csv(uploaded_file)

        # Basic Check: Ensure columns exist
        if 'Campaign_ID' in actual_df.columns and 'Actual_Value' in actual_df.columns:
            
            # Run Agent
            agent = QCAgent(expected_df, actual_df, tolerance)
            results = agent.validate()

            # Display KPIs
            pass_count = len(results[results['QC_Status'] == 'PASS'])
            fail_count = len(results[results['QC_Status'] == 'FAIL'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Campaigns", len(results))
            col2.metric("Passed", pass_count)
            col3.metric("Failed", fail_count, delta=f"{fail_count}", delta_color="inverse")

            # Publication Table
            st.subheader("QC Validation Results")
            
            def style_status(row):
                return ['background-color: #d4edda' if row.QC_Status == 'PASS' else 'background-color: #f8d7da'] * len(row)

            st.dataframe(
                results.style.apply(style_status, axis=1)
                .format({'Expected_Value': '${:,.2f}', 'Actual_Value': '${:,.2f}', 'Variance_Pct': '{:.2f}%'})
            )

            # Download Result
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button("Export QC Report", csv, "qc_report.csv", "text/csv")
        else:
            st.error("CSV must have 'Campaign_ID' and 'Actual_Value' columns.")
    else:
        st.info("Awaiting CSV upload to run validation...")

if __name__ == "__main__":
    main()