import streamlit as st
import pandas as pd

# 1. Configure the page to use the full screen width
st.set_page_config(layout="wide", page_title="My Data Dashboard")

st.title("📊 My Custom Data Dashboard")

# --- HELPER FUNCTION: Load Data efficiently ---
# This stops the app from re-loading the 200MB file every time you click a button
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
# Note: The server limit must be set in config.toml or via command line for files >200MB
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type="csv")

# --- MAIN PAGE ---
if uploaded_file is not None:
    try:
        # Load the data using the cached function
        with st.spinner('Loading data...'):
            df = load_data(uploaded_file)
        
        # --- METRICS SECTION ---
        # Show basic info at the top
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", f"{df.shape[0]:,}") # Adds comma separator (e.g. 135,391)
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", df.isna().sum().sum())

        # --- PREVIEW SECTION ---
        with st.expander("Values Preview (Click to expand)", expanded=False):
            st.dataframe(df.head())

        # --- PLOTTING SECTION ---
        st.divider()
        st.subheader("Visualize Your Data")
        
        # Identify column types automatically
        numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            # Layout the dropdowns
            c1, c2, c3 = st.columns(3)
            
            # 1. Select X-Axis (e.g., Time/Week)
            # We try to auto-select 'wm_yr_wk' if it exists
            default_x = all_cols.index("wm_yr_wk") if "wm_yr_wk" in all_cols else 0
            x_axis = c1.selectbox("X-Axis (Time)", all_cols, index=default_x)

            # 2. Select Y-Axis (e.g., Supply/Inventory)
            # We try to auto-select 'Week_of_Supply' if it exists
            default_y = numeric_cols.index("Week_of_Supply") if "Week_of_Supply" in numeric_cols else 0
            y_axis = c2.selectbox("Y-Axis (Value)", numeric_cols, index=default_y)
            
            # 3. Select Color/Grouping (e.g., Item Number)
            # We try to auto-select 'walmart_item_number' if it exists
            default_color = all_cols.index("walmart_item_number") if "walmart_item_number" in all_cols else 0
            color_col = c3.selectbox("Color Code By", all_cols, index=default_color)

            # --- FILTER LOGIC ---
            # Crucial for large files: We must filter specific items to avoid a "rainbow mess"
            st.write(f"### Filter by {color_col}")
            st.info(f"Select specific items to compare. Showing top 5 by default.")
            
            unique_items = df[color_col].unique()
            
            # Pre-select the first 5 items so the chart isn't empty on load
            selected_items = st.multiselect(
                f"Choose specific {color_col}s to view:",
                options=unique_items,
                default=unique_items[:5]
            )

            if selected_items:
                # Filter data to only selected items
                filtered_df = df[df[color_col].isin(selected_items)]

                # PIVOT THE DATA
                # This reshapes the data so Streamlit knows how to stack/color the bars
                # Rows = X-axis, Columns = Colors, Values = Y-axis
                chart_data = filtered_df.pivot_table(
                    index=x_axis,
                    columns=color_col,
                    values=y_axis,
                    aggfunc='sum'
                )
                
                # Plot the chart
                st.bar_chart(chart_data)
                
                # Optional: Show the data used for the chart
                with st.expander("See chart data"):
                    st.dataframe(chart_data)
            else:
                st.warning("Please select at least one item from the box above to generate the chart.")

        else:
            st.warning("No numeric columns found in this CSV to plot.")
            
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👈 Waiting for you to upload a CSV file in the sidebar.")

