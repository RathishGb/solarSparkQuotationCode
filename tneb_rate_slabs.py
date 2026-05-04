"""
TNEB Rate Slab Configuration for Tamil Nadu Electricity Board.

As per TNEB tariff schedules (updated 2024-2026).
This includes domestic, commercial, and agricultural rate slabs.

Rate slabs are progressive - tariff increases with higher consumption.
"""

# Domestic Rate Slabs (FY 2024-25 and 2025-26)
# Format: {
#     "slab_name": "Description",
#     "from_units": starting unit,
#     "to_units": ending unit,
#     "rate_per_unit": Rs/unit (including all charges),
#     "fixed_charge_monthly": Rs/month
# }

DOMESTIC_RATE_SLABS = [
    {
        "slab_name": "Slab 1",
        "from_units": 0,
        "to_units": 100,
        "rate_per_unit": 3.00,
        "fixed_charge_monthly": 30,
        "description": "0-100 units (subsidized slab)"
    },
    {
        "slab_name": "Slab 2",
        "from_units": 101,
        "to_units": 200,
        "rate_per_unit": 6.00,
        "fixed_charge_monthly": 30,
        "description": "101-200 units (normal slab)"
    },
    {
        "slab_name": "Slab 3",
        "from_units": 201,
        "to_units": 300,
        "rate_per_unit": 7.50,
        "fixed_charge_monthly": 50,
        "description": "201-300 units (higher slab)"
    },
    {
        "slab_name": "Slab 4",
        "from_units": 301,
        "to_units": float('inf'),
        "rate_per_unit": 9.50,
        "fixed_charge_monthly": 75,
        "description": "301+ units (peak slab)"
    },
]

# Commercial Rate Slabs (Small commercial / Non-domestic)
COMMERCIAL_RATE_SLABS = [
    {
        "slab_name": "Slab 1",
        "from_units": 0,
        "to_units": 100,
        "rate_per_unit": 4.50,
        "fixed_charge_monthly": 50,
        "description": "0-100 units"
    },
    {
        "slab_name": "Slab 2",
        "from_units": 101,
        "to_units": 200,
        "rate_per_unit": 7.50,
        "fixed_charge_monthly": 50,
        "description": "101-200 units"
    },
    {
        "slab_name": "Slab 3",
        "from_units": 201,
        "to_units": 500,
        "rate_per_unit": 9.50,
        "fixed_charge_monthly": 100,
        "description": "201-500 units"
    },
    {
        "slab_name": "Slab 4",
        "from_units": 501,
        "to_units": float('inf'),
        "rate_per_unit": 11.50,
        "fixed_charge_monthly": 150,
        "description": "501+ units"
    },
]

# Agricultural Rate Slabs (Pump sets and farms)
AGRICULTURAL_RATE_SLABS = [
    {
        "slab_name": "Slab 1",
        "from_units": 0,
        "to_units": 50,
        "rate_per_unit": 0.50,
        "fixed_charge_monthly": 50,
        "description": "0-50 units (highly subsidized)"
    },
    {
        "slab_name": "Slab 2",
        "from_units": 51,
        "to_units": 100,
        "rate_per_unit": 1.50,
        "fixed_charge_monthly": 50,
        "description": "51-100 units"
    },
    {
        "slab_name": "Slab 3",
        "from_units": 101,
        "to_units": 200,
        "rate_per_unit": 3.50,
        "fixed_charge_monthly": 75,
        "description": "101-200 units"
    },
    {
        "slab_name": "Slab 4",
        "from_units": 201,
        "to_units": float('inf'),
        "rate_per_unit": 5.50,
        "fixed_charge_monthly": 100,
        "description": "201+ units"
    },
]

# Additional charges and taxes
ADDITIONAL_CHARGES = {
    "gst_percentage": 5,  # 5% GST on electricity in TN
    "surcharge_percentage": 0,  # Additional surcharge (varies by tariff)
    "fuel_surcharge_percentage": 0,  # Fuel adjustment charges (varies)
    "reactive_power_charge": 0.50,  # Rs/kVArh (if applicable)
}

