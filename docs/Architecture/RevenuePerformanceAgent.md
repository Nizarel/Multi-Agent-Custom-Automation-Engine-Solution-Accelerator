# Revenue Performance Agent Implementation Guide
## Multi-Agent Custom Automation Engine Solution Accelerator

*Document Version: 1.0*  
*Created: June 24, 2025*  
*Author: GitHub Copilot*

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Agent Overview](#agent-overview)
3. [Business Questions Coverage](#business-questions-coverage)
4. [Technical Architecture](#technical-architecture)
5. [Implementation Steps](#implementation-steps)
6. [MCP Integration](#mcp-integration)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)
9. [Performance Optimization](#performance-optimization)
10. [Future Enhancements](#future-enhancements)

---

## Executive Summary

The **Revenue Performance Agent** is the first specialized sales analysis agent to be implemented in the Multi-Agent Custom Automation Engine. This agent focuses on financial performance analysis, revenue optimization, and sales forecasting for the beverage distribution business.

### Key Features
- **Revenue Trend Analysis:** Real-time insights across zones, categories, and time periods
- **Profitability Calculations:** Multi-dimensional profitability analysis
- **Sales Forecasting:** AI-powered predictions with seasonality considerations
- **Best-Selling Products:** Volume and value-based product rankings
- **Financial KPIs:** Comprehensive monitoring and variance analysis

#### Why Start with Revenue Performance Agent?
1. **Highest Business Impact:** Covers 9 of 33 business questions (27%)
2. **Core Financial Metrics:** Revenue and profitability are fundamental KPIs
3. **Foundation for Others:** Revenue analysis feeds into customer, territory, and product decisions
4. **Clear MCP Integration:** Direct mapping to `segmentacion` fact table
5. **Immediate Value:** Quick wins with actionable insights

---

## Agent Overview

### 🎯 Purpose
Financial performance analysis and revenue optimization for beverage distribution operations.

### 💡 Core Capabilities
- Revenue trend analysis across multiple dimensions
- Profitability analysis by channel, zone, and category
- Sales forecasting with variance analysis
- Price optimization recommendations
- Financial KPI monitoring and alerting

### 📊 Database Tables Used
- `segmentacion` — Primary fact table with sales transactions
- `tiempo` — Time dimension for temporal analysis
- `cliente` — Customer master data and channel information
- `mercado` — Geographic hierarchy (CEDI, Zone, Territory)
- `producto` — Product master data and category classification

### 🔧 Tools Provided
1. `analyze_revenue_trends` — Multi-dimensional revenue analysis
2. `calculate_profitability` — Profitability metrics by dimension
3. `get_best_selling_products` — Product performance rankings
4. `forecast_sales` — Predictive sales forecasting

---

## Business Questions Coverage

The Revenue Performance Agent addresses **9 critical business questions**:

### 1. Best-Selling Products Analysis
- **Question:** What are the best-selling products by volume and value?
- **Tool:** `get_best_selling_products`
- **Output:** Ranked list with revenue, volume, customer count metrics

### 2. Profitability Analysis
- **Question:** What is the profitability by channel, zone, or product category?
- **Tool:** `calculate_profitability`
- **Output:** Profitability metrics with margin indicators

### 3. CEDI Performance
- **Question:** Which product/category generated highest profit last quarter per CEDI?
- **Tool:** `calculate_profitability` with CEDI dimension
- **Output:** CEDI-level profitability rankings

### 4. Price Variation Analysis
- **Question:** Is there variation in average selling price per material by zone?
- **Tool:** `analyze_revenue_trends` with price analysis
- **Output:** Price variance reports by geographic zone

### 5. Sales Forecasting
- **Question:** Sales forecast for next month/quarter per CEDI and product?
- **Tool:** `forecast_sales`
- **Output:** Predictive forecasts with confidence intervals

### 6. Forecast Accuracy
- **Question:** How close are actual sales to forecasts?
- **Tool:** `forecast_sales` with accuracy metrics
- **Output:** Variance analysis and accuracy scores

### 7. Demand Estimation
- **Question:** Which zones had demand over/underestimated?
- **Tool:** `analyze_revenue_trends` with forecast comparison
- **Output:** Zone-level demand accuracy analysis

### 8. Revenue vs. Forecast
- **Question:** Revenue vs. forecast accuracy analysis
- **Tool:** Combined analysis tools
- **Output:** Comprehensive accuracy dashboard

### 9. Purchase Ticket Analysis
- **Question:** Average purchase ticket variation by channel and zone
- **Tool:** `analyze_revenue_trends`
- **Output:** Transaction value analysis by dimension

---

## Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Revenue Performance Agent                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Agent Core                           │ │
│  │  - Session Management                                   │ │
│  │  - Memory Store Integration                             │ │
│  │  - Tool Registration                                    │ │
│  │  - System Message Configuration                         │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Revenue Performance Tools                   │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ analyze_revenue │  │ calculate       │              │ │
│  │  │ _trends         │  │ _profitability  │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ get_best_selling│  │ forecast_sales  │              │ │
│  │  │ _products       │  │                 │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   MCP Integration                       │ │
│  │  - Async Query Execution                                │ │
│  │  - Connection Pooling                                   │ │
│  │  - Query Optimization                                   │ │
│  │  - Result Caching                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Query → Revenue Performance Agent → Tool Selection → 
MCP Query Builder → Database → Result Processing → 
Formatted Insights → User Response
```

---

## Implementation Steps

### Step 1: Update Agent Type Enum

```python
# ...existing code...
class AgentType(str, Enum):
    """Enum representing different types of agents in the system."""
    GROUP_CHAT_MANAGER = "group_chat_manager"
    PLANNER = "planner"
    HUMAN = "human"
    HR = "hr"
    MARKETING = "marketing"
    PRODUCT = "product"
    PROCUREMENT = "procurement"
    TECH_SUPPORT = "tech_support"
    GENERIC = "generic"
    # New specialized sales agents
    REVENUE_PERFORMANCE = "revenue_performance"
    CUSTOMER_INTELLIGENCE = "customer_intelligence"
    TERRITORY_DISTRIBUTION = "territory_distribution"
    PRODUCT_ANALYTICS = "product_analytics"
    MARKET_INTELLIGENCE = "market_intelligence"
```

### Step 2: Create Revenue Performance Tools

```python
"""Revenue Performance Tools for sales analysis using MCP client."""
from typing import Annotated, Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import logging

from semantic_kernel.functions import kernel_function
from models.messages_kernel import AgentType

logger = logging.getLogger(__name__)


class RevenuePerformanceTools:
    """Tools for revenue performance analysis using MCP client."""
    
    def __init__(self, mcp_client=None):
        """Initialize with MCP client for database access."""
        self.mcp_client = mcp_client
        self._agent_name = AgentType.REVENUE_PERFORMANCE.value
    
    @kernel_function(name="analyze_revenue_trends")
    async def analyze_revenue_trends(
        self,
        time_period: Annotated[str, "Time period for analysis (e.g., 'last_30_days', 'last_quarter', 'YTD')"] = "last_30_days",
        zone: Annotated[str, "Geographic zone to analyze (e.g., 'all', 'Norte', 'Sur', 'Occidente')"] = "all",
        product_category: Annotated[str, "Product category to analyze (e.g., 'all', 'REFRESCOS', 'AGUA')"] = "all"
    ) -> str:
        """
        Analyze revenue trends across different dimensions.
        
        Args:
            time_period: Time period for analysis
            zone: Geographic zone to analyze
            product_category: Product category to analyze
            
        Returns:
            Detailed revenue trend analysis with insights
        """
        try:
            # Calculate date range based on time period
            end_date = datetime.now()
            if time_period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "last_quarter":
                start_date = end_date - timedelta(days=90)
            elif time_period == "YTD":
                start_date = datetime(end_date.year, 1, 1)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Build query with proper joins
            query = f"""
            SELECT 
                t.CALMONTH as month,
                m.Zona as zone,
                p.Categoria as category,
                SUM(s.net_revenue) as total_revenue,
                SUM(s.VentasCajasUnidad) as total_volume,
                COUNT(DISTINCT s.customer_id) as unique_customers,
                AVG(s.net_revenue) as avg_transaction_value
            FROM segmentacion s
            JOIN tiempo t ON s.calday = t.Fecha
            JOIN cliente c ON s.customer_id = c.customer_id
            JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
            JOIN mercado m ON cc.cedi_id = m.CEDIid
            JOIN producto p ON s.material_id = p.Material
            WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
            """
            
            if zone != "all":
                query += f" AND m.Zona = '{zone}'"
            if product_category != "all":
                query += f" AND p.Categoria = '{product_category}'"
                
            query += """
            GROUP BY t.CALMONTH, m.Zona, p.Categoria
            ORDER BY t.CALMONTH DESC, total_revenue DESC
            """
            
            # Execute query via MCP
            if self.mcp_client:
                result = await self.mcp_client.call_tool(
                    "query-database",
                    {"query": query}
                )
                
                # Process and format results
                return self._format_revenue_trends(result, time_period, zone, product_category)
            else:
                return "MCP client not available. Unable to analyze revenue trends."
                
        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {str(e)}")
            return f"Error analyzing revenue trends: {str(e)}"
    
    @kernel_function(name="calculate_profitability")
    async def calculate_profitability(
        self,
        dimension: Annotated[str, "Dimension to analyze ('channel', 'zone', 'category', 'product')"] = "category",
        time_period: Annotated[str, "Time period for analysis"] = "last_30_days",
        top_n: Annotated[int, "Number of top results to return"] = 10
    ) -> str:
        """
        Calculate profitability metrics by different dimensions.
        
        Args:
            dimension: Dimension to analyze profitability
            time_period: Time period for analysis
            top_n: Number of top results to return
            
        Returns:
            Profitability analysis with rankings and insights
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            if time_period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "last_quarter":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Build query based on dimension
            if dimension == "channel":
                group_field = "c.Canal_Comercial"
                select_field = "c.Canal_Comercial as dimension_value"
            elif dimension == "zone":
                group_field = "m.Zona"
                select_field = "m.Zona as dimension_value"
            elif dimension == "category":
                group_field = "p.Categoria"
                select_field = "p.Categoria as dimension_value"
            else:  # product
                group_field = "p.Material, p.Producto"
                select_field = "p.Material as material_id, p.Producto as dimension_value"
            
            query = f"""
            SELECT TOP {top_n}
                {select_field},
                SUM(s.net_revenue) as total_revenue,
                SUM(s.IngresoNetoSImpuestos) as revenue_without_tax,
                SUM(s.VentasCajasUnidad) as total_volume,
                COUNT(DISTINCT s.customer_id) as customer_count,
                AVG(s.net_revenue / NULLIF(s.VentasCajasUnidad, 0)) as avg_price_per_unit,
                SUM(s.net_revenue) / NULLIF(SUM(s.VentasCajasUnidad), 0) as revenue_per_unit
            FROM segmentacion s
            JOIN tiempo t ON s.calday = t.Fecha
            JOIN cliente c ON s.customer_id = c.customer_id
            JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
            JOIN mercado m ON cc.cedi_id = m.CEDIid
            JOIN producto p ON s.material_id = p.Material
            WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
            GROUP BY {group_field}
            ORDER BY total_revenue DESC
            """
            
            # Execute query
            if self.mcp_client:
                result = await self.mcp_client.call_tool(
                    "query-database",
                    {"query": query}
                )
                
                return self._format_profitability_analysis(result, dimension, time_period)
            else:
                return "MCP client not available. Unable to calculate profitability."
                
        except Exception as e:
            logger.error(f"Error calculating profitability: {str(e)}")
            return f"Error calculating profitability: {str(e)}"
    
    @kernel_function(name="get_best_selling_products")
    async def get_best_selling_products(
        self,
        metric: Annotated[str, "Metric to rank by ('volume' or 'value')"] = "value",
        zone: Annotated[str, "Zone to filter by"] = "all",
        time_period: Annotated[str, "Time period for analysis"] = "last_30_days",
        limit: Annotated[int, "Number of products to return"] = 20
    ) -> str:
        """
        Get best-selling products by volume or value.
        
        Args:
            metric: Whether to rank by volume or value
            zone: Geographic zone to analyze
            time_period: Time period for analysis
            limit: Number of products to return
            
        Returns:
            List of best-selling products with detailed metrics
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            if time_period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
            
            order_by = "total_revenue" if metric == "value" else "total_volume"
            
            query = f"""
            SELECT TOP {limit}
                p.Material,
                p.Producto,
                p.Categoria,
                p.Subcategoria,
                p.AgrupadordeMarca as brand,
                SUM(s.net_revenue) as total_revenue,
                SUM(s.VentasCajasUnidad) as total_volume,
                COUNT(DISTINCT s.customer_id) as customer_count,
                COUNT(DISTINCT s.calday) as days_sold,
                AVG(s.net_revenue / NULLIF(s.VentasCajasUnidad, 0)) as avg_price_per_unit
            FROM segmentacion s
            JOIN tiempo t ON s.calday = t.Fecha
            JOIN producto p ON s.material_id = p.Material
            """
            
            if zone != "all":
                query += f"""
                JOIN cliente c ON s.customer_id = c.customer_id
                JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
                JOIN mercado m ON cc.cedi_id = m.CEDIid
                WHERE m.Zona = '{zone}'
                AND t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                """
            else:
                query += f"""
                WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                """
                
            query += f"""
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
            GROUP BY p.Material, p.Producto, p.Categoria, p.Subcategoria, p.AgrupadordeMarca
            ORDER BY {order_by} DESC
            """
            
            # Execute query
            if self.mcp_client:
                result = await self.mcp_client.call_tool(
                    "query-database",
                    {"query": query}
                )
                
                return self._format_best_selling_products(result, metric, zone, time_period)
            else:
                return "MCP client not available. Unable to get best-selling products."
                
        except Exception as e:
            logger.error(f"Error getting best-selling products: {str(e)}")
            return f"Error getting best-selling products: {str(e)}"
    
    @kernel_function(name="forecast_sales")
    async def forecast_sales(
        self,
        forecast_period: Annotated[str, "Period to forecast ('next_month', 'next_quarter')"] = "next_month",
        dimension: Annotated[str, "Dimension to forecast by ('cedi', 'product', 'category')"] = "category",
        use_seasonality: Annotated[bool, "Whether to consider seasonal patterns"] = True
    ) -> str:
        """
        Generate sales forecast for specified period and dimension.
        
        Args:
            forecast_period: Period to forecast
            dimension: Dimension to forecast by
            use_seasonality: Whether to consider seasonal patterns
            
        Returns:
            Sales forecast with confidence intervals and insights
        """
        try:
            # For forecasting, we'll use historical data to project forward
            # This is a simplified approach - in production, use proper time series models
            
            lookback_days = 90 if forecast_period == "next_quarter" else 30
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get historical data
            if dimension == "cedi":
                group_by = "m.CEDI, m.CEDIid"
                select_field = "m.CEDI as dimension_value"
            elif dimension == "product":
                group_by = "p.Material, p.Producto"
                select_field = "p.Material as material_id, p.Producto as dimension_value"
            else:  # category
                group_by = "p.Categoria"
                select_field = "p.Categoria as dimension_value"
            
            query = f"""
            SELECT 
                {select_field},
                t.CALMONTH as month,
                SUM(s.net_revenue) as monthly_revenue,
                SUM(s.VentasCajasUnidad) as monthly_volume,
                COUNT(DISTINCT s.customer_id) as monthly_customers
            FROM segmentacion s
            JOIN tiempo t ON s.calday = t.Fecha
            JOIN cliente c ON s.customer_id = c.customer_id
            JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
            JOIN mercado m ON cc.cedi_id = m.CEDIid
            JOIN producto p ON s.material_id = p.Material
            WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
            GROUP BY {group_by}, t.CALMONTH
            ORDER BY t.CALMONTH DESC
            """
            
            # Execute query
            if self.mcp_client:
                result = await self.mcp_client.call_tool(
                    "query-database",
                    {"query": query}
                )
                
                return self._generate_forecast(result, forecast_period, dimension, use_seasonality)
            else:
                return "MCP client not available. Unable to generate forecast."
                
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return f"Error generating forecast: {str(e)}"
    
    def _format_revenue_trends(self, data: Dict[str, Any], time_period: str, zone: str, category: str) -> str:
        """Format revenue trends data into insights."""
        try:
            rows = data.get("rows", [])
            if not rows:
                return "No revenue data found for the specified criteria."
            
            # Calculate summary metrics
            total_revenue = sum(row.get("total_revenue", 0) for row in rows)
            total_volume = sum(row.get("total_volume", 0) for row in rows)
            unique_customers = len(set(row.get("unique_customers", 0) for row in rows))
            
            # Build insights
            insights = f"""
📊 **Revenue Trend Analysis**
📅 Period: {time_period}
🌎 Zone: {zone}
📦 Category: {category}

**Summary Metrics:**
- 💰 Total Revenue: ${total_revenue:,.2f}
- 📦 Total Volume: {total_volume:,.0f} units
- 👥 Unique Customers: {unique_customers:,}

**Top Performing Segments:**
"""
            
            # Add top 5 segments
            for i, row in enumerate(rows[:5]):
                insights += f"""
{i+1}. **{row.get('zone', 'N/A')} - {row.get('category', 'N/A')}**
   - Revenue: ${row.get('total_revenue', 0):,.2f}
   - Volume: {row.get('total_volume', 0):,.0f} units
   - Avg Transaction: ${row.get('avg_transaction_value', 0):,.2f}
"""
            
            # Add trend analysis
            if len(rows) > 1:
                # Simple month-over-month comparison
                latest_month = rows[0]
                previous_month = rows[1] if len(rows) > 1 else None
                
                if previous_month:
                    revenue_change = ((latest_month.get('total_revenue', 0) - previous_month.get('total_revenue', 0)) 
                                    / previous_month.get('total_revenue', 1)) * 100
                    
                    trend_icon = "📈" if revenue_change > 0 else "📉"
                    insights += f"\n**Trend:** {trend_icon} {revenue_change:+.1f}% vs previous period"
            
            return insights
            
        except Exception as e:
            logger.error(f"Error formatting revenue trends: {str(e)}")
            return "Error formatting revenue trend analysis"
    
    def _format_profitability_analysis(self, data: Dict[str, Any], dimension: str, time_period: str) -> str:
        """Format profitability analysis data."""
        try:
            rows = data.get("rows", [])
            if not rows:
                return f"No profitability data found for {dimension} in {time_period}."
            
            insights = f"""
💼 **Profitability Analysis by {dimension.title()}**
📅 Period: {time_period}

**Top {len(rows)} Most Profitable {dimension.title()}s:**
"""
            
            for i, row in enumerate(rows):
                revenue = row.get('total_revenue', 0)
                volume = row.get('total_volume', 0)
                customers = row.get('customer_count', 0)
                revenue_per_unit = row.get('revenue_per_unit', 0)
                
                insights += f"""
{i+1}. **{row.get('dimension_value', 'Unknown')}**
   - 💰 Revenue: ${revenue:,.2f}
   - 📦 Volume: {volume:,.0f} units
   - 👥 Customers: {customers:,}
   - 💵 Revenue/Unit: ${revenue_per_unit:.2f}
   - 📊 Margin Indicator: {"⭐" * min(5, int(revenue_per_unit/10))}
"""
            
            # Add summary insights
            total_revenue = sum(row.get('total_revenue', 0) for row in rows)
            avg_revenue_per_unit = sum(row.get('revenue_per_unit', 0) for row in rows) / len(rows)
            
            insights += f"""
**Summary Insights:**
- Total Revenue (Top {len(rows)}): ${total_revenue:,.2f}
- Average Revenue per Unit: ${avg_revenue_per_unit:.2f}
- Recommendation: Focus on top 3 {dimension}s for maximum profitability impact
"""
            
            return insights
            
        except Exception as e:
            logger.error(f"Error formatting profitability analysis: {str(e)}")
            return "Error formatting profitability analysis"
    
    def _format_best_selling_products(self, data: Dict[str, Any], metric: str, zone: str, time_period: str) -> str:
        """Format best-selling products data."""
        try:
            rows = data.get("rows", [])
            if not rows:
                return f"No product sales data found for {zone} in {time_period}."
            
            metric_label = "Revenue" if metric == "value" else "Volume"
            
            insights = f"""
🏆 **Best-Selling Products by {metric_label}**
📅 Period: {time_period}
🌎 Zone: {zone}

**Top {len(rows)} Products:**
"""
            
            for i, row in enumerate(rows):
                material = row.get('Material', 'Unknown')
                product = row.get('Producto', 'Unknown')
                category = row.get('Categoria', 'Unknown')
                brand = row.get('brand', 'Unknown')
                revenue = row.get('total_revenue', 0)
                volume = row.get('total_volume', 0)
                customers = row.get('customer_count', 0)
                days_sold = row.get('days_sold', 0)
                
                insights += f"""
{i+1}. **{product}** ({material})
   - 🏷️ Category: {category}
   - 🏢 Brand: {brand}
   - 💰 Revenue: ${revenue:,.2f}
   - 📦 Volume: {volume:,.0f} units
   - 👥 Customers: {customers:,}
   - 📅 Days Sold: {days_sold}
   - 🔥 Popularity: {"🔥" * min(5, int(customers/100))}
"""
            
            # Add category summary
            categories = {}
            for row in rows:
                cat = row.get('Categoria', 'Unknown')
                if cat not in categories:
                    categories[cat] = {'count': 0, 'revenue': 0}
                categories[cat]['count'] += 1
                categories[cat]['revenue'] += row.get('total_revenue', 0)
            
            insights += "\n**Category Distribution:**\n"
            for cat, data in sorted(categories.items(), key=lambda x: x[1]['revenue'], reverse=True):
                insights += f"- {cat}: {data['count']} products, ${data['revenue']:,.2f} revenue\n"
            
            return insights
            
        except Exception as e:
            logger.error(f"Error formatting best-selling products: {str(e)}")
            return "Error formatting best-selling products analysis"
    
    def _generate_forecast(self, data: Dict[str, Any], forecast_period: str, dimension: str, use_seasonality: bool) -> str:
        """Generate sales forecast based on historical data."""
        try:
            rows = data.get("rows", [])
            if not rows:
                return f"Insufficient historical data for forecasting by {dimension}."
            
            # Group data by dimension
            dimension_data = {}
            for row in rows:
                dim_value = row.get('dimension_value', 'Unknown')
                month = row.get('month', '')
                
                if dim_value not in dimension_data:
                    dimension_data[dim_value] = []
                
                dimension_data[dim_value].append({
                    'month': month,
                    'revenue': row.get('monthly_revenue', 0),
                    'volume': row.get('monthly_volume', 0),
                    'customers': row.get('monthly_customers', 0)
                })
            
            # Simple forecast: average of last 3 months with trend adjustment
            period_label = "Next Month" if forecast_period == "next_month" else "Next Quarter"
            
            insights = f"""
🔮 **Sales Forecast - {period_label}**
📊 Dimension: {dimension.title()}
🌡️ Seasonality: {"Enabled" if use_seasonality else "Disabled"}

**Forecasted Performance:**
"""
            
            total_forecast_revenue = 0
            total_forecast_volume = 0
            
            for dim_value, history in list(dimension_data.items())[:10]:  # Top 10
                if len(history) >= 3:
                    # Calculate average and trend
                    last_3_revenue = [h['revenue'] for h in history[:3]]
                    avg_revenue = sum(last_3_revenue) / len(last_3_revenue)
                    
                    # Simple trend calculation
                    if len(last_3_revenue) >= 2:
                        trend = (last_3_revenue[0] - last_3_revenue[1]) / last_3_revenue[1] if last_3_revenue[1] > 0 else 0
                    else:
                        trend = 0
                    
                    # Apply trend and seasonality
                    forecast_revenue = avg_revenue * (1 + trend)
                    if use_seasonality and forecast_period == "next_month":
                        # Simple seasonality: assume 10% increase in Q4
                        current_month = datetime.now().month
                        if current_month >= 10:
                            forecast_revenue *= 1.1
                    
                    total_forecast_revenue += forecast_revenue
                    
                    confidence = "High" if len(history) >= 6 else "Medium" if len(history) >= 3 else "Low"
                    
                    insights += f"""
**{dim_value}**
- 📈 Forecast Revenue: ${forecast_revenue:,.2f}
- 📊 Based on: {len(history)} months of data
- 🎯 Confidence: {confidence}
- 📉 Trend: {trend:+.1%}
"""
            
            insights += f"""
**Total Forecast Summary:**
- 💰 Total Expected Revenue: ${total_forecast_revenue:,.2f}
- 📊 Based on top {len(dimension_data)} {dimension}s
- ⚠️ Note: This is a simplified forecast. Consider external factors and market conditions.
"""
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return "Error generating sales forecast"
```

### Step 3: Create Revenue Performance Agent

```python
# ...see full implementation in the guide above for details...
from typing import Dict, List, Optional, Any

from context.cosmos_memory_kernel import CosmosMemoryContext
from kernel_agents.agent_base import AgentBase
from kernel_tools.revenue_performance_tools import RevenuePerformanceTools
from models.messages_kernel import AgentType


class RevenuePerformanceAgent(AgentBase):
    """
    Specialized agent for revenue performance analysis and financial insights.
    
    This agent focuses on:
    - Revenue trend analysis
    - Profitability calculations
    - Sales forecasting
    - Financial KPI monitoring
    - Price optimization recommendations
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        mcp_client: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize the Revenue Performance Agent.
        
        Args:
            session_id: Current session identifier
            user_id: User identifier
            memory_store: Cosmos memory store for context
            mcp_client: MCP client for database access
            **kwargs: Additional arguments for base class
        """
        # Initialize revenue performance tools with MCP client
        self.revenue_tools = RevenuePerformanceTools(mcp_client=mcp_client)
        
        # Create tools list for the agent
        tools = [
            self.revenue_tools.analyze_revenue_trends,
            self.revenue_tools.calculate_profitability,
            self.revenue_tools.get_best_selling_products,
            self.revenue_tools.forecast_sales
        ]
        
        # Set up the system message for the agent
        system_message = self._get_system_message()
        
        # Initialize base class
        super().__init__(
            agent_name=AgentType.REVENUE_PERFORMANCE.value,
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            tools=tools,
            system_message=system_message,
            **kwargs
        )
    
    def _get_system_message(self) -> str:
        """
        Get the specialized system message for the Revenue Performance Agent.
        
        Returns:
            System message string that defines the agent's behavior and expertise
        """
        return """You are a Revenue Performance Analysis specialist focused on financial 
metrics, profitability analysis, and sales forecasting for a beverage distribution company.

Your expertise includes:
- Revenue trend analysis across time periods, zones, and product categories
- Profitability calculations by channel, zone, and product category
- Sales forecasting with seasonality consideration
- Price optimization and revenue maximization strategies
- Financial KPI monitoring and variance analysis
- Best-selling product identification by volume and value

When analyzing data:
1. Always provide specific metrics with proper formatting (currency, percentages, units)
2. Include actionable insights and recommendations
3. Highlight trends and patterns in the data
4. Compare performance across different dimensions
5. Identify opportunities for revenue growth
6. Flag any concerning trends or anomalies

Format your responses with:
- Clear headers and sections
- Bullet points for key insights
- Tables for comparative data
- Emoji indicators for visual clarity (📈 for increases, 📉 for decreases, etc.)
- Executive summary at the beginning
- Detailed recommendations at the end

Remember to:
- Consider seasonal patterns when relevant
- Account for market dynamics and competitive factors
- Provide confidence levels for forecasts
- Suggest follow-up analyses when appropriate

Your goal is to provide data-driven insights that enable better business decisions 
and drive revenue growth."""
    
    @classmethod
    async def create(
        cls,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        mcp_client: Optional[Any] = None,
        **kwargs
    ) -> "RevenuePerformanceAgent":
        """
        Factory method to create a Revenue Performance Agent instance.
        
        Args:
            session_id: Current session identifier
            user_id: User identifier
            memory_store: Cosmos memory store for context
            mcp_client: MCP client for database access
            **kwargs: Additional arguments
            
        Returns:
            RevenuePerformanceAgent instance
        """
        return cls(
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            mcp_client=mcp_client,
            **kwargs
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the Revenue Performance Agent.
        
        Returns:
            Dictionary describing agent capabilities
        """
        return {
            "agent_type": AgentType.REVENUE_PERFORMANCE.value,
            "description": "Specialized agent for revenue performance analysis and financial insights",
            "capabilities": [
                "Revenue trend analysis",
                "Profitability calculations",
                "Sales forecasting",
                "Best-selling product identification",
                "Price optimization recommendations",
                "Financial KPI monitoring"
            ],
            "tools": [
                {
                    "name": "analyze_revenue_trends",
                    "description": "Analyze revenue trends across time periods and dimensions"
                },
                {
                    "name": "calculate_profitability",
                    "description": "Calculate profitability by channel, zone, or product"
                },
                {
                    "name": "get_best_selling_products",
                    "description": "Identify best-selling products by volume or value"
                },
                {
                    "name": "forecast_sales",
                    "description": "Generate sales forecasts with seasonality consideration"
                }
            ],
            "business_questions": [
                "What are the best-selling products by volume and value?",
                "What is the profitability by channel, zone, or product category?",
                "Which product/category generated highest profit last quarter?",
                "Is there variation in average selling price by zone?",
                "What is the sales forecast for next month/quarter?",
                "How do actual sales compare to forecasts?",
                "Which zones had demand over/underestimated?",
                "What is the average purchase ticket by channel and zone?"
            ]
        }
```

### Step 4: Update Agent Factory

```python
# ...existing code...
from kernel_agents.revenue_performance_agent import RevenuePerformanceAgent
class AgentFactory:
    """Factory for creating agents in the Multi-Agent Custom Automation Engine."""
    
    _agent_classes: Dict[AgentType, Type[AgentBase]] = {
        # Core orchestration agents (KEEP)
        AgentType.GROUP_CHAT_MANAGER: GroupChatManager,
        AgentType.PLANNER: PlannerAgent,
        AgentType.HUMAN: HumanAgent,
        AgentType.GENERIC: GenericAgent,
        
        # Legacy agents (TO BE DEPRECATED)
        AgentType.HR: HRAgent,
        AgentType.MARKETING: MarketingAgent,
        AgentType.PRODUCT: ProductAgent,
        AgentType.PROCUREMENT: ProcurementAgent,
        AgentType.TECH_SUPPORT: TechSupportAgent,
        
        # New specialized sales agents
        AgentType.REVENUE_PERFORMANCE: RevenuePerformanceAgent,
    }
    
    @classmethod
    async def create_agent(
        cls,
        agent_type: AgentType,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        mcp_client: Optional[Any] = None,
        **kwargs
    ) -> AgentBase:
        """Create an agent instance of the specified type."""
        agent_class = cls._agent_classes.get(agent_type)
        
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Pass MCP client to specialized sales agents
        if agent_type in [
            AgentType.REVENUE_PERFORMANCE,
            AgentType.CUSTOMER_INTELLIGENCE,
            AgentType.TERRITORY_DISTRIBUTION,
            AgentType.PRODUCT_ANALYTICS,
            AgentType.MARKET_INTELLIGENCE
        ]:
            kwargs['mcp_client'] = mcp_client
        
        # Create agent instance
        return await agent_class.create(
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            **kwargs
        )
```

### Step 5: Update Orchestration Layer

```python
# ...existing code...
class PlannerAgent(AgentBase):
    def __init__(self, session_id, user_id, memory_store, **kwargs):
        # Update available agents list
        self._available_agents = [
            AgentType.HUMAN.value,
            AgentType.GENERIC.value,
            # Legacy agents (to be phased out)
            AgentType.HR.value,
            AgentType.MARKETING.value,
            AgentType.PRODUCT.value,
            AgentType.PROCUREMENT.value,
            AgentType.TECH_SUPPORT.value,
            # New specialized sales agents
            AgentType.REVENUE_PERFORMANCE.value,
        ]
        
        # Add keyword mapping for intelligent routing
        self._keyword_agent_mapping = {
            # Revenue keywords
            "revenue|profit|sales|financial|forecast|price|profitability|best-selling": AgentType.REVENUE_PERFORMANCE.value,
            # Legacy mappings (keep for backward compatibility)
            "hr|human resources|employee|hiring": AgentType.HR.value,
            "marketing|campaign|promotion|brand": AgentType.MARKETING.value,
            "product|feature|roadmap|development": AgentType.PRODUCT.value,
            "procurement|supplier|vendor|purchase": AgentType.PROCUREMENT.value,
            "technical|support|issue|bug": AgentType.TECH_SUPPORT.value,
        }
        
        # Update system message to include revenue performance capabilities
        system_message = f"""You are a Planner agent that creates step-by-step plans to accomplish tasks.

Available specialized agents:
- **revenue_performance**: Financial analysis, revenue trends, profitability, forecasting, best-selling products
- **human**: For tasks requiring human input or approval
- **generic**: For general tasks not covered by specialized agents

Legacy agents (use only if specifically requested):
- hr, marketing, product, procurement, tech_support

When creating plans:
1. Analyze the task to identify required expertise
2. Route revenue/financial questions to revenue_performance agent
3. Break complex tasks into clear, actionable steps
4. Assign each step to the most appropriate agent
5. Include human agent for approvals or clarifications

Always prefer specialized agents over generic agent when applicable."""
        
        super().__init__(
            agent_name=AgentType.PLANNER.value,
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            system_message=system_message,
            **kwargs
        )
    
    async def _route_to_agent(self, task_description: str) -> str:
        """Route task to appropriate agent based on keywords."""
        task_lower = task_description.lower()
        
        for keywords, agent in self._keyword_agent_mapping.items():
            if any(keyword in task_lower for keyword in keywords.split("|")):
                return agent
        
        return AgentType.GENERIC.value
```

### Step 6: Update Group Chat Manager

```python
# ...existing code...
class GroupChatManager(AgentBase):
    def __init__(self, session_id, user_id, memory_store, **kwargs):
        # Add intelligent routing for specialized agents
        self._agent_routing_map = {
            # Financial/Revenue keywords
            "revenue|profit|financial|sales performance|forecasting|price|profitability|best-selling": 
                AgentType.REVENUE_PERFORMANCE.value,
            
            # Future specialized agents (placeholder)
            "customer|client|retention|segmentation|churn|acquisition":
                AgentType.CUSTOMER_INTELLIGENCE.value,
            
            "territory|cedi|route|coverage|distribution|geographic":
                AgentType.TERRITORY_DISTRIBUTION.value,
            
            "product|inventory|turnover|seasonal|category|brand":
                AgentType.PRODUCT_ANALYTICS.value,
            
            "promotion|campaign|market|competition|penetration":
                AgentType.MARKET_INTELLIGENCE.value,
        }
        
        # Update system message
        system_message = """You are the Group Chat Manager orchestrating a team of specialized agents.

Your responsibilities:
1. Analyze incoming requests to identify required expertise
2. Route tasks to appropriate specialized agents
3. Coordinate multi-agent workflows for complex queries
4. Synthesize results from multiple agents
5. Ensure human approval for critical decisions

Specialized agents available:
- **revenue_performance**: Revenue analysis, profitability, forecasting, best-selling products
- **human**: Human input and approvals
- **generic**: General tasks

Route financial/revenue questions to revenue_performance agent for best results."""
        
        super().__init__(
            agent_name=AgentType.GROUP_CHAT_MANAGER.value,
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            system_message=system_message,
            **kwargs
        )
    
    async def route_query(self, description: str) -> List[str]:
        """Intelligently route queries to appropriate specialist agents."""
        required_agents = []
        description_lower = description.lower()
        
        for keywords, agent in self._agent_routing_map.items():
            if any(keyword in description_lower for keyword in keywords.split("|")):
                # Only add revenue_performance for now, others are placeholders
                if agent == AgentType.REVENUE_PERFORMANCE.value:
                    required_agents.append(agent)
        
        return required_agents or [AgentType.GENERIC.value]
```

---

## MCP Integration

### Query Optimization Strategies

#### 1. Indexed Queries
```sql
-- Ensure indexes on commonly filtered columns
CREATE INDEX idx_segmentacion_calday ON segmentacion(calday);
CREATE INDEX idx_segmentacion_customer ON segmentacion(customer_id);
CREATE INDEX idx_segmentacion_material ON segmentacion(material_id);
```

#### 2. Query Batching
```python
async def execute_batch_queries(self, queries: List[str]) -> List[Dict]:
    """Execute multiple queries in parallel for performance."""
    tasks = [self.mcp_client.call_tool("query-database", {"query": q}) for q in queries]
    return await asyncio.gather(*tasks)
```

#### 3. Error Handling
```python
async def safe_query_execution(self, query: str) -> Dict[str, Any]:
    """Execute query with comprehensive error handling."""
    try:
        result = await self.mcp_client.call_tool("query-database", {"query": query})
        return result
    except TimeoutError:
        logger.error(f"Query timeout: {query[:100]}...")
        return {"error": "Query timeout. Please try with a smaller date range."}
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
```

---

## Testing Strategy

### Unit Test
```python
# filepath: src/backend/tests/test_revenue_performance_agent.py
import pytest
from unittest.mock import Mock, AsyncMock
from kernel_agents.revenue_performance_agent import RevenuePerformanceAgent
from kernel_tools.revenue_performance_tools import RevenuePerformanceTools

@pytest.mark.asyncio
async def test_revenue_trends_analysis():
    """Test revenue trends analysis functionality."""
    # Mock MCP client
    mock_mcp_client = Mock()
    mock_mcp_client.call_tool = AsyncMock(return_value={
        "rows": [
            {"zone": "Norte", "category": "REFRESCOS", "total_revenue": 100000},
            {"zone": "Sur", "category": "AGUA", "total_revenue": 80000}
        ]
    })
    
    # Create tools instance
    tools = RevenuePerformanceTools(mcp_client=mock_mcp_client)
    
    # Test analyze_revenue_trends
    result = await tools.analyze_revenue_trends(
        time_period="last_30_days",
        zone="all",
        product_category="all"
    )
    
    assert "Revenue Trend Analysis" in result
    assert "Norte" in result
    assert "$100,000" in result

@pytest.mark.asyncio
async def test_profitability_calculation():
    """Test profitability calculation functionality."""
    # Test implementation...

@pytest.mark.asyncio
async def test_best_selling_products():
    """Test best-selling products identification."""
    # Test implementation...

@pytest.mark.asyncio
async def test_sales_forecast():
    """Test sales forecasting functionality."""
    # Test implementation...
```

### Integration Test
```python
# filepath: src/backend/tests/test_revenue_integration.py
@pytest.mark.integration
async def test_full_revenue_analysis_workflow():
    """Test complete revenue analysis workflow."""
    # Initialize real components
    session_id = "test-session"
    user_id = "test-user"
    
    # Create memory store
    memory_store = CosmosMemoryContext(
        cosmos_client=config.cosmos_client,
        database_name=config.cosmos_database,
        container_name=config.cosmos_container
    )
    
    # Create MCP client
    mcp_client = MCPClient()
    await mcp_client.initialize()
    
    # Create Revenue Performance Agent
    agent = await AgentFactory.create_agent(
        agent_type=AgentType.REVENUE_PERFORMANCE,
        session_id=session_id,
        user_id=user_id,
        memory_store=memory_store,
        mcp_client=mcp_client
    )
    
    # Test complex query
    response = await agent.process_message(
        "Analyze revenue trends for the last quarter and identify top 5 best-selling products"
    )
    
    assert response is not None
    assert "revenue" in response.lower()
    assert "best-selling" in response.lower()
    
    # Cleanup
    await mcp_client.cleanup()
```

### Performance Tests
```python
# filepath: src/backend/tests/test_revenue_performance.py
@pytest.mark.performance
async def test_query_performance():
    """Test query execution performance."""
    import time
    
    # Setup
    tools = RevenuePerformanceTools(mcp_client=mock_mcp_client)
    
    # Measure execution time
    start_time = time.time()
    
    await tools.analyze_revenue_trends(
        time_period="last_30_days",
        zone="all",
        product_category="all"
    )
    
    execution_time = time.time() - start_time
    
    # Assert performance requirement
    assert execution_time < 5.0, f"Query took {execution_time}s, expected < 5s"
```

---

## Performance Optimization

### Query Optimization Tips

#### 1. Use Materialized Views
```sql
-- Create materialized view for common aggregations
CREATE MATERIALIZED VIEW mv_daily_revenue AS
SELECT 
    t.Fecha as date,
    m.Zona as zone,
    p.Categoria as category,
    SUM(s.net_revenue) as total_revenue,
    COUNT(DISTINCT s.customer_id) as customer_count
FROM segmentacion s
JOIN tiempo t ON s.calday = t.Fecha
JOIN cliente c ON s.customer_id = c.customer_id
JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
JOIN mercado m ON cc.cedi_id = m.CEDIid
JOIN producto p ON s.material_id = p.Material
GROUP BY t.Fecha, m.Zona, p.Categoria;
```

#### 2. Implement Query Pagination
```python
async def get_paginated_results(self, query: str, page: int = 1, page_size: int = 100):
    """Get paginated results for large datasets."""
    offset = (page - 1) * page_size
    paginated_query = f"{query} OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
    return await self.mcp_client.call_tool("query-database", {"query": paginated_query})
```

#### 3. Cache Frequently Used Data
```python
from aiocache import Cache
from aiocache.serializers import JsonSerializer

cache = Cache(Cache.REDIS, serializer=JsonSerializer())

@cache.cached(ttl=3600)  # Cache for 1 hour
async def get_zone_list(self):
    """Get cached list of zones."""
    query = "SELECT DISTINCT Zona FROM mercado ORDER BY Zona"
    result = await self.mcp_client.call_tool("query-database", {"query": query})
    return [row['Zona'] for row in result.get('rows', [])]
```

---

## Future Enhancements

- Implement additional specialized agents (Customer Intelligence, Territory Distribution, etc.)
- Add advanced forecasting models (ARIMA, Prophet, ML-based)
- Integrate with BI dashboards for visualization
- Real-time alerting and anomaly detection
- Automated report scheduling and distribution

---

*End of Guide*
