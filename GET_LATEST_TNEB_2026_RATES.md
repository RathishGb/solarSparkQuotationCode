# Getting Latest TNEB 2026 Rates - Complete Guide

## Current System Status

✅ **Currently Using:** FY 2025-26 Rates (April 1, 2025 - March 31, 2026)  
📅 **Today's Date:** April 24, 2026  
❓ **Need:** FY 2026-27 Rates (if released after April 1, 2026)

---

## What Changed on April 1, 2026?

On this date, TNEB released **FY 2026-27 tariff rates** (if following the annual schedule). You need to:

1. **Check if new rates are official**
2. **Get exact values from TNEB**
3. **Update your system**

---

## Official TNEB Rate Sources

### Primary - TNEB Official Website

**URL:** https://www.tneb.in

**Steps:**
1. Click on "Tariff" or "Consumer Info"
2. Look for "Schedule of Charges 2026-27"
3. Download the official **Tariff Order PDF**
4. Find the rates for:
   - ✓ Domestic
   - ✓ Commercial (Non-Domestic)
   - ✓ Agricultural
   - ✓ Net Metering rates

### Secondary Sources

- **TNEB Consumer Portal:** https://portal.tneb.nic.in (login with EB number)
- **Tamil Nadu Government:** https://www.tamil.gov.in  
- **Energy News:** Search "TNEB tariff 2026" in The Hindu, Business Today
- **Notifications:** Check official Government Gazette notices

---

## Current Rate Configuration in System

### Domestic (4 Slabs)
```
Slab 1:   0-100 units    @ Rs 3.00/unit  + Rs 30 fixed
Slab 2: 101-200 units    @ Rs 6.00/unit  + Rs 30 fixed
Slab 3: 201-300 units    @ Rs 7.50/unit  + Rs 50 fixed
Slab 4: 301+ units       @ Rs 9.50/unit  + Rs 75 fixed
```

### Commercial (4 Slabs)
```
Slab 1:   0-100 units    @ Rs 4.50/unit  + Rs 50 fixed
Slab 2: 101-200 units    @ Rs 7.50/unit  + Rs 50 fixed
Slab 3: 201-500 units    @ Rs 9.50/unit  + Rs 100 fixed
Slab 4: 501+ units       @ Rs 11.50/unit + Rs 150 fixed
```

### Agricultural (4 Slabs)
```
Slab 1:   0-50 units     @ Rs 0.50/unit  + Rs 50 fixed
Slab 2:  51-100 units    @ Rs 1.50/unit  + Rs 50 fixed
Slab 3: 101-200 units    @ Rs 3.50/unit  + Rs 75 fixed
Slab 4: 201+ units       @ Rs 5.50/unit  + Rs 100 fixed
```

### Net Metering Credits
- Domestic: Rs 8.50/unit
- Commercial: Rs 9.50/unit  
- Agricultural: Rs 5.50/unit

---

## How to Verify Current Rates Are Correct

### Method 1: Run Verification Tool

```bash
cd d:\solarQuoteGithubRepo\solarSparkQuotationCode
.\.venv\Scripts\python tneb_rate_verification.py
```

Choose option **2** to verify with your own TNEB bill.

### Method 2: Manual Calculation Comparison

**Your recent TNEB bill:**
- Monthly consumption: 220 units
- Your actual bill: Rs X

**Our system calculation:**
```
Slab 1 (0-100): 100 × Rs 3.00 = Rs 300
Slab 2 (101-200): 100 × Rs 6.00 = Rs 600  
Slab 3 (201-220): 20 × Rs 7.50 = Rs 150
Fixed: Rs 50
Subtotal: Rs 1,100
GST (5%): Rs 55
Total: Rs 1,155
```

If your bill is ≈ Rs 1,155, rates are **accurate** ✅  
If your bill is significantly different, rates need **updating** ❌

---

## Step-by-Step Update Process

### Step 1: Get Official Rates

```
TNEB Website → Tariff Schedule → Download PDF for 2026-27
```

Collect:
- [ ] Domestic rates for all 4 slabs
- [ ] Commercial rates for all 4 slabs
- [ ] Agricultural rates for all 4 slabs
- [ ] Fixed charges for each
- [ ] Net metering credit rates

### Step 2: Update Code File

