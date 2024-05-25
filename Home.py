import streamlit as st

def main():
    # Set the title and layout of the dashboard
    st.title("Welcome to The Arrow!")

    st.sidebar.success("Select page above.")
    st.sidebar.title("Welcome!")
    st.sidebar.image('.\images\logo.jpg', use_column_width='always')

    # Add components to the sidebar
    st.sidebar.header("Options")
    option = st.sidebar.selectbox("Select an assessment method", ["Qualitative", "Quantitative"])

    # Add components to the main content area
    st.write(f"You selected: {option}")

if __name__ == "__main__":
    main()