# QC-Agent
It does compare actual vs expected value
# 🛡️ QC AI Agent: Variance Reconciliation Engine

This project is a high-performance Quality Control (QC) Agent built with Python and Streamlit. It automates the reconciliation process by comparing "Expected" values from Google Ads API with "Actual" values from CSV uploads mimicing the mocking environment.

## 🚀 OVERVIEW
The agent performs three primary tasks:
1. Ingestion: Pulls benchmark data from Google Ads (as a mocking environment) or simply local CSV performance records.
2. Validation: Calculates the variance ($) and variance percentage (%) between sources.
3. Publication: Assigns a PASS or FAIL status based on a user-defined Tolerance Threshold.

## 📁 FOLDER STRUCTURE
qc-agent-app/
├── quality_check_app.py  # Main Python/Streamlit code
├── actual.csv            # Your CSV data (ID, Actual)
└── README.txt            # This documentation file

## 🛠️ INSTALLATION (Run in VS Code Terminal)
1. Install the required libraries:
   pip install streamlit pandas numpy google-ads

2. Run the dashboard:
   streamlit run app.py

## 📊 QC LOGIC
- PASS: If the difference between Expected and Actual is WITHIN the threshold.
- FAIL: If the difference EXCEEDS the threshold.

## 📥 EXPORTING
Once the validation is complete, use the "Print" button in the top right of the dashboard to download the finalized audit trail as PDF.

## APP link: https://qc-agent-ntqlrqkvb5nyzyszcdeszo.streamlit.app/
