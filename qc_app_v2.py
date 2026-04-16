import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATA INGESTION ---
def get_expected_data():
    data = {
        'ID': [101, 102, 103, 104, 105],
        'Expected': [1500.0, 2400.0, 500.0, 1200.0, 3000.0]
    }
    return pd.DataFrame(data)

# --- 2. QC ENGINE LOGIC ---
def run_qc_process(expected_df, actual_df, limit):
    # Standardize column names to uppercase
    actual_df.columns = [str(col).upper().strip() for col in actual_df.columns]
    expected_df.columns = [str(col).upper().strip() for col in expected_df.columns]

    # --- CRITICAL FIX: CONVERT ID TO STRING ---
    # This prevents the ValueError by ensuring both IDs are the same type
    expected_df['ID'] = expected_df['ID'].astype(str).str.strip()
    actual_df['ID'] = actual_df['ID'].astype(str).str.strip()

    # Merge data
    merged = pd.merge(expected_df, actual_df, on='ID', how='inner')
    
    # Check if merge actually found anything
    if merged.empty:
        return None

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

# --- 3. STREAMLIT DASHBOARD UI ---
def main():
    st.set_page_config(page_title="AI QC Agent", layout="wide")
    st.title("🛡️ QC AI Agent: Variance Validator")

    st.sidebar.header("Agent Settings")
    threshold = st.sidebar.slider("Tolerance Threshold (%)", 0.0, 15.0, 5.0)
    
    uploaded_file = st.sidebar.file_uploader("Upload Actual Values (CSV)", type="csv")

    if uploaded_file:
        expected_df = get_expected_data()
        actual_df = pd.read_csv(uploaded_file)
        
        # Identify columns (case-insensitive)
        cols = [str(c).upper().strip() for c in actual_df.columns]
        
        if 'ID' in cols and 'ACTUAL' in cols:
            results = run_qc_process(expected_df, actual_df, threshold)
            
            if results is not None and not results.empty:
                # Dashboard Metrics
                fails = len(results[results['QC_RESULT'] == '⚠️ FAIL'])
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Records", len(results))
                c2.metric("Discrepancies", fails, delta=f"{fails} alerts", delta_color="inverse")
                c3.metric("Threshold", f"{threshold}%")

                # Table Output
                st.subheader("Validation Table")
                st.dataframe(results)
            else:
                st.warning("⚠️ No matching IDs found between Expected data and your CSV. Check your ID values.")
        else:
            st.error(f"Required columns 'ID' and 'Actual' not found. Found: {list(actual_df.columns)}")

if __name__ == "__main__":
    main()