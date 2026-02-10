# Tennis Store Management System - Project Scope

## Overview
A comprehensive management system for tennis shops to manage inventory, clients, their rackets, and service/maintenance history (primarily stringing services).

---

## Entities & Relationships

### 1. **User** (Shop Staff/Admin)
Store employees who manage the system and perform services.

**Attributes:**
- `id` (UUID, PK)
- `email` (unique, required)
- `username` (unique, required)
- `hashed_password` (required)
- `first_name` (required)
- `last_name` (required)
- `phone_number` (optional)
- `role` (enum: ADMIN, STAFF)
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- One User → Many MaintenanceRecords (performs services)

---

### 2. **Client** (Tennis Shop Customer)
Customers who own rackets and receive services from the shop.

**Attributes:**
- `id` (UUID, PK)
- `first_name` (required)
- `last_name` (required)
- `email` (unique, optional)
- `phone_number` (required)
- `date_of_birth` (optional)
- `address_line1`, `address_line2` (optional)
- `city`, `postal_code`, `country` (optional)
- `notes` (optional - special preferences)
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- One Client → Many ClientRackets (owns rackets)

---

### 3. **ProductCategory**
Categories for organizing inventory products.

**Attributes:**
- `id` (UUID, PK)
- `name` (unique, required) - e.g., "Racquets", "Strings", "Grips", "Overgrips", "Dampeners", "Bags"
- `slug` (unique, required) - URL-friendly identifier
- `description` (optional)
- `sort_order` (integer, default: 0)
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- One ProductCategory → Many Products

**Common Categories:**
- Racquets
- Strings
- Base Grips
- Overgrips
- Dampeners
- Bags
- Accessories

---

### 4. **Product** (Inventory Item)
Products available in the shop inventory.

**Attributes:**
- `id` (UUID, PK)
- `category_id` (FK → ProductCategory, required)
- `name` (required)
- `brand` (required)
- `model` (optional)
- `sku` (unique, optional)
- `description` (optional)
- `price` (decimal, optional) - retail price
- `cost_price` (decimal, optional) - for profit tracking
- `quantity_in_stock` (integer, default: 0)
- `image_url` (optional)
- `specifications` (JSON, optional) - flexible attributes like:
  - For strings: `{"gauge": "1.25mm", "color": "black", "material": "polyester"}`
  - For grips: `{"thickness": "1.8mm", "color": "white"}`
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- Many Products → One ProductCategory
- Products are referenced in MaintenanceRecords for:
  - Main strings
  - Cross strings
  - Base grips
  - Overgrips
  - Dampeners

---

### 5. **ClientRacket**
Individual rackets owned by clients, tracked in the system.

**Attributes:**
- `id` (UUID, PK)
- `client_id` (FK → Client, required)
- `product_id` (FK → Product, optional) - if the racket is from shop inventory
- `custom_name` (optional) - e.g., "My Wilson Pro Staff"
- `brand` (required)
- `model` (required)
- `serial_number` (optional)
- `purchase_date` (optional)
- `weight_unstrung` (decimal, optional) - in grams
- `grip_size` (required) - e.g., "4 1/4", "4 3/8", "4 1/2"
- `notes` (optional)
- `is_active` (boolean, default: true) - false if client no longer owns it
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- Many ClientRackets → One Client (owner)
- One ClientRacket → Many MaintenanceRecords (service history)
- Many ClientRackets → One Product (optional, if racket is in catalog)

---

### 6. **MaintenanceRecord** (Service/Stringing History)
Records of services performed on client rackets.

**Attributes:**
- `id` (UUID, PK)
- `client_racket_id` (FK → ClientRacket, required)
- `performed_by_user_id` (FK → User, required)
- `service_date` (datetime, default: now)
- `service_type` (enum: STRINGING, REPAIR, OTHER)

**String Configuration:**
- `main_string_id` (FK → Product, optional)
- `cross_string_id` (FK → Product, optional) - can differ from mains
- `main_tension_kg` (decimal, optional) - e.g., 24.5 kg
- `cross_tension_kg` (decimal, optional) - e.g., 23.0 kg
- `string_pattern` (optional) - e.g., "16x19", "18x20"

**Grip Configuration:**
- `base_grip_id` (FK → Product, optional)
- `overgrip_id` (FK → Product, optional)
- `number_of_overgrips` (integer, default: 1)

**Additional Accessories:**
- `dampener_id` (FK → Product, optional)
- `dampener_position` (optional) - e.g., "center", "bottom"

**Service Details:**
- `service_cost` (decimal, required) - amount charged to client
- `duration_minutes` (integer, optional) - time taken
- `notes` (optional) - special requests or observations
- `is_warranty_service` (boolean, default: false)
- `next_service_due_date` (date, optional) - estimated next service
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- Many MaintenanceRecords → One ClientRacket (racket serviced)
- Many MaintenanceRecords → One User (who performed the service)
- MaintenanceRecords reference Products for:
  - Main strings (Many → One)
  - Cross strings (Many → One)
  - Base grips (Many → One)
  - Overgrips (Many → One)
  - Dampeners (Many → One)

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│     User        │
│  (Staff/Admin)  │
└────────┬────────┘
         │
         │ performs
         │
         ▼
