# RAPSEB FIWARE Stack

## Project

Optional FIWARE/NGSI-LD integration for the RAPSEB spraying workcell. Captures per-pass and per-session spray data, stores it in Orion-LD context broker, and visualises it in Grafana. This is an add-on to the main robotic_arm_spraying_jazzy codebase.

## Stack

- Orion-LD 1.6.0 (NGSI-LD context broker)
- MongoDB 6.0 (persistence)
- Grafana 10.4.0 with yesoreyeram-infinity-datasource plugin
- Python 3 (ROS 2 bridge, data generation, Orion client)
- ROS 2 Jazzy (optional, for live bridge only)

## Layout

```
docker-compose.yml              # Orion-LD + MongoDB + Grafana
ngsi_ld/
  data_models.py                # SprayPass and SpraySession entity builders
scripts/
  orion_client.py               # HTTP client for Orion-LD (upsert, query, delete, healthy)
  ros_bridge.py                 # ROS 2 node: subscribes /rapseb/spray_status -> pushes to Orion-LD
  generate_demo_data.py         # Generates realistic CSV + NGSI-LD JSON demo data
  render_dashboard.py           # Renders dashboard PNGs from CSV data (matplotlib)
config/grafana/
  dashboards/rapseb-overview.json  # 4-panel Grafana dashboard
  provisioning/                    # Datasource and dashboard provisioning
data/                              # Generated CSV and JSON output
docs/                              # Dashboard screenshots
```

## NGSI-LD Entities

Only two entity types (defined in ngsi_ld/data_models.py):
- **SprayPass** - individual spray pass with coveragePercentage, epoxyUsed, duration, passNumber
- **SpraySession** - per-board session with totalPasses, finalCoveragePercentage, totalEpoxyUsed, status

No other entity types (old types like RobotState, SafetyEvent, KPIMetric were removed).

## ROS 2 Interface

The bridge (scripts/ros_bridge.py) subscribes to `/rapseb/spray_status` (std_msgs/String with JSON). Two event types:
- `pass_complete` -> creates SprayPass entity
- `session_complete` -> creates SpraySession entity

The main spraying codebase does not yet publish to this topic. This is the intended integration point.

## Running

```bash
docker compose up -d                    # Start stack
python scripts/generate_demo_data.py    # Generate demo data
python scripts/render_dashboard.py      # Render dashboard PNGs
```

Grafana: http://localhost:3000 (rapseb / arise2026)

## Demo Data

generate_demo_data.py produces 38 sessions across 3 days with seed-based randomisation (seed=2023 gives exactly 1 aborted session). Coverage ranges 96.5-99.4% for completed boards. Per-pass progression: ~50% -> ~80% -> ~95% -> ~98%.

## Common Pitfalls

- The Grafana dashboard uses the Infinity datasource plugin reading CSV files, not direct Orion-LD queries. This is simpler for demo/review purposes.
- Timestamps in CSV must not have both +00:00 and Z suffix. Use isoformat() without appending Z.
- orion_client.py uses NGSI-LD v1 API at /ngsi-ld/v1/entities.

## Style

- Minimal code, no unnecessary abstractions.
- Direct, technical language. No filler.
- Maintainer: Parity Platform P.C.
