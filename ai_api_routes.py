"""
Flask API endpoints for AI Agent integration.
Add these routes to your existing app.py
"""

@app.route("/api/analyze-eb", methods=["POST"])
def analyze_eb():
    """
    API endpoint to analyze EB number and get solar recommendation.
    
    Request JSON:
    {
        "eb_number": "333333333330001",
        "recommendation_type": "balanced"  // optional: conservative/aggressive
    }
    
    Response JSON:
    {
        "success": true,
        "eb_number": "333333333330001",
        "consumer_info": {...},
        "consumption_analysis": {...},
        "solar_recommendation": {...}
    }
    """
    from ai_agent import SolarAIAgent
    
    try:
        data = request.get_json()
        
        if not data or "eb_number" not in data:
            return jsonify({"error": "EB number is required"}), 400
        
        eb_number = data.get("eb_number", "").strip()
        recommendation_type = data.get("recommendation_type", "balanced")
        
        # Validate recommendation type
        if recommendation_type not in ["conservative", "balanced", "aggressive"]:
            recommendation_type = "balanced"
        
        # Initialize and run agent
        agent = SolarAIAgent()
        result = agent.analyze_and_recommend(eb_number, recommendation_type)
        
        return jsonify(result), 200 if result.get("success") else 400
        
    except Exception as e:
        logger.error(f"Error in analyze_eb: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/consumer-search", methods=["GET"])
def consumer_search():
    """
    Quick consumer lookup by EB number.
    Query params: ?eb_number=333333333330001
    """
    from tneb_fetcher import TNEBConsumerFetcher
    
    try:
        eb_number = request.args.get("eb_number", "").strip()
        
        if not eb_number:
            return jsonify({"error": "EB number is required"}), 400
        
        fetcher = TNEBConsumerFetcher()
        consumer_data = fetcher.fetch_consumer_details(eb_number)
        
        if consumer_data:
            consumption_data = fetcher.get_monthly_consumption(eb_number)
            consumer_data["consumption_history"] = consumption_data.get("monthly_consumption")
            return jsonify({"success": True, "data": consumer_data}), 200
        else:
            return jsonify({"success": False, "error": "Consumer not found"}), 404
            
    except Exception as e:
        logger.error(f"Error in consumer_search: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/solar-recommendation", methods=["POST"])
def solar_recommendation():
    """
    Generate solar recommendation for given consumption.
    
    Request JSON:
    {
        "monthly_units": 220,
        "consumer_type": "domestic",  // domestic or commercial
        "coverage": "balanced"         // conservative/balanced/aggressive
    }
    """
    from solar_recommendation import SolarRecommendationEngine
    
    try:
        data = request.get_json()
        
        if not data or "monthly_units" not in data:
            return jsonify({"error": "monthly_units is required"}), 400
        
        engine = SolarRecommendationEngine()
        recommendation = engine.recommend_solar_kw(
            monthly_units=float(data.get("monthly_units")),
            consumer_type=data.get("consumer_type", "domestic"),
            coverage=data.get("coverage", "balanced")
        )
        
        return jsonify(recommendation), 200
        
    except Exception as e:
        logger.error(f"Error in solar_recommendation: {str(e)}")
        return jsonify({"error": str(e)}), 500
