# 👗 Fashion Ecommerce - Odoo 17 Module

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-blue.svg)](https://github.com/odoo/odoo)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Author](https://img.shields.io/badge/Author-Manzi%20osee-orange.svg)](https://github.com/manziosee)

> 🚀 **A comprehensive fashion retail solution built for the Kigali Odoo Roadshow**

Transform your fashion business with this powerful Odoo module designed specifically for clothing retailers. Whether you're serving individual customers (B2C) or business clients (B2B), this module provides everything you need to manage your fashion inventory and online sales.

## 🌟 Features

### 🎯 **Target Audience Management**
- **Men's Collection** - Curated selection for male customers
- **Women's Collection** - Elegant and trendy women's fashion
- **Children's Collection** - Fun and comfortable kids' clothing

### 🏢 **Business Model Support**
- **B2C Sales** - Direct-to-consumer retail operations
- **B2B Sales** - Wholesale and boutique partnerships
- **Dual Channel** - Seamlessly handle both business models

### 👕 **Fashion-Specific Features**
- **Brand Management** - Track products from Nike, Zara, H&M, Levi's, and more
- **Size Variants** - Complete size range from XS to XXXL
- **Color Tracking** - Organize inventory by color options
- **Material Information** - Cotton, Denim, Silk, Polyester classifications
- **Seasonal Collections** - Spring, Summer, Autumn, Winter, All-Season

### 📦 **Advanced Inventory Management**
- **Stock Level Monitoring** - Min/Max stock level alerts
- **Real-time Availability** - Live inventory tracking
- **Multi-location Support** - Warehouse and store management

### 🌐 **eCommerce Integration**
- **Custom Homepage** - Professional landing page
- **Category Filtering** - Shop by target audience with URL parameters
- **Responsive Design** - Mobile-friendly shopping experience
- **Product Catalog** - Beautiful product cards with detailed information

## 🛠️ Installation

### Prerequisites
- Odoo 17.0+
- Docker & Docker Compose
- Required Odoo modules: `base`, `product`, `sale_management`, `stock`, `account`, `website`, `website_sale`

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/manziosee/fashion_ecommerce.git
cd fashion_ecommerce

# Start the containers
docker-compose up -d

# Install the module via Odoo Apps menu
# Search for "Fashion Ecommerce" and click Install
```

## 🎨 Demo Data

The module includes realistic demo data featuring:

### 👥 **Sample Customers**
- **John Doe** - Individual B2C customer from Kigali
- **Mary Smith** - Individual B2C customer 
- **Kigali Fashion Boutique** - B2B wholesale client

### 👔 **Product Catalog**
- **Nike Men's Casual Shirt** - $45.00
- **Levi's Men's Classic Jeans** - $85.00
- **Adidas Men's Winter Jacket** - $120.00
- **Zara Women's Summer Dress** - $65.00
- **H&M Women's Elegant Blouse** - $55.00
- **GAP Women's Skinny Jeans** - $75.00
- **Disney Kids' Mickey Mouse T-Shirt** - $25.00
- **Nike Kids' Sports Shorts** - $30.00

## 🚀 Usage

### 📊 **Backend Management**
1. Navigate to **Fashion Ecommerce** menu
2. Manage **Products** with fashion-specific attributes
3. Process **Sales Orders** with B2C/B2B classification
4. Monitor inventory levels and stock alerts

### 🛒 **Frontend Shopping**
1. Visit your website homepage (`/`)
2. Browse products by category (`/shop?target_audience=men`)
3. Filter by Men, Women, or Children collections
4. View detailed product information including brand, size, color

### 🎯 **URL Filtering**
- `/shop` - All products
- `/shop?target_audience=men` - Men's collection
- `/shop?target_audience=women` - Women's collection  
- `/shop?target_audience=children` - Children's collection

## 🏗️ **Architecture**

```
fashion_ecommerce/
├── 📁 controllers/          # Web controllers for routing
│   ├── __init__.py         # Controller package initialization
│   └── main.py             # Homepage and shop routing logic
├── 📁 data/                 # Demo data and fixtures
│   └── demo_data.xml       # Fashion products and customers
├── 📁 models/               # Business logic and data models
│   ├── __init__.py         # Models package initialization
│   ├── product.py          # Product template extensions
│   └── sale_order.py       # Sales order extensions
├── 📁 security/             # Access rights and permissions
│   └── ir.model.access.csv # Model access control rules
├── 📁 static/               # Frontend assets
│   └── src/
│       └── css/
│           └── fashion.css  # Custom styling for fashion theme
├── 📁 views/                # XML views and templates
│   ├── menus.xml           # Backend menu structure
│   ├── product_views.xml   # Product form and tree views
│   ├── sale_order_views.xml # Sales order customizations
│   ├── website_assets.xml  # Asset loading configuration
│   ├── website_pages.xml   # Homepage and shop templates
│   └── website_templates.xml # Template inheritance
├── 📄 __init__.py          # Main package initialization
├── 📄 __manifest__.py      # Module configuration and dependencies
└── 📄 README.md           # Project documentation
```

## 🎯 **Business Case Alignment**

This module was specifically designed for the **FashionEcommerce** company case study presented at the Kigali Odoo Roadshow. It addresses all key requirements:

- ✅ **Integrated ERP System** - Unified business management
- ✅ **Online Sales Integration** - eShop functionality
- ✅ **Sales Flow Management** - Order processing and invoicing
- ✅ **Inventory Management** - Stock tracking and alerts
- ✅ **B2C & B2B Support** - Dual business model handling
- ✅ **International Brands** - Support for global fashion brands

## 🤝 **Contributing**

Built with ❤️ for the Odoo community in Rwanda. 

### 📧 **Contact**
- **Author**: Manzi osee
- **GitHub**: [manziosee/fashion_ecommerce](https://github.com/manziosee/fashion_ecommerce.git)
- **Odoo Version**: 17.0

---

*"Easy to configure, Easy to use, Easy to scale"* - Perfect for growing fashion retailers in Rwanda and beyond! 🇷🇼

---

**Made for the Kigali Odoo Roadshow 2025** 🎉