Edit: `tneb_rate_slabs.py`

Find section: `DOMESTIC_RATE_SLABS = [`

Replace rates in each slab:
```python
{
    "slab_name": "Slab 1",
    "from_units": 0,
    "to_units": 100,
    "rate_per_unit": 3.00,  # ← UPDATE THIS
    "fixed_charge_monthly": 30,  # ← UPDATE THIS
    "description": "0-100 units (subsidized slab)"
}
```

### Step 3: Run Tests

```bash
.\.venv\Scripts\python test_tneb_integration.py
```

All tests should still pass ✅

### Step 4: Verify with Your Bill

```bash
.\.venv\Scripts\python tneb_rate_verification.py
```

Choose option 2, enter your bill details, check accuracy.

### Step 5: Update Documentation

Update these files with new rates:
- `TNEB_RATES_REFERENCE.md` - Update rate tables
- `tneb_rate_slabs.py` - Update comments with "FY 2026-27"
- `AI_AGENT_README.md` - Update example calculations

### Step 6: Commit & Deploy

```bash
git add tneb_rate_slabs.py TNEB_RATES_REFERENCE.md
git commit -m "Update TNEB rates for FY 2026-27"
git push
```

---

## Troubleshooting

### Problem 1: Can't find rates on TNEB website

**Solution:**
- Rates usually released 1-2 weeks after April 1
- Check again in mid-April
- Call TNEB customer care: 197 (toll-free)
- Check local news for latest tariff updates

### Problem 2: Rates are very different from current

**Solution:**
- Double-check TNEB website - ensure you have correct fiscal year (2026-27)
- Verify you're reading domestic vs commercial correctly
- Check if includes GST (usually it does)
- Calculate sample bill manually to confirm

### Problem 3: Your AI agent gives wrong recommendations

**Possible causes:**
- Rates not updated after April 1, 2026
- Outdated slab information
- Different consumer category

**Fix:**
1. Run verification tool
2. Compare calculated vs actual bill
3. If different > 5%, update rates immediately
4. Re-run AI agent analysis

---

## Automated Check Script

Run this monthly to check for rate changes:

```python
# check_rates_monthly.py
from datetime import datetime
from tneb_rate_verification import verify_with_known_bill

if datetime.now().month in [4]:  # April only
    print("⚠️  It's rate update season!")
    print("Please verify current rates...")
    verify_with_known_bill()
```

---

## Reference Rates History

| FY | Domestic Slab 4 | Commercial Slab 4 | Last Updated |
|----|-----------------|-------------------|--------------|
| 2024-25 | Rs 9.00 | Rs 11.00 | Apr 2024 |
| 2025-26 | Rs 9.50 | Rs 11.50 | Apr 2025 |
| 2026-27 | Rs ??.?? | Rs ??.?? | Apr 2026 |

*Update as you get official rates*

---

## Key Dates to Remember

- **April 1, 2026:** New rates effective (FY 2026-27)
- **April 24, 2026:** TODAY - You should check for updates!
- **March 31, 2027:** Current rates expire
- **April 1, 2027:** Next rate revision

---

## Quick Links for Implementation

| Task | File | Action |
|------|------|--------|
| See current rates | `tneb_rate_slabs.py` | View `DOMESTIC_RATE_SLABS` array |
| Update rates | `tneb_rate_slabs.py` | Edit rate values and fixed charges |
| Test changes | Terminal | Run `test_tneb_integration.py` |
| Verify accuracy | Terminal | Run `tneb_rate_verification.py` |
| View reference | `TNEB_RATES_REFERENCE.md` | Check rate tables section |

---

## Next Steps

1. ✅ **Now:** Visit TNEB website, check for 2026-27 rates
2. ⏭️ **If new rates exist:** Update `tneb_rate_slabs.py`
3. ⏭️ **Run:** Test suite to verify
4. ⏭️ **Verify:** With your own TNEB bill
5. ⏭️ **Deploy:** Update AI agent with new rates

---

**Questions?**

- TNEB Customer Care: 197 (toll-free)
- TNEB Website: https://www.tneb.in
- Consumer Portal: https://portal.tneb.nic.in

---

**Version:** 1.0  
**Last Updated:** April 24, 2026  
**Status:** Ready to update for FY 2026-27 rates
