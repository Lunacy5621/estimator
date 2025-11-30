import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "quotes.db"

st.set_page_config(page_title="Quote History - LV Handyman Pro", page_icon="📋", layout="wide")

st.title("📋 Quote History")

def get_quotes():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('''
        SELECT 
            id,
            created_at,
            customer_name,
            customer_phone,
            job_category,
            job_type,
            price_low,
            price_high,
            notes,
            status
        FROM quotes 
        ORDER BY created_at DESC
    ''', conn)
    conn.close()
    return df

def update_status(quote_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE quotes SET status = ? WHERE id = ?', (new_status, quote_id))
    conn.commit()
    conn.close()

def delete_quote(quote_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM quotes WHERE id = ?', (quote_id,))
    conn.commit()
    conn.close()

try:
    df = get_quotes()
    
    if len(df) == 0:
        st.info("No quotes yet. Go create some!")
    else:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Quotes", len(df))
        with col2:
            won = len(df[df['status'] == 'won'])
            st.metric("Won", won)
        with col3:
            lost = len(df[df['status'] == 'lost'])
            st.metric("Lost", lost)
        with col4:
            if won + lost > 0:
                close_rate = (won / (won + lost)) * 100
                st.metric("Close Rate", f"{close_rate:.0f}%")
            else:
                st.metric("Close Rate", "N/A")
        
        st.markdown("---")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by status", ["All", "quoted", "won", "lost"])
        with col2:
            category_filter = st.selectbox("Filter by category", ["All"] + list(df['job_category'].unique()))
        
        # Apply filters
        filtered_df = df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['job_category'] == category_filter]
        
        st.markdown("---")
        
        # Display quotes
        for idx, row in filtered_df.iterrows():
            with st.expander(f"**{row['job_type']}** - ${row['price_low']:,.0f}" + (f"-${row['price_high']:,.0f}" if row['price_high'] != row['price_low'] else "") + f" | {row['status'].upper()}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Customer:** {row['customer_name'] or 'N/A'}")
                    st.write(f"**Phone:** {row['customer_phone'] or 'N/A'}")
                    st.write(f"**Category:** {row['job_category']}")
                with col2:
                    st.write(f"**Date:** {row['created_at'][:10]}")
                    st.write(f"**Notes:** {row['notes'] or 'None'}")
                
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("✅ Won", key=f"won_{row['id']}"):
                        update_status(row['id'], 'won')
                        st.rerun()
                with col2:
                    if st.button("❌ Lost", key=f"lost_{row['id']}"):
                        update_status(row['id'], 'lost')
                        st.rerun()
                with col3:
                    if st.button("🔄 Reset", key=f"reset_{row['id']}"):
                        update_status(row['id'], 'quoted')
                        st.rerun()
                with col4:
                    if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                        delete_quote(row['id'])
                        st.rerun()

except Exception as e:
    st.error(f"Database not found or error: {e}")
    st.info("Create some quotes first from the main estimator page.")

st.markdown("---")
st.caption("LV Handyman Pro • Quote Tracking")
