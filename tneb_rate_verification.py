"""
TNEB Rate Verification & Update Tool
Run this to verify current rates and update if needed
"""

from tneb_rate_slabs import (
    DOMESTIC_RATE_SLABS,
    COMMERCIAL_RATE_SLABS,
    AGRICULTURAL_RATE_SLABS,
    NET_METERING_RATES,
    get_rate_for_consumption
)


def display_current_rates():
    """Display currently configured rates."""
    print("\n" + "="*70)
    print("CURRENT RATES IN SYSTEM")
    print("="*70)
    
    print("\n📱 DOMESTIC RATES (FY 2025-26)")
    print("-" * 70)
    print(f"{'Slab':<10} {'Units':<20} {'Rate/Unit':<15} {'Fixed Charge':<15}")
    print("-" * 70)
    
    for slab in DOMESTIC_RATE_SLABS:
        units_range = f"{int(slab['from_units'])}-{int(slab['to_units']) if slab['to_units'] != float('inf') else 'Above'}"
        print(f"{slab['slab_name']:<10} {units_range:<20} Rs {slab['rate_per_unit']:<13.2f} Rs {slab['fixed_charge_monthly']:<13}")
    
    print("\n🏢 COMMERCIAL RATES (FY 2025-26)")
    print("-" * 70)
    print(f"{'Slab':<10} {'Units':<20} {'Rate/Unit':<15} {'Fixed Charge':<15}")
    print("-" * 70)
    
    for slab in COMMERCIAL_RATE_SLABS:
        units_range = f"{int(slab['from_units'])}-{int(slab['to_units']) if slab['to_units'] != float('inf') else 'Above'}"
        print(f"{slab['slab_name']:<10} {units_range:<20} Rs {slab['rate_per_unit']:<13.2f} Rs {slab['fixed_charge_monthly']:<13}")
    
    print("\n🌾 AGRICULTURAL RATES (FY 2025-26)")
    print("-" * 70)
    print(f"{'Slab':<10} {'Units':<20} {'Rate/Unit':<15} {'Fixed Charge':<15}")
    print("-" * 70)
    
    for slab in AGRICULTURAL_RATE_SLABS:
        units_range = f"{int(slab['from_units'])}-{int(slab['to_units']) if slab['to_units'] != float('inf') else 'Above'}"
        print(f"{slab['slab_name']:<10} {units_range:<20} Rs {slab['rate_per_unit']:<13.2f} Rs {slab['fixed_charge_monthly']:<13}")
    
    print("\n☀️ NET METERING CREDIT RATES")
    print("-" * 70)
    for category, rate in NET_METERING_RATES.items():
        print(f"{category.capitalize():<20}: Rs {rate}/unit")


def verify_with_known_bill():
    """Verify rates by comparing with known TNEB bill."""
    print("\n" + "="*70)
    print("VERIFICATION: Compare with Your Actual TNEB Bill")
    print("="*70)
    
    print("""
    Enter details from your recent TNEB bill to verify rates:
    """)
    
    try:
        units = float(input("Enter your monthly consumption (units): "))
        category = input("Enter category (domestic/commercial/agricultural): ").lower()
        
        if category not in ['domestic', 'commercial', 'agricultural']:
            category = 'domestic'
        
        actual_bill = float(input(f"Enter your actual monthly bill (Rs): "))
        
        # Calculate using our system
        rate_info = get_rate_for_consumption(units, category)
        calculated_bill = rate_info['total_bill']
        
        print(f"\n{'Metric':<30} {'Your Bill':<15} {'Our Calculation':<15} {'Match':<10}")
        print("-" * 70)
        
        # Compare
        bill_diff = abs(actual_bill - calculated_bill)
        bill_match = "✓ Yes" if bill_diff < 10 else "✗ No"
        
        print(f"{'Monthly Bill (Rs)':<30} {actual_bill:<15.2f} {calculated_bill:<15.2f} {bill_match:<10}")
        print(f"{'Difference':<30} {bill_diff:<15.2f}")
        print(f"{'Accuracy':<30} {(1 - bill_diff/actual_bill)*100:<14.1f}% ")
        
        if bill_diff < 10:
            print("\n✅ Rates are VERIFIED and ACCURATE!")
        elif bill_diff < 50:
            print(f"\n⚠️  Rates may need minor update (Rs {bill_diff:.0f} difference)")
        else:
            print(f"\n❌ Rates need UPDATE (Rs {bill_diff:.0f} difference - {(bill_diff/actual_bill)*100:.1f}%)")
            print("   Please check latest TNEB portal for updated rates")
    
    except ValueError:
        print("Invalid input. Please enter numeric values.")


