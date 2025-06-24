# Database Schema Documentation
## Multi-Agent Custom Automation Engine Solution Accelerator

*Last Updated: June 24, 2025*

---

## Table of Contents
1. [Overview](#overview)
2. [Database Architecture](#database-architecture)
3. [Table Descriptions](#table-descriptions)
4. [Table Relationships](#table-relationships)
5. [Business Questions Analysis](#business-questions-analysis)
6. [Data Model Design Patterns](#data-model-design-patterns)
7. [Key Metrics and KPIs](#key-metrics-and-kpis)

---

## Overview

This document provides comprehensive documentation for the sales analytics database schema used in the Multi-Agent Custom Automation Engine Solution Accelerator. The database follows a star schema design pattern optimized for business intelligence and analytics workloads, supporting comprehensive sales analysis across customer, product, time, and geographic dimensions.

### Database Context
- **Industry:** Consumer Goods/Beverage Distribution
- **Primary Use Case:** Sales Analytics, Customer Intelligence, Territory Management
- **Schema Pattern:** Star Schema with Fact and Dimension Tables
- **Geographic Scope:** Multi-region distribution network with CEDI (Distribution Centers)

---

## Database Architecture

The database consists of 6 core tables organized in a star schema pattern:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   cliente   │────│ cliente_cedi │────│   mercado   │
│ (Customer   │    │ (Customer-   │    │ (Market/    │
│  Master)    │    │  CEDI Link)  │    │  Geography) │
└─────────────┘    └──────────────┘    └─────────────┘
       │                                       │
       │           ┌─────────────┐            │
       │           │   tiempo    │            │
       │           │ (Time Dim)  │            │
       │           └─────────────┘            │
       │                  │                   │
       │                  │                   │
       └──────────────────▼───────────────────┘
                    ┌─────────────┐
                    │segmentacion │ ◄─────┐
                    │ (Sales Fact │       │
                    │   Table)    │       │
                    └─────────────┘       │
                           ▲              │
                           │              │
                    ┌─────────────┐       │
                    │  producto   │───────┘
                    │ (Product    │
                    │  Master)    │
                    └─────────────┘
```

---

## Table Descriptions

### 1. `cliente` (Customer Master Table)
**Purpose:** Central repository for customer master data and attributes

**Primary Key:** `customer_id`

**Key Columns:**
- `customer_id` (varchar, 56) - Unique customer identifier
- `Canal_Comercial` (varchar, 80) - Commercial channel classification
- `SubcanalComercial` (varchar, 102) - Commercial subchannel
- `MedidadeclienteIndustria` (varchar, 40) - Customer industry measure
- `CanalIISSCOM` (varchar, 66) - IISSCOM channel classification
- `SubCanalIISSCOM` (varchar, 80) - IISSCOM subchannel
- `Nombre_cliente` (varchar, 88) - Customer name
- `Cliente_facturable` (varchar, 22) - Billable customer flag
- `ID_Cliente_facturable` (varchar, 60) - Billable customer ID
- `Cuenta_clave` (varchar, 70) - Key account designation
- `customer_zone_d` (varchar, 80) - Customer zone
- `Territorio_del_cliente` (varchar, 80) - Customer territory
- `Tamano_cliente` (varchar, 50) - Customer size classification
- `Estatus_del_cliente` (varchar, 38) - Customer status
- Geographic fields: `Latitud`, `Longitud`, `Codigo_Postal`, `Entre_calles`

**Business Purpose:**
- Customer segmentation and classification
- Channel and territory management
- Key account identification
- Geographic analysis and routing

---

### 2. `cliente_cedi` (Customer-CEDI Relationship Bridge Table)
**Purpose:** Links customers to their serving distribution centers (CEDIs)

**Primary Key:** `customer_id`, `distribution_channel_id`

**Key Columns:**
- `customer_id` (varchar, 22) - Customer identifier (FK to cliente)
- `cedi_id` (varchar, 22) - Distribution center ID (FK to mercado)
- `distribution_channel_id` (varchar, 4) - Distribution channel identifier
- `customer_distribution_id` (varchar, 28) - Combined customer-distribution ID
- `Region` (varchar, 18) - Regional classification
- `CEDI` (varchar, 50) - Distribution center name
- `Territorio` (varchar, 30) - Territory designation
- `Subterritorio` (varchar, 28) - Sub-territory designation
- `LocalForaneo` (varchar, 14) - Local/Foreign classification

**Business Purpose:**
- Customer-to-CEDI assignment management
- Territory and route planning
- Distribution channel analysis
- Regional performance tracking

---

### 3. `mercado` (Market/Geography Master Table)
**Purpose:** Master data for market hierarchy and geographic organization

**Primary Key:** `CEDIid`

**Key Columns:**
- `CEDIid` (varchar, 8) - Distribution center unique identifier
- `CEDI` (varchar, 50) - Distribution center name
- `Zona` (varchar, 18) - Zone classification
- `Territorio` (varchar, 30) - Territory designation
- `Subterritorio` (varchar, 28) - Sub-territory designation
- `LocalForaneo` (varchar, 14) - Local/Foreign market classification

**Business Purpose:**
- Geographic hierarchy management
- Market segmentation
- Performance comparison across regions
- Expansion planning and coverage analysis

---

### 4. `producto` (Product Master Table)
**Purpose:** Comprehensive product catalog and classification system

**Primary Key:** `Material`

**Key Columns:**
- `Material` (varchar, 36) - Material/SKU code (unique product identifier)
- `Producto` (varchar, 82) - Product name/description
- `Categoria` (varchar, 52) - Product category (e.g., carbonated, non-carbonated)
- `Subcategoria` (varchar, 60) - Product subcategory
- `AgrupadordeMarca` (varchar, 40) - Brand grouping
- `SaborGlobal` (varchar, 52) - Global flavor classification
- `Retornabilidad` (varchar, 26) - Returnability (returnable vs non-returnable)
- `Contenido` (varchar, 30) - Content/volume specification
- `Medida` (varchar, 20) - Measurement unit
- `TipodeEmpaque` (varchar, 20) - Package type
- `Extensiondelinea1` (varchar, 36) - Product line extension 1
- `Extensiondelinea2` (varchar, 50) - Product line extension 2

**Business Purpose:**
- Product portfolio management
- Category and brand analysis
- Packaging and format optimization
- New product launch tracking

---

### 5. `segmentacion` (Sales Fact Table)
**Purpose:** Central fact table containing all sales transactions and metrics

**Primary Key:** `customer_id`, `calday`, `material_id`, `distribution_channel_id`

**Key Columns:**
- `customer_id` (varchar, 20) - Customer identifier (FK to cliente)
- `calday` (date) - Transaction date (FK to tiempo)
- `material_id` (varchar, 36) - Product identifier (FK to producto)
- `distribution_channel_id` (varchar, 4) - Distribution channel
- `CALMONTH` (int) - Calendar month identifier
- `customer_distribution_id` (varchar, 26) - Customer-distribution combination
- **Sales Metrics:**
  - `VentasCajasUnidad` (float) - Sales in case units
  - `IngresoNetoSImpuestos` (float) - Net revenue without taxes
  - `VentasCajasOriginales` (float) - Original case sales
  - `net_revenue` (float) - Net revenue
  - `bottles_sold_m` (float) - Bottles sold (in millions)
- `Cobertura` (int) - Coverage metric

**Business Purpose:**
- Sales performance tracking
- Revenue analysis
- Volume metrics monitoring
- Customer purchase behavior analysis
- Coverage and penetration measurement

---

### 6. `tiempo` (Time Dimension Table)
**Purpose:** Comprehensive time dimension for temporal analysis

**Primary Key:** `Fecha`

**Key Columns:**
- `Fecha` (date) - Calendar date
- `Year` (int) - Year
- `NumMes` (int) - Month number (1-12)
- `Dia` (int) - Day of month
- `Q` (int) - Quarter (1-4)
- `Semana` (int) - Week number
- `YTD` (bit) - Year-to-date flag
- `LYTD` (bit) - Last year-to-date flag
- `Mes` (varchar, 18) - Month name
- `FechaID` (int) - Date identifier
- `YearMes` (varchar, 14) - Year-month combination
- `CALMONTH` (varchar, 12) - Calendar month identifier
- `MesCorto` (varchar, 6) - Short month abbreviation

**Business Purpose:**
- Time-based analysis and trending
- Seasonal pattern identification
- Year-over-year comparisons
- Period-based reporting and forecasting

---

## Table Relationships

### Primary Relationships

#### 1. Customer Dimension Relationships
- **cliente** ↔ **cliente_cedi** (One-to-Many)
  - Link: `cliente.customer_id` → `cliente_cedi.customer_id`
  - Purpose: Maps customers to their serving distribution centers

- **cliente** ↔ **segmentacion** (One-to-Many)
  - Link: `cliente.customer_id` → `segmentacion.customer_id`
  - Purpose: Links customer data to sales transactions

#### 2. Geographic Dimension Relationships
- **cliente_cedi** ↔ **mercado** (Many-to-One)
  - Link: `cliente_cedi.cedi_id` → `mercado.CEDIid`
  - Purpose: Provides market hierarchy for customer-CEDI assignments

#### 3. Product Dimension Relationships
- **producto** ↔ **segmentacion** (One-to-Many)
  - Link: `producto.Material` → `segmentacion.material_id`
  - Purpose: Links product master data to sales transactions

#### 4. Time Dimension Relationships
- **tiempo** ↔ **segmentacion** (One-to-Many)
  - Link: `tiempo.Fecha` → `segmentacion.calday`
  - Purpose: Provides time dimension for sales analysis

### Relationship Cardinalities
```
cliente (1) ────── (M) cliente_cedi (M) ────── (1) mercado
   │                                              │
   │ (1)                                          │
   │                                              │
   └────────────── (M) segmentacion (M) ─────────┘
                         │ (M)
                         │
                    (1)  │
                   tiempo │
                         │ (M)
                    producto
```

---

## Business Questions Analysis

The database schema is designed to support a comprehensive set of business analytics questions. Below is an analysis of how the schema addresses key business requirements:

### Sales Performance Analytics
1. **Best-selling products analysis** - Supported via `segmentacion` metrics joined with `producto` master data
2. **Returnable vs non-returnable comparison** - Enabled through `producto.Retornabilidad` field
3. **Channel and zone profitability** - Achieved through customer channel data and geographic hierarchy

### Customer Intelligence
4. **Key customer identification** - Via `cliente.Cuenta_clave` and sales volume analysis
5. **Customer segmentation** - Through multiple customer classification fields
6. **Purchase behavior analysis** - Enabled by transaction-level data in `segmentacion`

### Geographic and Territory Management
7. **CEDI performance comparison** - Supported via `mercado` and aggregated sales data
8. **Territory coverage analysis** - Through geographic hierarchy and customer assignments
9. **Route optimization** - Via customer-CEDI relationships and geographic data

### Product and Category Management
10. **Product adoption tracking** - Through time-series analysis of new product sales
11. **Category performance** - Via `producto.Categoria` and sales metrics
12. **Brand penetration analysis** - Enabled by `producto.AgrupadordeMarca` classification

### Time-based Analytics
13. **Seasonal trend analysis** - Supported by comprehensive time dimension
14. **Forecasting capabilities** - Through historical sales patterns by time periods
15. **Year-over-year comparisons** - Via `tiempo.YTD` and `tiempo.LYTD` flags

---

## Data Model Design Patterns

### Star Schema Implementation
The database follows a classic **star schema** pattern with:

- **Central Fact Table:** `segmentacion` (sales transactions)
- **Dimension Tables:** 
  - `cliente` (customer dimension)
  - `producto` (product dimension)
  - `tiempo` (time dimension)
  - `mercado` (geography dimension)
- **Bridge Table:** `cliente_cedi` (resolves many-to-many customer-CEDI relationships)

### Benefits of This Design:
1. **Query Performance:** Optimized for analytical queries with minimal joins
2. **Scalability:** Easy to add new dimensions or modify existing ones
3. **Business User Friendly:** Intuitive structure for business analysts
4. **Aggregation Efficiency:** Supports fast aggregations across any dimension combination

### Indexing Strategy
Based on the schema analysis, key indexes include:
- `cliente.Canal_Comercial` - For channel-based analysis
- `cliente_cedi.cedi_id` - For CEDI-based queries
- `tiempo.CALMONTH` - For monthly aggregations
- Primary keys on all tables for referential integrity

---

## Key Metrics and KPIs

### Sales Metrics
- **Volume Metrics:**
  - `VentasCajasUnidad` - Primary volume measure in case units
  - `VentasCajasOriginales` - Original case volume
  - `bottles_sold_m` - Volume in bottle units

- **Revenue Metrics:**
  - `IngresoNetoSImpuestos` - Net revenue excluding taxes
  - `net_revenue` - Total net revenue
  - Average selling price (calculated: revenue ÷ volume)

### Performance Indicators
- **Coverage:** `Cobertura` field in segmentacion table
- **Customer Penetration:** Active customers by territory/product
- **Market Share:** Brand performance by category and geography
- **Growth Rates:** Period-over-period comparisons using time dimension

### Operational Metrics
- **Territory Performance:** Sales and coverage by geographic hierarchy
- **Channel Effectiveness:** Performance by commercial channel
- **Product Mix:** Category and brand distribution analysis
- **Customer Retention:** Purchase frequency and recency analysis

---

## Technical Implementation Notes

### Data Types and Constraints
- Most string fields use `varchar` with appropriate lengths
- Numeric metrics use `float` for precision in calculations
- Date fields properly typed as `date` for time-based operations
- Primary keys enforce data integrity across relationships

### Performance Considerations
- Star schema design optimizes for read-heavy analytical workloads
- Dimension tables are relatively small for efficient joins
- Fact table partitioning by date recommended for large datasets
- Indexing strategy focuses on common query patterns

### Data Quality Features
- Primary key constraints ensure uniqueness
- Foreign key relationships maintain referential integrity
- Standardized naming conventions across tables
- Consistent geographic hierarchy structure

---

## Conclusion

This database schema provides a robust foundation for comprehensive sales analytics and business intelligence. The star schema design pattern, combined with rich dimensional attributes, enables sophisticated analysis across customer, product, geographic, and temporal dimensions. The structure directly supports the extensive list of business questions identified in the requirements, making it an effective platform for data-driven decision making in sales and distribution management.

---

*This documentation serves as a reference for data analysts, business users, and technical teams working with the Multi-Agent Custom Automation Engine Solution Accelerator database.*
