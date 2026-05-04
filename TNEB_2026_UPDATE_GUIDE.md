# TNEB 2026 Rate Update Guide

## Current Status (April 2026)

The system currently uses **FY 2025-26 rates** which are active from April 1, 2025 to March 31, 2026.

Since today is **April 24, 2026**, check if new rates for **FY 2026-27** have been officially released by TNEB.

## Where to Find Latest TNEB Rates

### Official Sources

1. **TNEB Portal**
   - URL: https://www.tneb.in
   - Navigate to: Tariff → Schedule of Charges
   - Look for: "Tariff Order [Current Year]"

2. **TNEB e-Services**
   - URL: https://tneb.nic.in
   - Check: Consumer Information → Tariff Rates

3. **TNEB Consumer Portal** 
   - Login with your EB number
   - View your bill details (shows current applicable rates)
   - Check rate comparison section

### News & Government Sources

4. **The Hindu - Business Section**
   - Search: "TNEB tariff 2026"
   - Usually published in March-April

5. **Tamil Nadu Government Portal**
   - https://www.tamil.gov.in
   - Energy Department → Electricity

6. **TNEBGOV Updates**
   - Official TNEB notifications
   - Tariff order PDFs released annually

## How to Update Rates in Your Code

### Step 1: Get Latest Official Rates

Visit TNEB portal and note the rates for:
- Domestic (Residential) - Slabs 1-4
- Commercial (Non-Domestic) - Slabs 1-4
- Agricultural - Slabs 1-4

Expected format:
```
Slab | Units From-To | Rate/Unit (Rs) | Fixed Charge (Rs)
```

### Step 2: Update `tneb_rate_slabs.py`

Replace the rate arrays with latest values:

```python
DOMESTIC_RATE_SLABS = [
    {
        "slab_name": "Slab 1",
        "from_units": 0,
        "to_units": 100,
        "rate_per_unit": 3.50,  # UPDATE THIS
        "fixed_charge_monthly": 35,  # UPDATE THIS
        "description": "0-100 units (subsidized slab)"
    },
    # ... continue for other slabs
]
```

### Step 3: Test Updates

Run the test script to verify:

```bash
cd d:\solarQuoteGithubRepo\solarSparkQuotationCode
.\.venv\Scripts\python test_tneb_integration.py
```

Check output matches your new rates.

### Step 4: Update Documentation

Update these files with new rates:
- `tneb_rate_slabs.py` - Rate values
- `TNEB_RATES_REFERENCE.md` - Reference tables
- `tneb_rate_slabs.py` main section comments

## FY 2026-27 Rates Placeholder

Once you get official rates from TNEB, update:

### Expected Updates (Typically April 2026)

```python
# Template for 2026-27 rates
DOMESTIC_RATE_SLABS_2026_27 = [
    {
        "slab_name": "Slab 1",
        "from_units": 0,
        "to_units": 100,
        "rate_per_unit": X.XX,  # Get from TNEB
        "fixed_charge_monthly": XX,  # Get from TNEB
        "description": "0-100 units"
    },
    {
        "slab_name": "Slab 2",
        "from_units": 101,
        "to_units": 200,
        "rate_per_unit": X.XX,
        "fixed_charge_monthly": XX,
    },
    # ... continue
]
```

## Quick Reference: What Changes in Tariff Order

When TNEB releases new rates, they typically change:

1. **Unit Rates** (Rs/kWh)
   - Usually increases by 3-8% per slab
   - Progressive structure maintained

2. **Fixed Charges** (Rs/month)
   - Increases with inflation
   - Different for each category

3. **Slab Limits**
   - Rarely changed (usually maintained)
   - Sometimes new slabs added

4. **Net Metering Rates**
   - Credit rates may change
   - Usually follows unit rate changes

5. **GST & Surcharges**
   - May be adjusted
   - Already included in unit rates

## Automatic Update Script

Create this to fetch latest rates annually:

```python
# update_rates.py - To be implemented for automation
def fetch_latest_tneb_rates():
    """
    Schedule this to run in March/April
    Fetch latest rates from TNEB portal
    Update rate_slabs.py automatically
    """
    pass
```

## Calculation Verification

After updating, verify with a known consumption:

```python
from tneb_rate_slabs import get_rate_for_consumption

# Test with 220 units (typical household)
rate = get_rate_for_consumption(220, "domestic")
print(f"Monthly Bill: Rs {rate['total_bill']}")

# Compare with your actual TNEB bill
# Should match approximately (±2% due to rounding)
```

## Key Dates for TNEB Rates

| Date | Event |
|------|-------|
| March 31, 2026 | End of FY 2025-26 |
| April 1, 2026 | New rates effective (FY 2026-27) |
| April 1, 2027 | Next rate revision |

---

**Action Required:**
1. Check TNEB website for FY 2026-27 official notification
2. Get exact rates for all categories
3. Update `tneb_rate_slabs.py` with new rates
4. Run tests to verify
5. Update reference documentation

**Current System Status:** ✅ Using FY 2025-26 rates (valid until March 31, 2027)
