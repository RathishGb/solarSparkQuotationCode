"""AI Agent - TNEB Consumer Analysis & Solar Recommendation Agent."""

import logging
from typing import Dict, Optional
from tneb_fetcher import TNEBConsumerFetcher
from solar_recommendation import SolarRecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SolarAIAgent:
    """
    AI Agent that:
    1. Fetches TNEB consumer details using EB number
    2. Analyzes consumption patterns
    3. Recommends appropriate solar system size
    """

    def __init__(self):
        """Initialize AI agent with TNEB fetcher and recommendation engine."""
        self.tneb_fetcher = TNEBConsumerFetcher()
        self.solar_engine = SolarRecommendationEngine()
        self.conversation_history = []

    def analyze_and_recommend(
        self,
        eb_number: str,
        recommendation_type: str = "balanced",
    ) -> Dict:
        """
        Main agent function - Fetch TNEB details and recommend solar system.

        Args:
            eb_number: TNEB EB number
            recommendation_type: 'conservative', 'balanced', or 'aggressive'

        Returns:
            Dict with complete analysis and recommendation
        """
        # Step 1: Add to conversation history
        self._log_interaction(f"User Query: Analyze EB {eb_number}")

        # Step 2: Validate and fetch TNEB data
        logger.info(f"Step 1: Fetching TNEB details for EB {eb_number}")
        consumer_data = self.tneb_fetcher.fetch_consumer_details(eb_number)

        if not consumer_data:
            error_msg = f"Could not fetch TNEB details for EB {eb_number}"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}

        self._log_interaction(f"TNEB Details Retrieved: {consumer_data['consumer_name']}")

        # Step 3: Get consumption history
        logger.info("Step 2: Fetching consumption history")
        consumption_data = self.tneb_fetcher.get_monthly_consumption(eb_number)

        # Step 4: Analyze consumption patterns
        logger.info("Step 3: Analyzing consumption patterns")
        monthly_consumption = [
            month["units"] for month in consumption_data.get("monthly_consumption", [])
        ]

        consumption_analysis = self.solar_engine.get_consumption_analysis(
            monthly_consumption
        )
        self._log_interaction(f"Average Monthly Consumption: {consumption_analysis.get('average_monthly_units', 0)} units")

        # Step 5: Generate solar recommendation
        logger.info("Step 4: Generating solar recommendation")
        average_monthly = consumption_analysis.get("average_monthly_units", 0)
        peak_variation = consumption_analysis.get("peak_variation_category", "medium")
        consumer_type = "domestic"  # Can be inferred from TNEB category

        recommendation = self.solar_engine.recommend_solar_kw(
            monthly_units=average_monthly,
            consumer_type=consumer_type,
            coverage=recommendation_type,
            peak_variation=peak_variation,
        )

        self._log_interaction(f"Recommendation: {recommendation['recommended_kw']} kW Solar System")

        # Step 6: Compile comprehensive report
        report = self._compile_report(
            consumer_data,
            consumption_analysis,
            recommendation,
            eb_number
        )

        return report

    def get_recommendation_explanation(self, recommendation: Dict) -> str:
        """Get human-readable explanation of the recommendation."""
        if "error" in recommendation:
            return recommendation["error"]

        kw = recommendation["recommended_kw"]
        monthly_avg = recommendation.get("annual_consumption_units", 0) / 12
        savings = recommendation["monthly_save_estimate"]
        payback = recommendation["payback_period_years"]
        
        tneb_rate = recommendation.get("tneb_rate_information", {})
        rate_slab_insights = recommendation.get("rate_slab_insights", {})

        explanation = f"""
        📊 SOLAR RECOMMENDATION REPORT
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ⚡ Recommended Solar System Size: {kw} kW

        📈 Consumption Analysis:
           • Average Monthly Consumption: {monthly_avg:.0f} units (kWh)
           • Annual Consumption: {recommendation['annual_consumption_units']:.0f} units
           • Coverage Strategy: {recommendation['calculation_basis']}

        💵 Current TNEB Bill Analysis:
           • Current Monthly Bill: Rs {tneb_rate.get('current_monthly_bill', 'N/A')}
           • Current Slab: {tneb_rate.get('applicable_slab', 'N/A')}
           • Effective Rate: Rs {tneb_rate.get('effective_rate_per_unit', 'N/A')}/unit
           
        🎯 Rate Slab Opportunity:
           • {rate_slab_insights.get('insight', 'Optimizing based on TNEB rates')}
           • Potential Benefit from Lower Slab: Rs {rate_slab_insights.get('potential_slab_benefit', 0):.0f}/month

        💰 Financial Projection:
           • Estimated Monthly Savings: Rs {savings:,.2f}
           • Annual Savings: Rs {savings * 12:,.2f}
           • Estimated Payback Period: {payback} years
           • 25-Year Savings: Rs {savings * 12 * 25:,.2f}

        🔋 System Details:
           • Location: Tamil Nadu (Avg {recommendation['climate_data']['avg_peak_sun_hours']} peak sun hours)
           • System Efficiency: {recommendation['system_efficiency_factor']*100:.0f}%
           • Grid Dependency After Installation: Reduced by {recommendation['calculation_basis'].split('(')[1].split('%')[0]}%

        📋 Other Recommended Options:
        """

        for option in recommendation.get("options", []):
            explanation += f"\n           • {option['option']}: {option['recommended_kw']} kW (Save Rs {option['annual_savings'] * 12:,.0f}/year)"

        return explanation

    def interactive_consultation(self, eb_number: str) -> None:
        """Run interactive consultation with step-by-step explanation."""
        print("\n🤖 SolarSparkAI Consultation Agent")
        print("=" * 50)

        recommendation = self.analyze_and_recommend(eb_number, recommendation_type="balanced")

        if "error" not in recommendation:
            print(self.get_recommendation_explanation(recommendation))
            print("\n✅ Recommendation generated successfully!")
            print(f"📝 Next Steps:")
            print(f"   1. Site survey for exact roof space")
            print(f"   2. Electrical safety audit")
            print(f"   3. Net metering application with TNEB")
            print(f"   4. Equipment procurement and installation")
        else:
            print(f"❌ Error: {recommendation['error']}")

    @staticmethod
    def _compile_report(
        consumer_data: Dict,
        consumption_analysis: Dict,
        recommendation: Dict,
        eb_number: str
    ) -> Dict:
        """Compile comprehensive analysis report."""
        return {
            "success": True,
            "eb_number": eb_number,
            "consumer_info": {
                "name": consumer_data.get("consumer_name"),
                "address": consumer_data.get("service_address"),
                "category": consumer_data.get("category"),
                "phase": consumer_data.get("phase"),
                "sanctioned_load": f"{consumer_data.get('sanctioned_load_kw')} kW",
            },
            "consumption_analysis": consumption_analysis,
            "solar_recommendation": recommendation,
            "tneb_rate_information": recommendation.get("tneb_rate_information", {}),
            "rate_slab_benefits": recommendation.get("rate_slab_insights", {}),
            "generated_at": SolarAIAgent._get_timestamp(),
        }

    def _log_interaction(self, message: str) -> None:
        """Log agent interaction for tracking."""
        self.conversation_history.append(message)
        logger.info(f"[Agent] {message}")

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_conversation_history(self) -> list:
        """Get agent conversation history."""
        return self.conversation_history

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = SolarAIAgent()

    # Example EB numbers (in production, these would be real)
    test_eb_numbers = [
        "333333333330001",
        "333333333330002",
    ]

    for eb_number in test_eb_numbers:
        print(f"\n{'='*60}")
        agent.interactive_consultation(eb_number)
        print(f"{'='*60}\n")

        # Show agent conversation
        print("🗣️ Conversation Log:")
        for interaction in agent.get_conversation_history():
            print(f"  • {interaction}")

        agent.reset_conversation()
