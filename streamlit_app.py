import streamlit as st
import pandas as pd
from openai import OpenAI

import time
from io import BytesIO

# Streamlit app
def main():
    st.title("OpenAI CSV/Excel Processor")

    # Input fields for OpenAI API Key and file upload
    openai_key = st.text_input("Enter your OpenAI API Key", type="password")
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])


    if openai_key and uploaded_file:
        client = OpenAI(api_key=openai_key)

        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        # Check if the dataframe is valid
        if df.empty or df.shape[1] < 1:
            st.error("The uploaded file must have at least one column with data.")
            return

        # Set OpenAI API key

        # Initialize an empty list to store OpenAI responses
        responses = []

        # Display progress bar
        progress_bar = st.progress(0)
        total_rows = len(df)

        # Iterate over the first column and send each cell to OpenAI
        for idx, value in enumerate(df['instructions']):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": value
                        }
                    ]
                )
                responses.append(response.choices[0].message.content)
            except Exception as e:
                responses.append(f"Error: {e}")

            # Update progress bar
            progress_bar.progress((idx + 1) / total_rows)
            time.sleep(0.1)  # To avoid rate limiting

        # Add the responses as a new column to the dataframe
        df['OpenAI Response'] = responses

        # Allow the user to download the updated file
        output = BytesIO()
        if uploaded_file.name.endswith('.csv'):
            df.to_csv(output, index=False)
            output_filename = "openai_responses.csv"
        elif uploaded_file.name.endswith('.xlsx'):
            df.to_excel(output, index=False, engine='xlsxwriter')
            output_filename = "openai_responses.xlsx"

        st.download_button(
            label="Download Output File",
            data=output.getvalue(),
            file_name=output_filename,
            mime="text/csv" if uploaded_file.name.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
