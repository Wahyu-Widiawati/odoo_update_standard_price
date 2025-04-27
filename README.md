# 🛠️ Odoo Standard Price Update Script

This project automates the update of **Standard Price** values in **Odoo ERP** based on the **latest vendor purchase prices**.  
It uses a two-stage data pipeline:

1. Extract and transform data from Odoo and Vendor Pricelist databases.
2. Update Odoo’s product master data (`ir_property`) with the latest prices.

> This is a portfolio project. All sensitive information (such as credentials) has been removed or masked for public sharing.

---

## 🔧 Tech Stack

- **Python**: Data processing and database interaction
- **PostgreSQL**: Source and target databases
- **Odoo (v17)**: ERP system to update Standard Prices

---

## 🚀 How It Works

```
flowchart TD
    OdooDB[(Odoo Database - odoo_dev)] --> PyScript[odoo_update_standard_price.py]
    VendorDB[(Vendor Pricelist Database - cdw_prod)] --> PyScript
    PyScript --> Backup[Optional Backup of ir_property]
    PyScript --> UpdateStandardPrice[Update Standard Price in Odoo]
```

---

## 📋 Process Overview

- **Backup** the `ir_property` table (optional).
- **Fetch** current `standard_price` values from Odoo.
- **Fetch** latest vendor prices from the Vendor Pricelist database.
- **Update** product standard prices in Odoo where applicable.
- **Commit** all changes safely.

---

## ✨ Future Enhancements

- Add full logging instead of print statements.
- Add a dry-run mode for previewing updates.

---