# Time-of-use rates (if applicable for certain connections)
TIME_OF_USE_RATES = {
    "peak_hours": {  # 09:00 AM to 09:00 PM on weekdays
        "from_units": 0,
        "to_units": float('inf'),
        "rate_multiplier": 1.2,  # 20% premium
    },
    "off_peak_hours": {  # 09:00 PM to 09:00 AM + weekends
        "from_units": 0,
        "to_units": float('inf'),
        "rate_multiplier": 0.8,  # 20% discount
    }
}

# Net metering credit rate (for solar exported to grid)
NET_METERING_RATES = {
    "domestic": 8.50,  # Rs/unit credited back to consumer
    "commercial": 9.50,
    "agricultural": 5.50,
}

# Power factor surcharge rules
POWER_FACTOR_RULES = {
    "threshold": 0.95,  # Ideal power factor
    "surcharge_percentage": 0.5,  # 0.5% per 0.01 PF below threshold
    "applies_to": ["commercial", "agricultural"],
}

# Seasonal variations
SEASONAL_RATES = {
    # Summer: May-September (higher)
    "summer": {
        "multiplier": 1.05,
        "months": [5, 6, 7, 8, 9]
    },
    # Winter: October-December and Jan-Mar (lower)
    "winter": {
        "multiplier": 0.95,
        "months": [10, 11, 12, 1, 2, 3]
    },
    # Normal: April (base rate)
    "normal": {
        "multiplier": 1.0,
        "months": [4]
    }
}


def get_rate_for_consumption(monthly_units: float, category: str = "domestic") -> dict:
    """
    Calculate effective rate based on TNEB slab structure.
    
    Args:
        monthly_units: Monthly consumption in units (kWh)
        category: 'domestic', 'commercial', or 'agricultural'
        
    Returns:
        Dict with rate details including slab, unit rate, fixed charge, total bill
    """
    if category == "domestic":
        slabs = DOMESTIC_RATE_SLABS
    elif category == "commercial":
        slabs = COMMERCIAL_RATE_SLABS
    elif category == "agricultural":
        slabs = AGRICULTURAL_RATE_SLABS
    else:
        slabs = DOMESTIC_RATE_SLABS  # Default to domestic
    
    # Find applicable slab and calculate bill
    total_bill = 0
    slab_details = []
    remaining_units = monthly_units
    
    for slab in slabs:
        if remaining_units <= 0:
            break
            
        slab_from = slab["from_units"]
        slab_to = slab["to_units"]
        rate = slab["rate_per_unit"]
        
        # Calculate units in this slab
        if remaining_units <= slab_to:
            units_in_slab = remaining_units
            remaining_units = 0
        else:
            units_in_slab = slab_to - slab_from + 1
            remaining_units -= units_in_slab
        
        slab_bill = units_in_slab * rate
        total_bill += slab_bill
        
        slab_details.append({
            "slab": slab["slab_name"],
            "units": units_in_slab,
            "rate_per_unit": rate,
            "slab_bill": slab_bill
        })
    
    # Add fixed charge (take from first applicable slab)
    fixed_charge = slabs[0]["fixed_charge_monthly"]
    total_bill += fixed_charge
    
    # Add GST
    gst_amount = total_bill * (ADDITIONAL_CHARGES["gst_percentage"] / 100)
    total_with_gst = total_bill + gst_amount
    
    # Effective rate per unit
    effective_rate = total_with_gst / monthly_units if monthly_units > 0 else 0
    
    return {
        "category": category,
        "monthly_units": monthly_units,
        "slab_details": slab_details,
        "subtotal": round(total_bill, 2),
        "fixed_charge": fixed_charge,
        "gst_amount": round(gst_amount, 2),
        "total_bill": round(total_with_gst, 2),
        "effective_rate_per_unit": round(effective_rate, 2),
        "applicable_slab": _get_applicable_slab(monthly_units, category)
    }


