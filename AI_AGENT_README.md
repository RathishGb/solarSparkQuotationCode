# SolarSpark AI Agent - TNEB Integration Guide

## Overview

The SolarSpark AI Agent is an intelligent system that:
1. **Fetches TNEB Consumer Details** using EB number
2. **Analyzes Consumption Patterns** from historical monthly data
3. **Recommends Optimal Solar System Size** based on TNEB rate slabs
4. **Calculates Accurate Savings** using actual TNEB tariff rates

## Key Features

### 1. TNEB Rate Slab Integration

The system now uses **actuaNEB rate slabs** for Tamil Nadu:

#### Domestic Rate Slabs:
- **Slab 1 (0-100 units)**: Rs 3.00/unit + Rs 30/month fixed
- **Slab 2 (101-200 units)**: Rs 6.00/unit + Rs 30/month fixed
- **Slab 3 (201-300 units)**: Rs 7.50/unit + Rs 50/month fixed
- **Slab 4 (301+ units)**: Rs 9.50/unit + Rs 75/month fixed

#### Commercial Rate Slabs:
- **Slab 1 (0-100 units)**: Rs 4.50/unit + Rs 50/month fixed
- **Slab 2 (101-200 units)**: Rs 7.50/unit + Rs 50/month fixed
- **Slab 3 (201-500 units)**: Rs 9.50/unit + Rs 100/month fixed
- **Slab 4 (501+ units)**: Rs 11.50/unit + Rs 150/month fixed

### 2. Net Metering Benefits

The recommendation includes:
- **Self-consumption offset**: 80% of solar generation used immediately
- **Export credit**: 20% of generation credited back at Rs 8.50/unit (domestic)
- **Rate slab reduction**: Potential to drop to lower rate slab by reducing consumption

### 3. Rate Slab Opportunity Analysis

The agent identifies if solar installation can:
- Reduce you to a lower rate slab
- Calculate exact savings from slab difference
- Example: Moving from Slab 4 (Rs 9.50/unit) to Slab 2 (Rs 6.00/unit) saves Rs 3.50 per unit!

## Architecture

```
tneb_fetcher.py
    ↓
    └─→ Fetches consumer details & consumption history
        (Currently mock data, ready for real API integration)

tneb_rate_slabs.py
    ↓
    ├─→ Domestic/Commercial/Agricultural rate configurations
    ├─→ get_rate_for_consumption() - Calculate bill with rate slabs
    └─→ get_net_metering_benefit() - Calculate solar savings

solar_recommendation.py
    ↓
    ├─→ Uses rate slabs for accurate calculations
    ├─→ _calculate_savings() - Uses TNEB rates
    ├─→ _calculate_payback() - Based on actual savings
    └─→ _get_rate_slab_insights() - Identifies slab opportunities

ai_agent.py
    ↓
    └─→ Orchestrates entire analysis & recommendation

ai_api_routes.py / ai_agent.html
    ↓
    └─→ Flask API endpoints and web UI
```

## Usage Examples

### 1. Using the Python API

```python
from ai_agent import SolarAIAgent

# Initialize agent
agent = SolarAIAgent()

# Analyze EB number and get recommendation
result = agent.analyze_and_recommend(
    eb_number="333333333330001",
    recommendation_type="balanced"
)

# Display explanation
print(agent.get_recommendation_explanation(result))
```

### 2. Using the REST API

```bash
# Analyze EB number
curl -X POST http://localhost:5000/api/analyze-eb \
  -H "Content-Type: application/json" \
  -d '{
    "eb_number": "333333333330001",
    "recommendation_type": "balanced"
  }'

# Quick consumer search
curl http://localhost:5000/api/consumer-search?eb_number=333333333330001

# Get solar recommendation for specific consumption
curl -X POST http://localhost:5000/api/solar-recommendation \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_units": 220,
    "consumer_type": "domestic",
    "coverage": "balanced"
  }'
```

### 3. Using the Web UI

Navigate to: `http://localhost:5000/ai-agent`

Enter EB number and select recommendation type (Conservative/Balanced/Aggressive).

The UI displays:
- Consumer information
- Current TNEB billing details
- Rate slab opportunities
- Solar recommendation with options
- Financial projections
- Next steps

## Key Calculations

### Example: Domestic Consumer with 220 units/month