def rate_update_checklist():
    """Display checklist for manual rate update."""
    print("\n" + "="*70)
    print("RATE UPDATE CHECKLIST")
    print("="*70)
    
    checklist = """
    Follow these steps to update rates for FY 2026-27:

    □ Step 1: Visit TNEB Official Website
      → Go to: https://www.tneb.in
      → Click: Tariff → Tariff Schedule
      → Download: Official Tariff Order for 2026-27

    □ Step 2: Extract Rate Information
      Note the following for each category:
      → Domestic: 4 rate slabs + fixed charges
      → Commercial: 4 rate slabs + fixed charges
      → Agricultural: 4 rate slabs + fixed charges
      → Net metering credit rates

    □ Step 3: Update Code
      Edit: tneb_rate_slabs.py
      Update: DOMESTIC_RATE_SLABS array
      Update: COMMERCIAL_RATE_SLABS array
      Update: AGRICULTURAL_RATE_SLABS array
      Update: NET_METERING_RATES dict

    □ Step 4: Test Changes
      Run: .\.venv\Scripts\python test_tneb_integration.py
      Verify: All rates update correctly

    □ Step 5: Update Documentation
      Edit: TNEB_RATES_REFERENCE.md
      Edit: AI_AGENT_README.md (rate examples)
      Edit: tneb_rate_slabs.py comments

    □ Step 6: Verify with Actual Bill
      Run: .\.venv\Scripts\python tneb_rate_verification.py
      Enter: Your actual consumption & bill amount
      Check: Calculated vs actual match

    □ Step 7: Deploy
      Commit changes to Git
      Deploy to production
      Monitor for accuracy
    """
    
    print(checklist)


def rate_comparison():
    """Compare different scenarios with current rates."""
    print("\n" + "="*70)
    print("SCENARIO COMPARISON - Current Rates (FY 2025-26)")
    print("="*70)
    
    scenarios = [
        ("Low Usage", 80, "domestic"),
        ("Typical Household", 220, "domestic"),
        ("High Usage", 350, "domestic"),
        ("Small Commercial", 300, "commercial"),
        ("Large Commercial", 800, "commercial"),
        ("Agricultural", 150, "agricultural"),
    ]
    
    print(f"\n{'Scenario':<25} {'Units':<10} {'Bill (Rs)':<15} {'Rate/Unit':<15}")
    print("-" * 70)
    
    for scenario_name, units, category in scenarios:
        rate_info = get_rate_for_consumption(units, category)
        print(f"{scenario_name:<25} {units:<10} {rate_info['total_bill']:<15.2f} Rs {rate_info['effective_rate_per_unit']:<13.2f}/unit")


def main():
    """Main menu."""
    print("\n")
    print("╔" + "─"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  TNEB RATE VERIFICATION & UPDATE TOOL".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "─"*68 + "╝")
    
    while True:
        print("""
    OPTIONS:
    1. Display current rates in system
    2. Verify rates with your TNEB bill
    3. Show scenario comparisons
    4. Display update checklist
    5. Exit
        """)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            display_current_rates()
        elif choice == "2":
            verify_with_known_bill()
        elif choice == "3":
            rate_comparison()
        elif choice == "4":
            rate_update_checklist()
        elif choice == "5":
            print("\n✅ Exiting. Check TNEB portal regularly for rate updates!\n")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