def _get_applicable_slab(monthly_units: float, category: str) -> str:
    """Get the highest slab applicable for given consumption."""
    if category == "domestic":
        slabs = DOMESTIC_RATE_SLABS
    elif category == "commercial":
        slabs = COMMERCIAL_RATE_SLABS
    else:
        slabs = AGRICULTURAL_RATE_SLABS
    
    for slab in reversed(slabs):
        if monthly_units >= slab["from_units"]:
            return slab["description"]
    
    return slabs[0]["description"]


def get_net_metering_benefit(solar_kw: float, monthly_consumption: float, 
                             category: str = "domestic") -> dict:
    """
    Calculate net metering benefits based on monthly consumption and category.
    
    Args:
        solar_kw: Installed solar capacity in kW
        monthly_consumption: Monthly consumption in units
        category: Consumer category ('domestic', 'commercial', 'agricultural')
        
    Returns:
        Dict with net metering benefits
    """
    # Solar generation estimate: 4.5 peak sun hours/day average
    monthly_solar_generation = solar_kw * 4.5 * 30
    
    # Portion that offsets consumption vs. exported to grid
    # Assuming 80% self-consumption, 20% export (typical)
    self_consumption = min(monthly_solar_generation * 0.8, monthly_consumption)
    export_to_grid = monthly_solar_generation - self_consumption
    
    # Get billable units after solar offset
    billable_units = max(0, monthly_consumption - self_consumption)
    
    # Get rates
    current_rate = get_rate_for_consumption(monthly_consumption, category)
    reduced_rate = get_rate_for_consumption(billable_units, category)
    
    # Credit for exported units
    net_metering_rate = NET_METERING_RATES.get(category, 8.50)
    export_credit = export_to_grid * net_metering_rate
    
    # Calculate savings
    original_bill = current_rate["total_bill"]
    reduced_bill = reduced_rate["total_bill"]
    bill_after_solar = max(0, reduced_bill - export_credit)
    
    monthly_savings = original_bill - bill_after_solar
    
    return {
        "monthly_solar_generation": round(monthly_solar_generation, 2),
        "self_consumption_units": round(self_consumption, 2),
        "export_to_grid_units": round(export_to_grid, 2),
        "billable_units_after_solar": round(billable_units, 2),
        "original_monthly_bill": original_bill,
        "reduced_bill_with_self_consumption": reduced_bill,
        "export_credit": round(export_credit, 2),
        "bill_after_solar": round(bill_after_solar, 2),
        "monthly_savings": round(monthly_savings, 2),
        "annual_savings": round(monthly_savings * 12, 2),
    }


if __name__ == "__main__":
    # Example calculations
    print("=" * 60)
    print("TNEB RATE SLAB CALCULATOR")
    print("=" * 60)
    
    # Example 1: Domestic consumer with 220 units/month
    print("\nExample 1: Domestic Consumer (220 units/month)")
    print("-" * 60)
    rate_info = get_rate_for_consumption(220, "domestic")
    print(f"Monthly Bill: Rs {rate_info['total_bill']}")
    print(f"Effective Rate: Rs {rate_info['effective_rate_per_unit']}/unit")
    print(f"Applicable Slab: {rate_info['applicable_slab']}")
    
    # Example 2: Net metering benefits for 5kW system
    print("\nExample 2: Net Metering Benefits (220 units/month, 5kW Solar)")
    print("-" * 60)
    net_metering = get_net_metering_benefit(5, 220, "domestic")
    print(f"Monthly Savings: Rs {net_metering['monthly_savings']}")
    print(f"Annual Savings: Rs {net_metering['annual_savings']}")
    print(f"Solar Generation: {net_metering['monthly_solar_generation']} units/month")