**Current TNEB Bill Calculation:**
- Units in Slab 1 (0-100): 100 × Rs 3.00 = Rs 300
- Units in Slab 2 (101-200): 100 × Rs 6.00 = Rs 600
- Units in Slab 3 (201-220): 20 × Rs 7.50 = Rs 150
- Subtotal = Rs 1,050 + Rs 50 (fixed) = Rs 1,100
- GST (5%) = Rs 55
- **Total Monthly Bill = Rs 1,155**
- **Effective Rate = Rs 5.25/unit**

**With 5 kW Solar System (Balanced Coverage):**
- Monthly solar generation: 5 kW × 4.5 hours × 30 days = 675 units
- Self-consumption (80%): 540 units
- Export to grid (20%): 135 units
- Billable units: 220 - 540 = (negative, so 0)
- Export credit: 135 × Rs 8.50 = Rs 1,147.50
- Fixed charge still applies: Rs 50
- **New monthly bill: Rs 50 - Rs 1,147.50 = Credit of Rs 1,097.50**
- **Monthly Savings: ~Rs 1,155** (from zero bill + export credit)

**Payback Period:**
- System cost: 5 kW × Rs 80,000 = Rs 4,00,000
- Annual savings: Rs 1,155 × 12 = Rs 13,860
- Payback: 4,00,000 ÷ 13,860 = **29 years** (with conservative generation)

## Recommendation Types

### Conservative (50% Coverage)
- Generates 50% of annual consumption
- High grid dependency (50%)
- Lower installation cost
- Longer payback period
- Good for: Budget-conscious customers

### Balanced (75% Coverage)
- Generates 75% of annual consumption
- Moderate grid dependency (25%)
- Medium installation cost
- Reasonable payback period (~7-9 years)
- **Recommended** for most customers

### Aggressive (100% Coverage)
- Generates 100% of annual consumption
- Zero grid dependency
- Higher installation cost
- Shorter payback (~5-6 years)
- Good for: Maximum independence

## Rate Slab Insights

The agent identifies opportunities like:
- **Slab Reduction Benefit**: Moving to lower slab by reducing consumption
- **Export Credit Opportunity**: Exporting excess at higher rates
- **Fixed Charge Optimization**: Fixed charge becomes negligible with net metering

## Integration with Existing System

### Add to Flask App

In `app.py`, add:

```python
from ai_agent import SolarAIAgent
from ai_api_routes import *  # Imports the API endpoints

# Or manually import routes:
# - /api/analyze-eb
# - /api/consumer-search
# - /api/solar-recommendation
# - /ai-agent (web UI)
```

### Add Route to Navigation

In `templates/index.html`:

```html
<a href="/ai-agent">🤖 AI Solar Recommendation</a>
```

## Data Requirements

### To Fetch from TNEB API

The `tneb_fetcher.py` needs:
1. TNEB API endpoint URL
2. Authentication credentials (API key or OAuth2)
3. EB number validation format

Currently uses **mock data**. To integrate real TNEB API:

1. Get API credentials from TNEB
2. Update `TNEBConsumerFetcher.fetch_consumer_details()` method
3. Map TNEB response to our data structure
4. Handle errors and retries

## Rate Slab Updates

TNEB updates rates periodically (usually annually in April).

To update rates in code:

1. Edit `tneb_rate_slabs.py`
2. Update slab rates in `DOMESTIC_RATE_SLABS`, `COMMERCIAL_RATE_SLABS`, etc.
3. Update `NET_METERING_RATES` if changed
4. Test with `python tneb_rate_slabs.py`

## Future Enhancements

- [ ] Real TNEB API integration
- [ ] Historical rate tracking & trend analysis
- [ ] Subsidy eligibility checker
- [ ] Financing options calculator
- [ ] Equipment recommendation based on budget
- [ ] Installation timeline estimator
- [ ] Performance monitoring dashboard post-installation
- [ ] Time-of-use rate optimization
- [ ] Power factor correction recommendations
- [ ] Battery storage recommendation

## Testing

Run quick tests:

```bash
python tneb_rate_slabs.py  # Test rate slab calculations
python ai_agent.py         # Test full recommendation flow
```

## Support

For issues or questions:
1. Check TNEB rate slab validity
2. Verify EB number format
3. Check consumption data accuracy
4. Review logs in the agent's conversation history

---

**Version**: 1.0  
**Last Updated**: April 2026  
**TNEB Rates**: FY 2025-26
