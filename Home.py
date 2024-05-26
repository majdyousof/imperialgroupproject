import streamlit as st

def main():
    # Set the title and layout of the dashboard
    st.title("Welcome to The Arrow!")
    st.text('Under construction :hammer:')
    st.sidebar.success("Select page above.")
    st.sidebar.image('images/logo.jpg', use_column_width='always')

if __name__ == "__main__":
    main()