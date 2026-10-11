# Pick-to-Light Material Hub System

A repository-ready starter project for a manufacturing Pick-to-Light system. When a trolley arrives at the material hub, the operator scans/enters its trolley ID. The system looks up the trolley's manufacturing order (MO), style, and required materials/stickers, then activates the relevant pick-to-light locations. The operator presses each location's confirmation button after picking. Once all required items are confirmed, the trolley is marked complete and the hub is ready for the next trolley.

## Main workflow

1. **Trolley arrives:** identify the trolley by ID (barcode/RFID integration can be added).
2. **Database lookup:** retrieve MO, style, and required material/sticker quantities.
3. **Light activation:** activate the indicator at every required bin/box.
4. **Pick confirmation:** operator presses the button at each activated box.
5. **Completion:** when all required picks are confirmed, close the trolley task.
6. **Low-stock warning:** low inventory triggers a blinking warning state and appears on the dashboard.
7. **Restocking:** an authorized operator records replenishment and stock returns to normal when it rises above the threshold.

## MVP included

- Python Flask web app
- SQLite database (runs without a separate database server)
- Trolley/MO/style/material/sticker records
- Pick task creation and confirmation
- Bin light states: `OFF`, `ON`, `BLINKING_LOW_STOCK`, `CONFIRMED`
- Low-stock warnings and restock form
- Demo seed data
- Simple dashboard and JSON API

> **Hardware integration note:** This MVP simulates LEDs and push buttons in software. Actual LED modules and physical push buttons need a controller interface (for example ESP32 over MQTT/HTTP, a PLC, or a vendor-specific controller). No hardware protocol was specified, so the app isolates the light-control logic in `hardware.py` for safe replacement with your real integration.

## Requirements

- Python 3.10+
- Windows, Linux, or macOS

## Run on Windows (PowerShell)

```powershell
cd pick-to-light-system
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Run on Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Demo workflow

1. Open the dashboard.
2. Enter trolley ID `TRL-001` and click **Start trolley**.
3. The system creates a task using the demo MO/style requirements.
4. Click **Confirm picked** for each active material/bin.
5. When all lines are confirmed, the task is completed.
6. Use the **Restock** form to add stock to a bin. Low-stock bins show a blinking warning style.

## Repository structure

```text
pick-to-light-system/
├── app.py                 # Flask routes and workflow
├── database.py            # DB connection, schema, seed data
├── hardware.py            # Simulated light/button adapter; replace for real hardware
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   └── index.html         # Dashboard UI
└── static/
    └── style.css
```

## Core data model

- `trolleys`: trolley ID and assigned MO/style
- `orders`: manufacturing order and style
- `order_requirements`: materials/stickers and required quantity per order
- `bins`: physical box/bin, material, current stock, low-stock threshold, controller address
- `pick_tasks`: task created for a trolley/order
- `pick_task_lines`: per-bin requirement, picked quantity, and confirmation status
- `stock_movements`: auditable replenishment records

For a production deployment, use PostgreSQL, authenticated user roles, audit logging, network segmentation, controller acknowledgements, and transactional updates. Do not connect real actuators until emergency-stop, timeout, fault, and wrong-bin behavior have been tested.
