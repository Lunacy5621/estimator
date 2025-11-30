import streamlit as st
import sqlite3
from datetime import datetime
from pathlib import Path

# --- DATABASE SETUP ---
DB_PATH = Path(__file__).parent / "quotes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            job_type TEXT,
            job_category TEXT,
            price_low REAL,
            price_high REAL,
            notes TEXT,
            status TEXT DEFAULT 'quoted'
        )
    ''')
    conn.commit()
    conn.close()

def save_quote(customer_name, customer_phone, job_type, job_category, price_low, price_high, notes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO quotes (created_at, customer_name, customer_phone, job_type, job_category, price_low, price_high, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), customer_name, customer_phone, job_type, job_category, price_low, price_high, notes))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# --- PRICING DATA ---
FIXED_JOBS = {
    "Electrical": {
        "Ceiling fan install": 150,
        "Outlet replacement/repair": 120,
        "Light switch replacement": 120,
        "Light fixture": 120,
        "Replace breaker": 120,
    },
    "Plumbing": {
        "Faucet replacement": 150,
        "Garbage disposal replacement": 200,
        "Toilet repair/replacement": 300,
        "Kitchen sink install": 300,
    },
    "Other": {
        "Door lock replacement": 120,
        "TV wall mounting": 120,
        "Picture hanging/mirrors": 120,
        "Fire alarm battery/unit": 120,
        "A/C filter replace": 120,
    }
}

VARIABLE_JOBS = {
    "Drywall Repair": {
        "Small patch (under 1 sq ft)": {"type": "flat", "price": 150},
        "Large drywall repair": {"type": "sqft", "low": 25, "high": 25, "min": 120},
    },
    "Painting": {
        "Interior paint": {"type": "sqft", "low": 1.50, "high": 3.50, "min": 120},
    },
    "Flooring": {
        "LVP flooring (click-lock)": {"type": "sqft", "low": 1.50, "high": 4.00, "min": 500},
        "Tile install": {"type": "sqft", "low": 4.00, "high": 12.00, "min": 500},
        "Tile removal": {"type": "sqft", "low": 2.50, "high": 5.00, "min": 500},
        "Baseboards": {"type": "linear_ft", "low": 1.50, "high": 4.00, "min": 120},
    }
}

PAINT_MODIFIERS = {
    "Ceilings included": 150,
    "Dark to light (extra coats)": 100,
    "High ceilings (ladder work)": 100,
    "Trim/baseboards painted": 150,
    "Wallpaper removal first": 200,
    "Multiple colors (per extra color)": 75,
    "Customer supplies paint (+25% markup)": 0,  # Handled separately
}

# --- APP UI ---
st.set_page_config(page_title="LV Handyman Pro - Estimator", page_icon="🔧", layout="centered")

st.title("🔧 LV Handyman Pro")
st.subheader("Job Estimator")

# Customer info section
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("Customer Name", placeholder="Optional")
with col2:
    customer_phone = st.text_input("Phone", placeholder="Optional")

# Job type selection
st.markdown("---")
job_category = st.selectbox(
    "Job Category",
    ["-- Select --", "Electrical", "Plumbing", "Other", "Drywall Repair", "Painting", "Flooring"]
)

price_low = 0
price_high = 0
job_type = ""
notes = ""

if job_category in FIXED_JOBS:
    # Fixed price jobs
    jobs = list(FIXED_JOBS[job_category].keys())
    job_type = st.selectbox("Job Type", ["-- Select --"] + jobs)
    
    if job_type != "-- Select --":
        price = FIXED_JOBS[job_category][job_type]
        price_low = price
        price_high = price
        
        st.markdown("---")
        st.success(f"## 💰 ${price}")
        st.caption("Fixed price")

elif job_category == "Drywall Repair":
    job_type = st.selectbox("Job Type", ["-- Select --", "Small patch (under 1 sq ft)", "Large drywall repair"])
    
    if job_type == "Small patch (under 1 sq ft)":
        price_low = 150
        price_high = 150
        st.markdown("---")
        st.success(f"## 💰 $150")
        st.caption("Includes texture match")
        
    elif job_type == "Large drywall repair":
        sqft = st.number_input("Square feet", min_value=1, value=10)
        
        price_low = max(120, sqft * 25)
        price_high = price_low
        
        st.markdown("---")
        st.success(f"## 💰 ${price_low:,.0f}")
        st.caption(f"{sqft} sq ft × $25/sq ft (includes removal, install, texture, paint, materials)")

elif job_category == "Painting":
    job_type = "Interior paint"
    
    sqft = st.number_input("Wall square footage", min_value=1, value=200, 
                           help="Tip: Average room is 150-250 sq ft of wall space")
    
    st.markdown("**Modifiers:**")
    
    modifiers_selected = []
    modifier_total = 0
    
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("Ceilings included (+$150)"):
            modifiers_selected.append("Ceilings")
            modifier_total += 150
        if st.checkbox("Dark to light (+$100)"):
            modifiers_selected.append("Dark to light")
            modifier_total += 100
        if st.checkbox("High ceilings (+$100)"):
            modifiers_selected.append("High ceilings")
            modifier_total += 100
    with col2:
        if st.checkbox("Trim/baseboards (+$150)"):
            modifiers_selected.append("Trim/baseboards")
            modifier_total += 150
        if st.checkbox("Wallpaper removal (+$200)"):
            modifiers_selected.append("Wallpaper removal")
            modifier_total += 200
    
    extra_colors = st.number_input("Extra colors (beyond 1)", min_value=0, value=0)
    if extra_colors > 0:
        modifiers_selected.append(f"{extra_colors} extra colors")
        modifier_total += extra_colors * 75
    
    base_low = sqft * 1.50
    base_high = sqft * 3.50
    
    price_low = max(120, base_low + modifier_total)
    price_high = max(120, base_high + modifier_total)
    
    notes = ", ".join(modifiers_selected) if modifiers_selected else ""
    
    st.markdown("---")
    if price_low == price_high:
        st.success(f"## 💰 ${price_low:,.0f}")
    else:
        st.success(f"## 💰 ${price_low:,.0f} - ${price_high:,.0f}")
    
    st.caption(f"{sqft} sq ft × $1.50-$3.50/sq ft" + (f" + ${modifier_total} modifiers" if modifier_total > 0 else ""))
    
    if price_low != price_high:
        st.info("**Low:** One coat, light colors, easy access\n\n**High:** Two coats, dark-to-light, more prep")

elif job_category == "Flooring":
    flooring_jobs = list(VARIABLE_JOBS["Flooring"].keys())
    job_type = st.selectbox("Job Type", ["-- Select --"] + flooring_jobs)
    
    if job_type != "-- Select --":
        job_data = VARIABLE_JOBS["Flooring"][job_type]
        
        if job_data["type"] == "sqft":
            sqft = st.number_input("Square feet", min_value=1, value=100)
            
            raw_low = sqft * job_data["low"]
            raw_high = sqft * job_data["high"]
            
            price_low = max(job_data["min"], raw_low)
            price_high = max(job_data["min"], raw_high)
            
            st.markdown("---")
            st.success(f"## 💰 ${price_low:,.0f} - ${price_high:,.0f}")
            st.caption(f"{sqft} sq ft × ${job_data['low']:.2f}-${job_data['high']:.2f}/sq ft (min ${job_data['min']})")
            
        elif job_data["type"] == "linear_ft":
            linear_ft = st.number_input("Linear feet", min_value=1, value=50)
            
            raw_low = linear_ft * job_data["low"]
            raw_high = linear_ft * job_data["high"]
            
            price_low = max(job_data["min"], raw_low)
            price_high = max(job_data["min"], raw_high)
            
            st.markdown("---")
            st.success(f"## 💰 ${price_low:,.0f} - ${price_high:,.0f}")
            st.caption(f"{linear_ft} linear ft × ${job_data['low']:.2f}-${job_data['high']:.2f}/ft (min ${job_data['min']})")

# Save quote button
if price_low > 0:
    st.markdown("---")
    notes_input = st.text_input("Notes (optional)", value=notes, placeholder="Any special details...")
    
    if st.button("💾 Save Quote", type="primary", use_container_width=True):
        save_quote(customer_name, customer_phone, job_type, job_category, price_low, price_high, notes_input)
        st.success("✅ Quote saved!")
        st.balloons()

# Footer
st.markdown("---")
st.caption("LV Handyman Pro • Minimum job: $120 • Flooring minimum: $500")
