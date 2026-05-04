"""Solar Recommendation Engine - Suggest solar kW based on consumption."""

import logging
from typing import Dict, List, Tuple
from tneb_rate_slabs import get_rate_for_consumption, get_net_metering_benefit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SolarRecommendationEngine:
    """Calculate optimal solar system size based on consumption."""

    # Solar radiation and efficiency factors for Tamil Nadu
    DAILY_SOLAR_HOURS = 4.5  # Average peak sun hours per day in TN
    SYSTEM_EFFICIENCY = 0.75  # Account for inverter, cable, environmental losses
    
    # Recommended coverage ratios (% of annual consumption to cover)
    COVERAGE_RATIOS = {
        "domestic": {
            "conservative": 0.50,  # Cover 50% of consumption
            "balanced": 0.75,      # Cover 75% of consumption  
            "aggressive": 1.0,     # Cover 100% of consumption
        },
        "commercial": {
            "conservative": 0.40,
            "balanced": 0.60,
            "aggressive": 0.90,
        },
    }

    # Peak load factors (ratio of average to peak consumption)
    PEAK_LOAD_FACTORS = {
        "low": 1.3,      # Low variation (e.g., offices)
        "medium": 1.5,   # Medium variation
        "high": 2.0,     # High variation (e.g., industrial)
    }

    def recommend_solar_kw(
        self,
        monthly_units: float,
        consumer_type: str = "domestic",
        coverage: str = "balanced",
        peak_variation: str = "medium",
    ) -> Dict:
        """
        Recommend optimal solar system size based on TNEB rate slabs.

        Args:
            monthly_units: Average monthly consumption in units (kWh)
            consumer_type: 'domestic' or 'commercial'
            coverage: 'conservative', 'balanced', or 'aggressive'
            peak_variation: 'low', 'medium', or 'high'

        Returns:
            Dict with recommendation details
        """
        try:
            # Annual consumption
            annual_units = monthly_units * 12

            # Get coverage ratio
            coverage_ratio = self.COVERAGE_RATIOS.get(
                consumer_type, self.COVERAGE_RATIOS["domestic"]
            ).get(coverage, 0.75)

            # Calculate required solar generation
            required_generation = annual_units * coverage_ratio

            # Calculate system size needed
            system_kw = self._calculate_system_size(required_generation)

            # Round to standard sizes for aesthetic and practical reasons
            recommended_kw = self._round_to_standard_size(system_kw)

            # Get peak load recommendation
            peak_load_factor = self.PEAK_LOAD_FACTORS.get(peak_variation, 1.5)

            # Get TNEB rate information
            rate_info = get_rate_for_consumption(monthly_units, consumer_type)
            
            # Calculate savings using TNEB rates
            monthly_savings = self._calculate_savings(recommended_kw, monthly_units, consumer_type)
            
            # Calculate payback period
            payback_period = self._calculate_payback(recommended_kw, monthly_units, consumer_type)

            # Calculate various options
            options = self._generate_options(
                monthly_units, annual_units, consumer_type, coverage_ratio
            )

            return {
                "recommended_kw": recommended_kw,
                "calculation_basis": f"{coverage} coverage ({coverage_ratio*100:.0f}%)",
                "annual_consumption_units": annual_units,
                "annual_generation_needed": required_generation,
                "required_system_kw": round(system_kw, 2),
                "system_efficiency_factor": self.SYSTEM_EFFICIENCY,
                "peak_load_factor": peak_load_factor,
                "monthly_save_estimate": monthly_savings,
                "payback_period_years": payback_period,
                "tneb_rate_information": {
                    "current_monthly_bill": rate_info["total_bill"],
                    "effective_rate_per_unit": rate_info["effective_rate_per_unit"],
                    "applicable_slab": rate_info.get("applicable_slab", "N/A"),
                    "gst_included": True,
                },
                "options": options,
                "climate_data": {
                    "location": "Tamil Nadu",
                    "avg_peak_sun_hours": self.DAILY_SOLAR_HOURS,
                    "annual_irradiance": 1800,  # kWh/m²/year (approx for TN)
                },
                "rate_slab_insights": self._get_rate_slab_insights(monthly_units, consumer_type),
            }

        except Exception as e:
            logger.error(f"Error calculating recommendation: {str(e)}")
            return {"error": str(e)}

    def get_consumption_analysis(self, monthly_consumption_history: List[float]) -> Dict:
        """
        Analyze consumption patterns from historical data.

        Args:
            monthly_consumption_history: List of monthly units consumed

        Returns:
            Dict with consumption analysis
        """
        if not monthly_consumption_history:
            return {"error": "No consumption data provided"}

        avg_monthly = sum(monthly_consumption_history) / len(monthly_consumption_history)
        max_monthly = max(monthly_consumption_history)
        min_monthly = min(monthly_consumption_history)
        variation_pct = (
            (max_monthly - min_monthly) / avg_monthly * 100
            if avg_monthly > 0
            else 0
        )

        # Determine peak variation category
        if variation_pct < 25:
            peak_variation = "low"
        elif variation_pct < 50:
            peak_variation = "medium"
        else:
            peak_variation = "high"

        return {
            "average_monthly_units": round(avg_monthly, 2),
            "max_monthly_units": max_monthly,
            "min_monthly_units": min_monthly,
            "variation_percentage": round(variation_pct, 2),
            "peak_variation_category": peak_variation,
            "recommendation": self._get_consumption_insight(avg_monthly),
        }

    @staticmethod
    def _calculate_system_size(annual_generation_needed: float) -> float:
        """Calculate system size in kW based on required generation."""
        # Formula: SystemSize (kW) = Annual Generation Needed / (365 * Peak Sun Hours * Efficiency)
        system_size = (
            annual_generation_needed
            / (
                365
                * SolarRecommendationEngine.DAILY_SOLAR_HOURS
                * SolarRecommendationEngine.SYSTEM_EFFICIENCY
            )
        )
        return system_size

    @staticmethod
    def _round_to_standard_size(kw: float) -> float:
        """Round to nearest practical solar system size."""
        # Standard sizes: 1, 2, 3, 3.5, 4, 5, 6, 6.5, 7, 7.5, 8, 9, 10, 12...
        standard_sizes = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 6.5, 7, 7.5, 8, 9, 10, 12, 15, 20]

        # Find nearest standard size (round up for safety)
        for size in standard_sizes:
            if kw <= size:
                return size

        # If larger, round up to nearest integer + 0.5
        return round(kw + 0.5, 1)

    def _generate_options(
        self,
        monthly_units: float,
        annual_units: float,
        consumer_type: str,
        coverage_ratio: float,
    ) -> List[Dict]:
        """Generate multiple solar system options."""
        options = []

        for option_name in ["Conservative", "Balanced", "Aggressive"]:
            ratio = self.COVERAGE_RATIOS[consumer_type].get(
                option_name.lower(), 0.75
            )
            required_gen = annual_units * ratio
            sys_kw = self._calculate_system_size(required_gen)
            rec_kw = self._round_to_standard_size(sys_kw)

            monthly_savings = self._calculate_savings(rec_kw, monthly_units, consumer_type)

            options.append(
                {
                    "option": option_name,
                    "coverage_ratio": ratio,
                    "recommended_kw": rec_kw,
                    "annual_savings": monthly_savings * 12,
                    "grid_dependency": f"{(1 - ratio) * 100:.0f}%",
                }
            )

        return options

    @staticmethod
    def _calculate_savings(system_kw: float, monthly_units: float, category: str = "domestic") -> float:
        """Estimate monthly savings from solar generation using TNEB rate slabs."""
        try:
            # Use actual TNEB net metering calculation
            net_metering_benefit = get_net_metering_benefit(system_kw, monthly_units, category)
            return net_metering_benefit["monthly_savings"]
        except Exception as e:
            logger.error(f"Error calculating savings with TNEB rates: {str(e)}")
            # Fallback to basic calculation
            monthly_generation = system_kw * SolarRecommendationEngine.DAILY_SOLAR_HOURS * 30
            avg_tariff = 6.50  # Conservative estimate
            return round(monthly_generation * avg_tariff, 2)

    @staticmethod
    def _calculate_payback(system_kw: float, monthly_units: float, category: str = "domestic") -> float:
        """Estimate payback period in years."""
        # Assume cost: Rs 80,000 per kW (ballpark for residential TN)
        cost_per_kw = 80000
        system_cost = system_kw * cost_per_kw

        monthly_savings = SolarRecommendationEngine._calculate_savings(
            system_kw, monthly_units, category
        )
        annual_savings = monthly_savings * 12

        if annual_savings > 0:
            payback_years = system_cost / annual_savings
            return round(payback_years, 1)

        return 0

    @staticmethod
    def _get_consumption_insight(average_monthly: float) -> str:
        """Get consumption category insight."""
        if average_monthly < 100:
            return "Low consumption: Good candidate for 2-3 kW system"
        elif average_monthly < 250:
            return "Medium consumption: Suitable for 3-5 kW system"
        elif average_monthly < 500:
            return "High consumption: Consider 5-10 kW system"
        else:
            return "Very high consumption: Consider commercial/industrial solution"

    @staticmethod
    def _get_rate_slab_insights(monthly_units: float, consumer_type: str) -> Dict:
        """Get insights about TNEB rate slab impacts."""
        try:
            current_rate = get_rate_for_consumption(monthly_units, consumer_type)
            
            # Check if reducing consumption by solar could drop to lower slab
            if monthly_units > 100:
                lower_consumption = monthly_units * 0.75  # 75% of current
                lower_rate = get_rate_for_consumption(lower_consumption, consumer_type)
                
                slab_benefit = (
                    (current_rate["effective_rate_per_unit"] - lower_rate["effective_rate_per_unit"])
                    * monthly_units
                )
                
                return {
                    "current_slab": current_rate.get("applicable_slab", "N/A"),
                    "current_effective_rate": current_rate["effective_rate_per_unit"],
                    "current_monthly_bill": current_rate["total_bill"],
                    "potential_lower_slab": lower_rate.get("applicable_slab", "N/A"),
                    "potential_effective_rate": lower_rate["effective_rate_per_unit"],
                    "potential_bill_in_lower_slab": lower_rate["total_bill"],
                    "potential_slab_benefit": round(slab_benefit, 2),
                    "insight": f"By reducing consumption with solar, you could save Rs {slab_benefit:.0f}/month from rate slab difference alone!"
                }
            else:
                return {
                    "current_slab": current_rate.get("applicable_slab", "N/A"),
                    "current_effective_rate": current_rate["effective_rate_per_unit"],
                    "current_monthly_bill": current_rate["total_bill"],
                    "insight": "Already in lowest slab - solar benefits mainly from grid export credit and reduced consumption."
                }
        except Exception as e:
            logger.error(f"Error getting rate slab insights: {str(e)}")
            return {}

