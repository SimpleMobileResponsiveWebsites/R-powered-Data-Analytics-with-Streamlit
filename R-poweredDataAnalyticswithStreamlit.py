import streamlit as st
import pandas as pd
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

# Activate the automatic conversion between R and Pandas data structures
pandas2ri.activate()

# Import R packages
ggplot2 = importr('ggplot2')
dplyr = importr('dplyr')
base = importr('base')
data_table = importr('data.table')

# Define functions to run R code
def run_r_code(code):
    """Run raw R code as a string and return results."""
    return ro.r(code)

def load_dataset():
    """Load a sample dataset or allow users to upload their own."""
    st.sidebar.title("Dataset Options")
    sample_data = st.sidebar.selectbox("Choose a sample dataset", ["mtcars", "iris", "Upload CSV"])
    
    if sample_data == "mtcars":
        df = ro.r('mtcars')
    elif sample_data == "iris":
        df = ro.r('iris')
    else:
        uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            return df
        else:
            st.warning("Please upload a CSV file.")
            return None

    return pandas2ri.rpy2py(df)

def filter_data(df):
    """Apply filters on the dataset using R's dplyr package."""
    st.sidebar.title("Data Filters")
    filter_column = st.sidebar.selectbox("Select column to filter", df.columns)
    unique_values = df[filter_column].unique()
    selected_values = st.sidebar.multiselect("Select values", unique_values)

    if selected_values:
        # Convert selections to an R-friendly format and apply filter
        selected_values_r = ro.StrVector(selected_values)
        r_df = pandas2ri.py2rpy(df)
        filtered_df = r("dplyr::filter")(r_df, ro.Formula(f"{filter_column} %in% selected_values_r"))
        return pandas2ri.rpy2py(filtered_df)
    else:
        return df

def plot_data(df):
    """Plot the data using ggplot2 in R."""
    st.subheader("Data Visualization")
    x_column = st.selectbox("Select X-axis", df.columns)
    y_column = st.selectbox("Select Y-axis", df.columns)
    plot_type = st.selectbox("Select plot type", ["Scatter plot", "Bar plot"])

    if plot_type == "Scatter plot":
        code = f"""
        library(ggplot2)
        ggplot(data=mtcars, aes(x={x_column}, y={y_column})) + geom_point() + theme_minimal()
        """
    elif plot_type == "Bar plot":
        code = f"""
        library(ggplot2)
        ggplot(data=mtcars, aes(x={x_column}, y={y_column})) + geom_bar(stat="identity") + theme_minimal()
        """
    # Render plot
    result = run_r_code(code)
    st.pyplot(result)

def show_summary(df):
    """Display a summary of the dataset using R."""
    st.subheader("Dataset Summary")
    r_df = pandas2ri.py2rpy(df)
    summary = r("summary")(r_df)
    st.text(summary)

def main():
    st.title("R-powered Data Analytics with Streamlit")
    
    # Load dataset
    df = load_dataset()
    if df is None:
        st.stop()
    
    # Show summary
    show_summary(df)
    
    # Filter dataset
    filtered_df = filter_data(df)
    
    # Display filtered dataset
    st.subheader("Filtered Data")
    st.write(filtered_df)
    
    # Plot data
    plot_data(filtered_df)

if __name__ == "__main__":
    main()
