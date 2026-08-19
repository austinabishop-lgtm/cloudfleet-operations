from flask import Flask, render_template_string
import json
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
VEHICLES_FILE = BASE_DIR / "data" / "vehicles.json"
MISSIONS_FILE = BASE_DIR / "data" / "missions.json"


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


@app.route("/")
def dashboard():
    vehicles = load_json(VEHICLES_FILE)
    missions = load_json(MISSIONS_FILE)

    total_vehicles = len(vehicles)
    available = sum(1 for vehicle in vehicles if vehicle["status"] == "available")
    dispatched = sum(1 for vehicle in vehicles if vehicle["status"] == "dispatched")
    maintenance = sum(1 for vehicle in vehicles if vehicle["status"] == "maintenance")

    availability_percent = round((available / total_vehicles) * 100) if total_vehicles else 0

    alerts = []

    for vehicle in vehicles:
        if vehicle["maintenance_required"]:
            alerts.append(
                f'{vehicle["vehicle_id"]} requires maintenance attention.'
            )

    if availability_percent < 50:
        alerts.append("Fleet availability is below 50%.")

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CloudFleet Operations Platform</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                background-color: #f4f6f8;
                color: #1f2937;
            }

            header {
                background-color: #111827;
                color: white;
                padding: 24px 40px;
            }

            header h1 {
                margin: 0;
                font-size: 30px;
            }

            header p {
                margin-top: 8px;
                color: #d1d5db;
            }

            .container {
                padding: 30px 40px;
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }

            .card {
                background: white;
                border-radius: 10px;
                padding: 22px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            .card h3 {
                margin-top: 0;
                font-size: 15px;
                color: #6b7280;
                text-transform: uppercase;
            }

            .number {
                font-size: 34px;
                font-weight: bold;
                margin-top: 10px;
            }

            .section {
                background: white;
                border-radius: 10px;
                padding: 24px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }

            th, td {
                padding: 12px;
                border-bottom: 1px solid #e5e7eb;
                text-align: left;
            }

            th {
                background-color: #f9fafb;
            }

            .status {
                font-weight: bold;
                text-transform: capitalize;
            }

            .alert {
                background-color: #fff7ed;
                border-left: 5px solid #f97316;
                padding: 12px 15px;
                margin-top: 10px;
                border-radius: 5px;
            }

            .healthy {
                background-color: #ecfdf5;
                border-left: 5px solid #10b981;
                padding: 12px 15px;
                border-radius: 5px;
            }

            footer {
                text-align: center;
                padding: 20px;
                color: #6b7280;
            }

            @media (max-width: 900px) {
                .summary-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 600px) {
                .summary-grid {
                    grid-template-columns: 1fr;
                }

                .container {
                    padding: 20px;
                }
            }
        </style>
    </head>

    <body>

        <header>
            <h1>CloudFleet Operations Platform</h1>
            <p>Transportation readiness, mission visibility, and fleet status dashboard</p>
        </header>

        <div class="container">

            <div class="summary-grid">
                <div class="card">
                    <h3>Total Vehicles</h3>
                    <div class="number">{{ total_vehicles }}</div>
                </div>

                <div class="card">
                    <h3>Available</h3>
                    <div class="number">{{ available }}</div>
                </div>

                <div class="card">
                    <h3>Dispatched</h3>
                    <div class="number">{{ dispatched }}</div>
                </div>

                <div class="card">
                    <h3>Maintenance</h3>
                    <div class="number">{{ maintenance }}</div>
                </div>
            </div>

            <div class="section">
                <h2>Operational Alerts</h2>

                {% if alerts %}
                    {% for alert in alerts %}
                        <div class="alert">
                            ⚠ {{ alert }}
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="healthy">
                        ✓ No active operational alerts.
                    </div>
                {% endif %}
            </div>

            <div class="section">
                <h2>Active Missions</h2>

                <table>
                    <tr>
                        <th>Mission</th>
                        <th>Vehicle</th>
                        <th>Driver</th>
                        <th>Destination</th>
                        <th>Priority</th>
                        <th>Status</th>
                    </tr>

                    {% for mission in missions %}
                    <tr>
                        <td>{{ mission["mission_id"] }}</td>
                        <td>{{ mission["vehicle_id"] }}</td>
                        <td>{{ mission["driver"] }}</td>
                        <td>{{ mission["destination"] }}</td>
                        <td>{{ mission["priority"] }}</td>
                        <td class="status">{{ mission["status"].replace("_", " ") }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            <div class="section">
                <h2>Fleet Status</h2>

                <table>
                    <tr>
                        <th>Vehicle</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Location</th>
                        <th>Maintenance Required</th>
                    </tr>

                    {% for vehicle in vehicles %}
                    <tr>
                        <td>{{ vehicle["vehicle_id"] }}</td>
                        <td>{{ vehicle["type"] }}</td>
                        <td class="status">{{ vehicle["status"] }}</td>
                        <td>{{ vehicle["location"] }}</td>
                        <td>{{ "Yes" if vehicle["maintenance_required"] else "No" }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

        </div>

        <footer>
            CloudFleet Operations Platform — Cloud Engineering Portfolio Project
        </footer>

    </body>
    </html>
    """

    return render_template_string(
        html,
        vehicles=vehicles,
        missions=missions,
        total_vehicles=total_vehicles,
        available=available,
        dispatched=dispatched,
        maintenance=maintenance,
        alerts=alerts,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
