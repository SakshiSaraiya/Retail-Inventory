import streamlit as st
import mysql.connector
from mysql.connector import Error

# Establish MySQL connection using Streamlit secrets
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["host"],
            user=st.secrets["user"],
            password=st.secrets["password"],
            database=st.secrets["database"]
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Execute SELECT queries
def fetch_data(query, params=None):
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    return []

# Execute INSERT, UPDATE, DELETE queries
def execute_query(query, params=None):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return True
        except Error as e:
            st.error(f"Query execution error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False
