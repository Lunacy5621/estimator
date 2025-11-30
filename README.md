# LV Handyman Pro - Job Estimator

A simple, fast job estimator for Patty to quote customers instantly.

## Features

- **Fixed price jobs:** Electrical, Plumbing, Other (14 jobs total)
- **Variable jobs:** Drywall, Painting (with modifiers), Flooring
- **Quote logging:** Every quote saved to SQLite database
- **Quote tracking:** Mark quotes as Won/Lost, see close rate

## Quick Start (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Deploy to Streamlit Cloud (Free)

1. Create a GitHub account (if you don't have one)
2. Create a new repository and upload these files
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Sign in with GitHub
5. Click "New app"
6. Select your repository and `app.py`
7. Click "Deploy"

Your app will be live at `https://[your-app-name].streamlit.app`

## File Structure

```
lv_handyman_estimator/
├── app.py                    # Main estimator app
├── pages/
│   └── 1_Quote_History.py    # Quote tracking page
├── quotes.db                 # SQLite database (created automatically)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Pricing Summary

### Fixed Jobs ($120-$300)
- Electrical: Ceiling fan, outlets, switches, fixtures, breakers
- Plumbing: Faucets, garbage disposal, toilets, kitchen sink
- Other: Door locks, TV mounting, pictures, fire alarms, A/C filters

### Variable Jobs
- **Drywall:** $150 small patch, $25/sq ft large
- **Paint:** $1.50-$3.50/sq ft + modifiers
- **LVP Flooring:** $1.50-$4.00/sq ft (min $500)
- **Tile Install:** $4.00-$12.00/sq ft (min $500)
- **Tile Removal:** $2.50-$5.00/sq ft (min $500)
- **Baseboards:** $1.50-$4.00/linear ft (min $120)

### Minimums
- Standard minimum: $120
- Flooring minimum: $500

## Next Steps (Phase 2)

- [ ] Add travel fee modifier (15+ miles)
- [ ] Add rush/same-day pricing
- [ ] Add repeat customer discount
- [ ] Track actual job revenue vs quoted
- [ ] Add confidence scoring
