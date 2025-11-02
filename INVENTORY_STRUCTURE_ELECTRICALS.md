# 🔌 Electrical Shop - Inventory Structure Guide

## 📚 Understanding the Hierarchy

```
GROUP (Top Level - Product Line)
  └─ CATEGORY (Mid Level - Product Type)
      └─ ITEM (Bottom Level - Specific Product)
```

---

## 🏗️ Complete Structure for Electrical Shop

### **GROUP 1: Fans** 🌀

**Purpose:** All types of fans (ceiling, table, exhaust, etc.)

#### Categories:
1. **Ceiling Fans** - Standard ceiling mounted fans
2. **Table Fans** - Portable table/desk fans
3. **Exhaust Fans** - Kitchen/bathroom exhaust
4. **Wall Fans** - Wall mounted fans
5. **Pedestal Fans** - Stand fans

#### Example Items:
```
Group: Fans
Category: Ceiling Fans
Items:
  - Bajaj Ceiling Fan 48" (1200mm) - White
  - Bajaj Ceiling Fan 48" (1200mm) - Brown
  - HBL Premium Ceiling Fan 52" - White
  - Havells SS-390 Ceiling Fan 48" - Pearl White
  - Havells Leganza Ceiling Fan 52" - Brown
```

---

### **GROUP 2: Electrical Accessories** ⚡

**Purpose:** Switches, sockets, MCBs, and related electrical fittings

#### Categories:
1. **Switches & Sockets** - Wall switches, power sockets
2. **Switch Plates** - Cover plates for switches
3. **MCBs & Distribution** - Circuit breakers, DB boxes
4. **Extension Boards** - Multi-plug boards
5. **Electrical Boxes** - Concealed boxes for switches

#### Example Items:
```
Group: Electrical Accessories
Category: Switches & Sockets
Items:
  - Anchor Penta 6A Switch - White
  - Anchor Penta 16A Socket - White
  - Vega Modular Switch 6A - Ivory
  - REO 6A 2-Way Switch - White
  - REO 16A Socket with USB Charger
```

---

### **GROUP 3: Wiring & Fittings** 🔧

**Purpose:** Pipes, conduits, cable management, and related accessories

#### Categories:
1. **PVC Pipes & Conduits** - Electrical conduit pipes
2. **Pipe Fittings** - Elbows, bends, couplers
3. **Clamps & Bands** - Pipe mounting accessories
4. **Cable Trays** - Cable management
5. **Junction Boxes** - T-joints, distribution boxes

#### Example Items:
```
Group: Wiring & Fittings
Category: PVC Pipes & Conduits
Items:
  - PVC Conduit Pipe 20mm (3 meter)
  - PVC Conduit Pipe 25mm (3 meter)
  - Flexible Conduit Pipe 20mm

Category: Pipe Fittings
Items:
  - PVC Elbow 20mm - 90 Degree
  - PVC Elbow 25mm - 90 Degree
  - PVC Bend 20mm - 45 Degree
  - PVC T-Joint 20mm
  - PVC Coupler 20mm

Category: Clamps & Bands
Items:
  - Saddle Clamp 20mm (Pack of 10)
  - Metal Band 20mm (Pack of 10)
  - Pipe Clip 25mm (Pack of 10)
```

---

### **GROUP 4: Lighting** 💡

**Purpose:** All lighting products - LED, bulbs, tubes, etc.

#### Categories:
1. **LED Bulbs** - Standard LED bulbs
2. **LED Battens** - Tube lights, battens
3. **Downlights** - Recessed lighting
4. **Panel Lights** - Ceiling panels
5. **Street Lights** - Outdoor lighting
6. **Emergency Lights** - Battery backup lights
7. **Decorative Lights** - String lights, spotlights

#### Example Items:
```
Group: Lighting
Category: LED Bulbs
Items:
  - Bajaj LED Bulb 9W - Cool White (B22)
  - Bajaj LED Bulb 12W - Warm White (B22)
  - Orient LED Bulb 7W - Cool Day Light (B22)
  - Orient LED Bulb 9W - Warm White (B22)
  - Havells LED Bulb 9W - Cool White (B22)

Category: LED Battens
Items:
  - Bajaj LED Batten 20W (2 feet)
  - Orient LED Batten 20W (2 feet)
  - Bajaj LED Batten 40W (4 feet)
  - Orient LED Batten 40W (4 feet)
```

---

### **GROUP 5: Wires & Cables** 🔌

**Purpose:** Electrical wires and cables

