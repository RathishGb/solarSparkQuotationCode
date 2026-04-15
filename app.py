"""Flask web application for Solar Quotation PDF Generator."""

import os
import json
from datetime import date
from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from pdf_generator import generate_solar_pdf
from cost_calculator import calculate_costs, generate_cost_excel

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route("/", methods=["GET"])
def index():
    today = date.today().strftime("%Y-%m-%d")
    return render_template("index.html", today=today)


@app.route("/generate", methods=["POST"])
def generate():
    consumer_name = request.form.get("consumer_name", "").strip()
    consumer_address = request.form.get("consumer_address", "").strip()
    proposal_date = request.form.get("proposal_date", "").strip()
    num_connections = int(request.form.get("num_connections", 1))

    if not consumer_name or not consumer_address or not proposal_date:
        return "All consumer fields are required.", 400

    connections = []
    for i in range(num_connections):
        eb = request.form.get(f"eb_number_{i}", "").strip()
        kw = request.form.get(f"kw_{i}", "").strip()
        price = request.form.get(f"price_{i}", "").strip()
        consumption = request.form.get(f"consumption_{i}", "").strip()
        phase = request.form.get(f"phase_{i}", "1Phase").strip()

        if not eb or not kw or not price or not consumption:
            return f"All fields for connection {i+1} are required.", 400

        connections.append({
            "eb_number": eb,
            "kw": float(kw),
            "price": int(float(price)),
            "consumption": int(float(consumption)),
            "phase": phase,
        })

    data = {
        "consumer_name": consumer_name,
        "consumer_address": consumer_address,
        "proposal_date": proposal_date,
        "connections": connections,
    }

    pdf_bytes = generate_solar_pdf(data)

    # Create filename
    safe_name = "".join(c for c in consumer_name if c.isalnum() or c in " _-")
    total_kw = sum(c["kw"] for c in connections)
    filename = f"Solar_Proposal_{safe_name}_{total_kw}kW.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


# ─── Internal Cost Calculator (separate feature) ───

@app.route("/calculator", methods=["GET"])
def calculator():
    return render_template("calculator.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    if not data or "entries" not in data:
        return jsonify({"error": "No entries provided"}), 400

    results = []
    for entry in data["entries"]:
        result = calculate_costs(
            kw=float(entry["kw"]),
            customer_type=entry["customer_type"],
            phase=entry["phase"],
            panel_price_per_watt=entry.get("panel_price_per_watt"),
            inverter_price=entry.get("inverter_price"),
            selling_price=float(entry.get("selling_price", 0)),
        )
        results.append(result)

    return jsonify({"results": results})


@app.route("/calculate-excel", methods=["POST"])
def calculate_excel():
    data = request.get_json()
    if not data or "entries" not in data:
        return jsonify({"error": "No entries provided"}), 400

    results = []
    for entry in data["entries"]:
        result = calculate_costs(
            kw=float(entry["kw"]),
            customer_type=entry["customer_type"],
            phase=entry["phase"],
            panel_price_per_watt=entry.get("panel_price_per_watt"),
            inverter_price=entry.get("inverter_price"),
            selling_price=float(entry.get("selling_price", 0)),
        )
        results.append(result)

    excel_bytes = generate_cost_excel(results)

    return send_file(
        BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="Solar_Cost_Analysis.xlsx",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