┌─────────────────────────┐         ┌──────────────────┐
│   MaintenanceRecord     │◄────────│  ClientRacket    │
│   (Service History)     │ many    │   (Racket)       │
│                         │    for  │                  │
│ - service_type          │         │ - brand          │
│ - main_string_id    ────┼────┐    │ - model          │
│ - cross_string_id   ────┼────┤    │ - grip_size      │
│ - base_grip_id      ────┼────┤    │                  │
│ - overgrip_id       ────┼────┤    └────────┬─────────┘
│ - dampener_id       ────┼────┤             │
│ - main_tension          │    │             │ owned by
│ - cross_tension         │    │             │
│ - service_cost          │    │             ▼
│ - notes                 │    │    ┌──────────────────┐
└─────────────────────────┘    │    │     Client       │
                               │    │   (Customer)     │
                               │    │                  │
                               │    │ - first_name     │
                               │    │ - last_name      │
                               │    │ - phone_number   │
                               │    │ - email          │
                               │    └──────────────────┘
                               │
                               │ references
                               │
                               ▼
                     ┌──────────────────┐
                     │     Product      │
                     │   (Inventory)    │
                     │                  │
                     │ - brand          │
                     │ - name           │
                     │ - price          │
                     │ - quantity       │
                     │ - specifications │
                     └────────┬─────────┘
                              │
                              │ belongs to
                              │
                              ▼
                     ┌──────────────────┐
                     │ ProductCategory  │
                     │                  │
                     │ - name           │
                     │ - slug           │
                     └──────────────────┘
```

---

## Business Workflows

### 1. **Client Registration**
1. Add new client with contact information
2. Optionally add their existing rackets to the system

### 2. **Inventory Management**
1. Create product categories (Strings, Grips, etc.)
2. Add products to inventory with pricing and stock quantities
3. Track stock levels and generate low-stock alerts

### 3. **Racket Registration**
1. Register a client's racket with brand, model, grip size
2. Optionally link to product in inventory (if sold by shop)
3. Track racket details and custom preferences

### 4. **Service/Maintenance Workflow** (Primary Use Case)
1. Client brings racket for service (typically restringing)
2. Staff creates MaintenanceRecord with:
   - Service type (stringing, repair, other)
   - **String configuration:**
     - Select main string from inventory
     - Select cross string (can be different or same as mains)
     - Specify main tension (e.g., 24.5 kg)
     - Specify cross tension (e.g., 23.0 kg)
   - **Grip/Overgrip changes (if requested):**
     - Select base grip from inventory
     - Select overgrip from inventory
     - Specify number of overgrip layers
   - **Dampener (if requested):**
     - Select dampener from inventory
     - Note position (center, bottom, etc.)
   - Service cost
   - Special notes or client preferences
3. Record is saved with timestamp and staff member who performed it
4. Client can view full maintenance history for each racket

### 5. **Reporting & Analytics**
- View client racket configurations and preferences
- Track service history per client/racket
- Monitor product usage (which strings are most popular)
- Track revenue from services
- Identify low-stock items

---

## Key Features

### Client Management
- ✅ Full client profiles with contact details
- ✅ Track multiple rackets per client
- ✅ Client activity status (active/inactive)
- ✅ Custom notes and preferences

### Racket Tracking
- ✅ Detailed racket information (brand, model, grip size, weight)
- ✅ Link rackets to inventory products
- ✅ Track purchase dates and serial numbers
- ✅ Custom naming (e.g., "My favorite racket")
- ✅ Racket ownership status (active/sold/lost)

### Inventory System
- ✅ Categorized product catalog
- ✅ Stock level tracking
- ✅ Low-stock alerts
- ✅ Pricing (retail & cost for profit tracking)
- ✅ Flexible specifications (JSON field for product-specific attributes)
- ✅ SKU management

### Service/Maintenance Tracking
- ✅ Complete stringing records with:
  - Separate main and cross strings
  - Individual tension settings for mains and crosses
  - String pattern tracking
- ✅ Grip and overgrip changes
- ✅ Dampener installation tracking
- ✅ Service cost and duration tracking
- ✅ Warranty service flagging
- ✅ Next service due date estimation
- ✅ Staff attribution (who performed the service)
- ✅ Full service history per racket

### User Management
- ✅ Staff and admin roles
- ✅ User authentication (currently disabled for development)
- ✅ Track who performed each service

---

## Technical Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite (with UUID stored as strings for compatibility)
- **ORM:** SQLAlchemy (async)
- **Authentication:** JWT-based (currently disabled)
- **Data Validation:** Pydantic schemas

---

## Recommended Workflow
python -m uvicorn main:app --reload
Stop any running servers:
    taskkill //F //IM python.exe //T
Clear Python cache (optional, if you have weird issues):
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
Start the server:
    python main.py
Access the API:
    API Docs: http://localhost:8000/docs
    Health Check: http://localhost:8000/health

---

## Future Enhancements (Optional)

- [ ] Point-of-sale (POS) system for product sales
- [ ] Appointment scheduling for services
- [ ] Email/SMS notifications for service completion
- [ ] Client portal for viewing their racket history
- [ ] Inventory auto-depletion when products used in services
- [ ] Revenue analytics and reporting dashboards
- [ ] Barcode/QR code scanning for rackets
- [ ] Multi-store support
- [ ] Photo uploads for rackets and damage documentation