#### Categories:
1. **House Wire (Single Core)** - 1.0mm, 1.5mm, 2.5mm
2. **Flexible Wire (Multi Strand)** - For appliances
3. **Submersible Cables** - For pumps
4. **Coaxial Cables** - For TV/internet
5. **Telephone Cables** - Telecom wiring

#### Example Items:
```
Group: Wires & Cables
Category: House Wire (Single Core)
Items:
  - Finolex House Wire 1.0mm - Red (90m coil)
  - Finolex House Wire 1.5mm - Black (90m coil)
  - KEI House Wire 2.5mm - Red (90m coil)
  - Polycab House Wire 2.5mm - Black (90m coil)
```

---

### **GROUP 6: Tools & Testers** 🔧

**Purpose:** Electrical tools and testing equipment

#### Categories:
1. **Hand Tools** - Pliers, cutters, strippers
2. **Testers & Meters** - Voltage testers, multimeters
3. **Drilling Tools** - Hole saws, drill bits
4. **Soldering Equipment** - Soldering irons, wire
5. **Safety Equipment** - Gloves, goggles, tape

---

## 📋 **Quick Decision Guide**

### When Creating Groups:
- **Think Product Line:** What section of your shop?
- **Think Customer:** What do they ask for?
- Examples: "Do you have fans?", "I need wiring materials", "Show me LED lights"

### When Creating Categories:
- **Think Product Type:** What specific type?
- **Think Usage:** Where/how is it used?
- Examples: "Ceiling fan", "Wall socket", "PVC pipe", "LED bulb"

### When Creating Items:
- **Think SKU:** Unique product with price
- **Include:** Brand, Model, Size, Color, Specs
- Examples: "Bajaj Ceiling Fan 48" - White", "Anchor Penta 6A Switch - White"

---

## 🎯 **Complete Structure Example**

```
FANS (Group)
├── Ceiling Fans (Category)
│   ├── Bajaj Ceiling Fan 48" - White (Item)
│   ├── Bajaj Ceiling Fan 48" - Brown (Item)
│   ├── HBL Premium Fan 52" - White (Item)
│   └── Havells SS-390 48" - Pearl White (Item)
│
├── Table Fans (Category)
│   ├── Bajaj Table Fan 400mm - White (Item)
│   └── Orient Table Fan 400mm - Blue (Item)
│
└── Exhaust Fans (Category)
    ├── Bajaj Exhaust Fan 8" (200mm) (Item)
    └── Havells Exhaust Fan 12" (300mm) (Item)

ELECTRICAL ACCESSORIES (Group)
├── Switches & Sockets (Category)
│   ├── Anchor Penta 6A Switch - White (Item)
│   ├── Anchor Penta 16A Socket - White (Item)
│   ├── Vega Modular Switch 6A - Ivory (Item)
│   └── REO 6A 2-Way Switch - White (Item)
│
└── MCBs & Distribution (Category)
    ├── Anchor MCB 16A Single Pole (Item)
    └── Anchor MCB 32A Double Pole (Item)

WIRING & FITTINGS (Group)
├── PVC Pipes & Conduits (Category)
│   ├── PVC Conduit Pipe 20mm (3m) (Item)
│   └── PVC Conduit Pipe 25mm (3m) (Item)
│
├── Pipe Fittings (Category)
│   ├── PVC Elbow 20mm - 90° (Item)
│   ├── PVC T-Joint 20mm (Item)
│   └── PVC Coupler 20mm (Item)
│
└── Clamps & Bands (Category)
    ├── Saddle Clamp 20mm (Pack of 10) (Item)
    └── Metal Band 20mm (Pack of 10) (Item)

LIGHTING (Group)
├── LED Bulbs (Category)
│   ├── Bajaj LED 9W Cool White B22 (Item)
│   ├── Bajaj LED 12W Warm White B22 (Item)
│   ├── Orient LED 7W Cool Day B22 (Item)
│   └── Orient LED 9W Warm White B22 (Item)
│
└── LED Battens (Category)
    ├── Bajaj LED Batten 20W (2ft) (Item)
    └── Orient LED Batten 40W (4ft) (Item)
```

---

## 📊 **Sample Inventory Table**

