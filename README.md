# Pick-to-Light Material Hub System

## Project Overview

The **Pick-to-Light Material Hub System** is a smart manufacturing solution designed to improve material and sticker picking accuracy, reduce manual searching, and support timely replenishment in garment manufacturing.

When a trolley arrives at its designated position in front of the material hub, the system identifies the trolley and queries the database to retrieve its **Manufacturing Order (MO), style, and required materials or stickers**. The relevant pick-to-light indicators activate at the assigned storage boxes, guiding the operator to the correct items.

After picking the required material, the operator presses the confirmation button integrated into the corresponding indicator box. Once all required items are confirmed, the trolley's picking cycle is completed and the material hub is ready to process the next trolley.

The system also monitors material availability. When stock reaches its configured low-stock threshold, the corresponding indicator flashes to alert the operator that replenishment is required.

## Objectives

- Guide operators to the correct material and sticker locations.
- Retrieve trolley-specific MO, style, and material requirements from a database.
- Reduce material picking errors and unnecessary searching.
- Confirm each pick through the push button integrated with the indicator.
- Monitor inventory levels and provide visual low-stock warnings.
- Support faster trolley turnaround and a more organized material supply process.

## System Workflow

1. **Trolley arrival:** A trolley reaches its designated position in front of the material hub.
2. **Trolley identification:** The system identifies the trolley using an available method such as RFID, barcode scanning, or manual entry.
3. **Database query:** The system retrieves the associated MO, style, required materials or stickers, and required quantities.
4. **Pick-to-light activation:** Indicators at the relevant storage boxes illuminate to guide the operator.
5. **Picking and confirmation:** The operator picks the specified material and presses the corresponding push button to confirm completion.
6. **Task validation:** The system checks that all required picks for the trolley have been confirmed.
7. **Trolley completion:** Once all required picks are confirmed, the picking cycle closes and the hub can accept the next trolley.
8. **Low-stock alert:** If a material reaches its configured low-stock threshold, its indicator flashes to signal that replenishment is needed.
9. **Restocking:** The responsible operator replenishes the relevant box and updates the inventory record.

## Main Functional Components

- **Trolley identification:** Identifies the trolley at the material hub.
- **Database interface:** Provides MO, style, material, sticker, and quantity information.
- **Pick-to-light indicators:** Identify the storage boxes required for the current trolley.
- **Push-button confirmation:** Records the operator's confirmation for each required pick.
- **Inventory monitoring:** Tracks stock levels for materials and stickers.
- **Low-stock warning:** Uses a flashing indicator to identify boxes that need replenishment.
- **Task management:** Tracks picking progress and marks a trolley cycle complete when all required items are confirmed.

## Expected Benefits

- Improved picking accuracy and reduced risk of supplying incorrect materials or stickers.
- Reduced operator time spent searching for items.
- Better visibility of material requirements for each trolley and manufacturing order.
- Faster and more consistent trolley preparation.
- Earlier identification of low-stock materials.
- Improved inventory control and replenishment planning.
- Better traceability of picking activity when integrated with production and inventory databases.

## Implementation Considerations

The final implementation will depend on the factory's existing database, trolley identification method, indicator hardware, and controller communication protocol. The database should be connected to the authoritative source of MO and style requirements. Each indicator and push button should be mapped to its physical storage location.

For production use, the system should also include user access control, event logging, error handling, protection against duplicate confirmations, and clear handling of missing or insufficient stock. Physical hardware integration and end-to-end testing are required before operational deployment.

## Project Scope

This project covers the design of a database-driven pick-to-light workflow for material and sticker preparation at a manufacturing material hub. It combines trolley identification, order-based material lookup, visual picking guidance, button-based confirmation, task completion, and low-stock replenishment alerts.
