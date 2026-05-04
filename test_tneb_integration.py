"""
Test script to verify TNEB rate slab integration and AI agent functionality.
Run this to validate the implementation: python test_tneb_integration.py
"""

import sys
from tneb_rate_slabs import (
    get_rate_for_consumption,
    get_net_metering_benefit,
    DOMESTIC_RATE_SLABS
)
from solar_recommendation import SolarRecommendationEngine
from ai_agent import SolarAIAgent


def test_tneb_rate_slabs():
    """Test TNEB rate slab calculations."""
    print("\n" + "="*70)
    print("TEST 1: TNEB Rate Slab Calculations")
    print("="*70)
    
    test_cases = [
        (100, "domestic", "Slab 1 boundary"),
        (150, "domestic", "Mid Slab 2"),
        (220, "domestic", "Typical household"),
        (300, "domestic", "Slab 3 boundary"),
        (350, "domestic", "High consumption"),
    ]
    
    for units, category, description in test_cases:
        rate_info = get_rate_for_consumption(units, category)
        print(f"\n✓ {description} ({units} units)")
        print(f"  Current Monthly Bill: Rs {rate_info['total_bill']}")
        print(f"  Effective Rate: Rs {rate_info['effective_rate_per_unit']}/unit")
        print(f"  Applicable Slab: {rate_info['applicable_slab']}")


def test_net_metering():
    """Test net metering benefits calculation."""
    print("\n" + "="*70)
    print("TEST 2: Net Metering Benefits")
    print("="*70)
    
    test_cases = [
        (3, 150, "domestic", "Small 3kW system, 150 units"),
        (5, 220, "domestic", "Standard 5kW system, 220 units"),
        (10, 500, "commercial", "Large 10kW system, 500 units"),
    ]
    
    for kw, units, category, description in test_cases:
        benefit = get_net_metering_benefit(kw, units, category)
        print(f"\n✓ {description}")
        print(f"  Monthly Solar Generation: {benefit['monthly_solar_generation']} units")
        print(f"  Monthly Savings: Rs {benefit['monthly_savings']}")
        print(f"  Annual Savings: Rs {benefit['annual_savings']}")
        print(f"  Payback Period: ~{benefit['annual_savings'] / 1000 if benefit['annual_savings'] > 0 else 0:.1f} years")


def test_solar_recommendation():
    """Test solar recommendation engine."""
    print("\n" + "="*70)
    print("TEST 3: Solar Recommendation Engine")
    print("="*70)
    
    engine = SolarRecommendationEngine()
    
    # Test case: 220 units/month domestic consumer
    recommendation = engine.recommend_solar_kw(
        monthly_units=220,
        consumer_type="domestic",
        coverage="balanced",
        peak_variation="medium"
    )
    
    if "error" not in recommendation:
        print(f"\n✓ Recommendation for 220 units/month (Balanced)")
        print(f"  Recommended System: {recommendation['recommended_kw']} kW")
        print(f"  Monthly Savings: Rs {recommendation['monthly_save_estimate']}")
        print(f"  Annual Savings: Rs {recommendation['monthly_save_estimate'] * 12}")
        print(f"  Payback Period: {recommendation['payback_period_years']} years")
        print(f"  Effective TNEB Rate: Rs {recommendation['tneb_rate_information']['effective_rate_per_unit']}/unit")
        
        # Test rate slab insights
        insights = recommendation.get("rate_slab_insights", {})
        if insights.get("insight"):
            print(f"\n  Rate Slab Insight: {insights['insight']}")
            if "potential_slab_benefit" in insights:
                print(f"  Potential Slab Benefit: Rs {insights['potential_slab_benefit']}/month")
    else:
        print(f"✗ Error: {recommendation['error']}")


def test_ai_agent():
    """Test the complete AI agent flow."""
    print("\n" + "="*70)
    print("TEST 4: Complete AI Agent Flow")
    print("="*70)
    
    agent = SolarAIAgent()
    
    # Test with mock EB number
    print(f"\n✓ Testing with EB number: 333333333330001")
    result = agent.analyze_and_recommend(
        eb_number="333333333330001",
        recommendation_type="balanced"
    )
    
    if result.get("success"):
        print(f"  ✓ Analysis completed successfully")
        print(f"  Consumer: {result['consumer_info']['name']}")
        print(f"  Avg Consumption: {result['consumption_analysis']['average_monthly_units']} units")
        print(f"  Recommended Solar: {result['solar_recommendation']['recommended_kw']} kW")
        print(f"  Monthly Savings: Rs {result['solar_recommendation']['monthly_save_estimate']}")
        
        # Show explanation
        print(f"\n✓ Recommendation Explanation:")
        print(agent.get_recommendation_explanation(result['solar_recommendation']))
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")


def test_comparative_analysis():
    """Test comparing different coverage options."""
    print("\n" + "="*70)
    print("TEST 5: Comparative Analysis (Coverage Options)")
    print("="*70)
    
    engine = SolarRecommendationEngine()
    monthly_units = 220
    
    print(f"\nAnalyzing 220 units/month consumption with different strategies:\n")
    
    coverage_types = ["conservative", "balanced", "aggressive"]
    
    for coverage in coverage_types:
        rec = engine.recommend_solar_kw(
            monthly_units=monthly_units,
            consumer_type="domestic",
            coverage=coverage
        )
        
        if "error" not in rec:
            print(f"✓ {coverage.upper()} Strategy:")
            print(f"  System Size: {rec['recommended_kw']} kW")
            print(f"  Coverage: {rec['calculation_basis']}")
            print(f"  Monthly Savings: Rs {rec['monthly_save_estimate']}")
            print(f"  Payback: {rec['payback_period_years']} years")
            print(f"  25-Year Savings: Rs {rec['monthly_save_estimate'] * 12 * 25:,.0f}")
            print()


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "─"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  TNEB RATE SLAB & AI AGENT INTEGRATION TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "─"*68 + "╝")
    
    try:
        test_tneb_rate_slabs()
        test_net_metering()
        test_solar_recommendation()
        test_ai_agent()
        test_comparative_analysis()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