| Group | Category | Item Name | SKU | Unit | Stock | Price | Tax % | HSN |
|-------|----------|-----------|-----|------|-------|-------|-------|-----|
| Fans | Ceiling Fans | Bajaj Ceiling Fan 48" White | BAJ-CF-48-WHT | Pcs | 15 | 1450 | 18 | 8414 |
| Fans | Ceiling Fans | HBL Premium Fan 52" White | HBL-CF-52-WHT | Pcs | 10 | 1850 | 18 | 8414 |
| Electrical Accessories | Switches & Sockets | Anchor Penta 6A Switch White | ANC-SW-6A-WHT | Pcs | 50 | 85 | 18 | 8536 |
| Electrical Accessories | Switches & Sockets | Vega Modular Switch 6A Ivory | VEG-SW-6A-IVR | Pcs | 30 | 95 | 18 | 8536 |
| Wiring & Fittings | PVC Pipes | PVC Conduit Pipe 20mm 3m | PVC-P-20-3M | Pcs | 100 | 45 | 18 | 3917 |
| Wiring & Fittings | Pipe Fittings | PVC Elbow 20mm 90° | PVC-ELB-20-90 | Pcs | 200 | 8 | 18 | 3917 |
| Wiring & Fittings | Clamps & Bands | Metal Band 20mm Pack-10 | MTL-BND-20-P10 | Pack | 50 | 25 | 18 | 7326 |
| Lighting | LED Bulbs | Bajaj LED 9W Cool White B22 | BAJ-LED-9W-CW | Pcs | 80 | 120 | 12 | 8539 |
| Lighting | LED Bulbs | Orient LED 7W Cool Day B22 | ORI-LED-7W-CD | Pcs | 60 | 110 | 12 | 8539 |
| Lighting | LED Battens | Bajaj LED Batten 20W 2ft | BAJ-BTN-20W-2F | Pcs | 25 | 450 | 12 | 8539 |

---

## 💡 **Pro Tips**

### 1. **Brand-Based Grouping (Alternative)**
If you primarily stock specific brands:
```
BAJAJ PRODUCTS (Group)
├── Ceiling Fans (Category)
├── Table Fans (Category)
└── LED Lights (Category)

HAVELLS PRODUCTS (Group)
├── Ceiling Fans (Category)
├── Switches (Category)
└── MCBs (Category)
```

### 2. **SKU Naming Convention**
```
Format: BRAND-TYPE-SIZE-COLOR
Examples:
- BAJ-CF-48-WHT (Bajaj Ceiling Fan 48" White)
- ANC-SW-6A-WHT (Anchor Switch 6A White)
- PVC-ELB-20-90 (PVC Elbow 20mm 90°)
- ORI-LED-9W-CW (Orient LED 9W Cool White)
```

### 3. **Common Units**
- **Fans:** Pcs (pieces)
- **Switches:** Pcs
- **Pipes:** Pcs or Meter
- **LED Bulbs:** Pcs
- **Wire:** Meter or Coil
- **Clamps/Bands:** Pcs or Pack

### 4. **HSN Codes for Electricals**
- **8414:** Fans (ceiling, table, exhaust)
- **8536:** Switches, sockets, MCBs
- **3917:** PVC pipes and fittings
- **8539:** LED bulbs, lights, lamps
- **8544:** Electrical wires and cables
- **7326:** Metal clamps, bands, fittings

---

## 🎯 **Recommended Structure for Your Shop**

Based on your products, I recommend:

### **6 Main Groups:**
1. **Fans** (Bajaj, HBL, Havells - all fan types)
2. **Electrical Accessories** (Anchor Penta, Vega, REO - switches, sockets)
3. **Wiring & Fittings** (PVC pipes, elbows, bands, T-joints)
4. **Lighting** (Bajaj, Orient - LED bulbs, battens)
5. **Wires & Cables** (Single core, flexible, submersible)
6. **Tools & Testers** (Hand tools, testing equipment)

### **Benefits:**
- ✅ Easy to navigate for customers
- ✅ Matches how you think about inventory
- ✅ Simple to expand (add new categories as you grow)
- ✅ Clear reporting (sales by group/category)
- ✅ Professional structure

---

## 📝 **What to Put in Excel Template**

For your test import, I'll create an Excel file with:
- **50+ sample items** covering all groups
- **Realistic prices** for electrical shop
- **Proper SKU format**
- **Correct HSN codes**
- **Ready to import!**

---

## 🚀 **Next Steps**

1. **Download the Excel file** I'm creating (BizBooks_Electricals_Sample_Inventory.xlsx)
2. **Review the structure** - Groups, Categories, Items
3. **Modify as needed** - Change prices, add your items
4. **Import to BizBooks** - Bulk Import → Upload
5. **Start using!** - Create invoices, track stock

---

**💡 Remember:** You can always add more categories and items later. Start with the basics, then expand as your business grows!

