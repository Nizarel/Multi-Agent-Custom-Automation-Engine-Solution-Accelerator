# Table Record Counts

| Table | Number of Records | Description |
|-------|------------------|-------------|
| **dev.cliente** | 952,028 | Customer dimension |
| **dev.cliente_cedi** | 1,009,570 | Customer-CEDI bridge table |
| **dev.mercado** | 121 | Market/CEDI dimension |
| **dev.producto** | 1,435 | Product dimension |
| **dev.segmentacion** | 847,130,753 | Sales fact table (main transactional data) |
| **dev.tiempo** | 900 | Time dimension |

## **Key Insights:**

- **Largest Table:** `segmentacion` with over 847 million records - this is your main fact table containing all sales transactions
- **Customer Data:** Nearly 1 million customers with over 1 million customer-CEDI relationships
- **Product Catalog:** 1,435 different products/materials
- **Geographic Coverage:** 121 different CEDIs/markets
- **Time Range:** 900 time records (likely covering about 2.5 years of daily data)

The segmentation table being the largest is typical for a data warehouse - it contains the granular transactional sales data at the customer-product-date-channel level.
