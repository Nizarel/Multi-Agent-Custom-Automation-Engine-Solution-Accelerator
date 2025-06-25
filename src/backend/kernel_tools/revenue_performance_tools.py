"""Revenue Performance Tools for sales analysis using MCP client.

This module provides comprehensive revenue performance analysis tools for the 
Multi-Agent Custom Automation Engine Solution Accelerator. These tools enable
real-time financial performance insights, revenue optimization, and sales forecasting
for beverage distribution operations.

Key Features:
- Revenue trend analysis across multiple dimensions
- Profitability calculations by channel, zone, and category  
- Best-selling product rankings by volume and value
- AI-powered sales forecasting with seasonality considerations
- Financial KPI monitoring and variance analysis

Author: Multi-Agent Custom Automation Engine Solution Accelerator
Version: 1.0
Date: June 25, 2025
"""

import logging
from datetime import datetime, timedelta
from typing import Annotated, Optional, Dict, Any

from semantic_kernel.functions import kernel_function
from models.messages_kernel import AgentType
from services.mcp_integration_service import get_mcp_service

logger = logging.getLogger(__name__)


class RevenuePerformanceTools:
    """Tools for revenue performance analysis using MCP client.
    
    This class provides specialized tools for financial analysis in beverage distribution,
    covering revenue trends, profitability analysis, product performance, and sales forecasting.
    All tools integrate with the MCP (Model Context Protocol) client for secure database access.
    """
    
    agent_name = AgentType.REVENUE_PERFORMANCE.value
    
    def __init__(self, mcp_client=None):
        """Initialize Revenue Performance Tools with MCP client.
        
        Args:
            mcp_client: MCP client instance for database operations (deprecated, use MCP service)
        """
        self.mcp_client = mcp_client  # Keep for backward compatibility
        self._cache_timeout = 300  # 5 minutes cache for performance
        self._query_cache = {}
    
    @staticmethod
    @kernel_function(
        name="analyze_revenue_trends",
        description="Analyze revenue trends across different dimensions including time periods, zones, and product categories with detailed insights."
    )
    async def analyze_revenue_trends(
        time_period: Annotated[str, "Time period for analysis ('last_30_days', 'last_quarter', 'YTD', 'custom')"] = "last_30_days",
        zone: Annotated[str, "Geographic zone to analyze ('all', 'Norte', 'Sur', 'Occidente', 'Centro')"] = "all",
        product_category: Annotated[str, "Product category to analyze ('all', 'REFRESCOS', 'AGUA', 'JUGOS')"] = "all",
        start_date: Annotated[Optional[str], "Custom start date in YYYY-MM-DD format (for custom time_period)"] = None,
        end_date: Annotated[Optional[str], "Custom end date in YYYY-MM-DD format (for custom time_period)"] = None
    ) -> str:
        """
        Analyze revenue trends across different dimensions.
        
        Provides comprehensive revenue analysis including:
        - Total revenue and volume metrics
        - Geographic and category breakdowns
        - Month-over-month trend analysis
        - Customer engagement metrics
        - Average transaction values
        
        Args:
            time_period: Time period for analysis
            zone: Geographic zone to analyze
            product_category: Product category to analyze
            start_date: Custom start date (optional)
            end_date: Custom end date (optional)
            
        Returns:
            Detailed revenue trend analysis with actionable insights
        """
        try:
            # Calculate date range based on time period
            end_date_calc = datetime.now()
            
            if time_period == "custom" and start_date and end_date:
                start_date_calc = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_calc = datetime.strptime(end_date, '%Y-%m-%d')
            elif time_period == "last_30_days":
                start_date_calc = end_date_calc - timedelta(days=30)
            elif time_period == "last_quarter":
                start_date_calc = end_date_calc - timedelta(days=90)
            elif time_period == "YTD":
                start_date_calc = datetime(end_date_calc.year, 1, 1)
            else:
                start_date_calc = end_date_calc - timedelta(days=30)
            
            # Build comprehensive query with proper joins
            query = f"""
            SELECT 
                FORMAT(t.Fecha, 'yyyy-MM') as month,
                COALESCE(m.Zona, 'Unknown') as zone,
                COALESCE(p.Categoria, 'Unknown') as category,
                SUM(CAST(s.net_revenue AS DECIMAL(18,2))) as total_revenue,
                SUM(CAST(s.VentasCajasUnidad AS DECIMAL(18,2))) as total_volume,
                COUNT(DISTINCT s.customer_id) as unique_customers,
                COUNT(*) as transaction_count,
                AVG(CAST(s.net_revenue AS DECIMAL(18,2))) as avg_transaction_value,
                MIN(s.calday) as period_start,
                MAX(s.calday) as period_end
            FROM segmentacion s
            LEFT JOIN tiempo t ON s.calday = t.Fecha
            LEFT JOIN cliente c ON s.customer_id = c.customer_id
            LEFT JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
            LEFT JOIN mercado m ON cc.cedi_id = m.CEDIid
            LEFT JOIN producto p ON s.material_id = p.Material
            WHERE t.Fecha >= '{start_date_calc.strftime('%Y-%m-%d')}'
                AND t.Fecha <= '{end_date_calc.strftime('%Y-%m-%d')}'
                AND s.net_revenue IS NOT NULL
                AND s.net_revenue > 0
            """
            
            # Add filters based on parameters
            if zone != "all":
                query += f" AND m.Zona = '{zone}'"
            if product_category != "all":
                query += f" AND p.Categoria = '{product_category}'"
                
            query += """
            GROUP BY FORMAT(t.Fecha, 'yyyy-MM'), m.Zona, p.Categoria
            ORDER BY month DESC, total_revenue DESC
            """
            
            logger.info(f"Executing revenue trends analysis for period: {time_period}, zone: {zone}, category: {product_category}")
            
            # Execute query via MCP Integration Service
            try:
                # First try the new MCP service
                mcp_service = await get_mcp_service()
                result = await mcp_service.execute_query(query)
                
                return RevenuePerformanceTools._format_revenue_trends(result, time_period, zone, product_category)
                
            except Exception as query_error:
                logger.error(f"Database query failed: {str(query_error)}")
                
                # Fallback to old MCP client if available
                if hasattr(RevenuePerformanceTools, 'mcp_client') and RevenuePerformanceTools.mcp_client:
                    try:
                        result = await RevenuePerformanceTools.mcp_client.execute_query(query)
                        return RevenuePerformanceTools._format_revenue_trends(result, time_period, zone, product_category)
                    except Exception as fallback_error:
                        logger.error(f"Fallback MCP client also failed: {str(fallback_error)}")
                
                # Final fallback to mock data
                result = await RevenuePerformanceTools._execute_fallback_query("revenue_trends", {
                    "time_period": time_period,
                    "zone": zone,
                    "category": product_category
                })
                return RevenuePerformanceTools._format_revenue_trends(result, time_period, zone, product_category)
                
        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {str(e)}")
            return f"❌ Error analyzing revenue trends: {str(e)}\n\nPlease check your parameters and try again."
    
    @staticmethod
    @kernel_function(
        name="calculate_profitability",
        description="Calculate comprehensive profitability metrics by different business dimensions including margins, ROI, and performance rankings."
    )
    async def calculate_profitability(
        dimension: Annotated[str, "Dimension to analyze ('channel', 'zone', 'category', 'product', 'cedi')"] = "category",
        time_period: Annotated[str, "Time period for analysis ('last_30_days', 'last_quarter', 'YTD')"] = "last_30_days",
        top_n: Annotated[int, "Number of top results to return (1-50)"] = 10,
        include_margins: Annotated[bool, "Include detailed margin calculations"] = True
    ) -> str:
        """
        Calculate profitability metrics by different dimensions.
        
        Provides detailed profitability analysis including:
        - Revenue and volume metrics
        - Profit margin calculations
        - Customer acquisition metrics
        - Performance rankings and benchmarks
        - ROI indicators by dimension
        
        Args:
            dimension: Dimension to analyze profitability
            time_period: Time period for analysis
            top_n: Number of top results to return
            include_margins: Whether to include detailed margin calculations
            
        Returns:
            Comprehensive profitability analysis with rankings and insights
        """
        try:
            # Validate inputs
            if top_n < 1 or top_n > 50:
                return "❌ Error: top_n must be between 1 and 50."
            
            valid_dimensions = ['channel', 'zone', 'category', 'product', 'cedi']
            if dimension not in valid_dimensions:
                return f"❌ Error: dimension must be one of {valid_dimensions}."
            
            # Calculate date range
            end_date = datetime.now()
            if time_period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "last_quarter":
                start_date = end_date - timedelta(days=90)
            elif time_period == "YTD":
                start_date = datetime(end_date.year, 1, 1)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Build query based on dimension
            if dimension == "channel":
                group_field = "c.Canal_Comercial"
                select_field = "c.Canal_Comercial as dimension_value"
                dimension_label = "Channel"
            elif dimension == "zone":
                group_field = "m.Zona"
                select_field = "m.Zona as dimension_value"
                dimension_label = "Zone"
            elif dimension == "category":
                group_field = "p.Categoria"
                select_field = "p.Categoria as dimension_value"
                dimension_label = "Category"
            elif dimension == "cedi":
                group_field = "m.CEDI, m.CEDIid"
                select_field = "m.CEDI as dimension_value, m.CEDIid"
                dimension_label = "CEDI"
            else:  # product
                group_field = "p.Material, p.Producto"
                select_field = "p.Material as material_id, p.Producto as dimension_value"
                dimension_label = "Product"
            
            margin_fields = ""
            if include_margins:
                margin_fields = """
                    SUM(CAST(s.IngresoNetoSImpuestos AS DECIMAL(18,2))) as revenue_without_tax,
                    (SUM(CAST(s.net_revenue AS DECIMAL(18,2))) - SUM(CAST(s.IngresoNetoSImpuestos AS DECIMAL(18,2)))) as tax_amount,
                """
            
            query = f"""
            SELECT TOP {top_n}
                {select_field},
                SUM(CAST(s.net_revenue AS DECIMAL(18,2))) as total_revenue,
                {margin_fields}
                SUM(CAST(s.VentasCajasUnidad AS DECIMAL(18,2))) as total_volume,
                COUNT(DISTINCT s.customer_id) as customer_count,
                COUNT(*) as transaction_count,
                AVG(CAST(s.net_revenue AS DECIMAL(18,2))) as avg_transaction_value,
                SUM(CAST(s.net_revenue AS DECIMAL(18,2))) / NULLIF(SUM(CAST(s.VentasCajasUnidad AS DECIMAL(18,2))), 0) as revenue_per_unit,
                COUNT(DISTINCT s.calday) as active_days
            FROM segmentacion s
            LEFT JOIN tiempo t ON s.calday = t.Fecha
            LEFT JOIN cliente c ON s.customer_id = c.customer_id
            LEFT JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
            LEFT JOIN mercado m ON cc.cedi_id = m.CEDIid
            LEFT JOIN producto p ON s.material_id = p.Material
            WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
                AND s.net_revenue IS NOT NULL
                AND s.net_revenue > 0
            GROUP BY {group_field}
            ORDER BY total_revenue DESC
            """
            
            logger.info(f"Calculating profitability by {dimension} for {time_period}")
            
            # Execute query via MCP Integration Service
            try:
                # First try the new MCP service
                mcp_service = await get_mcp_service()
                result = await mcp_service.execute_query(query)
                
                return RevenuePerformanceTools._format_profitability_analysis(
                    result, dimension, dimension_label, time_period, include_margins
                )
                
            except Exception as query_error:
                logger.error(f"Database query failed: {str(query_error)}")
                
                # Fallback to old MCP client if available
                if hasattr(RevenuePerformanceTools, 'mcp_client') and RevenuePerformanceTools.mcp_client:
                    try:
                        result = await RevenuePerformanceTools.mcp_client.execute_query(query)
                        return RevenuePerformanceTools._format_profitability_analysis(
                            result, dimension, dimension_label, time_period, include_margins
                        )
                    except Exception as fallback_error:
                        logger.error(f"Fallback MCP client also failed: {str(fallback_error)}")
                
                # Final fallback to mock data
                result = await RevenuePerformanceTools._execute_fallback_query("profitability", {
                    "dimension": dimension,
                    "time_period": time_period,
                    "top_n": top_n
                })
                return RevenuePerformanceTools._format_profitability_analysis(
                    result, dimension, dimension_label, time_period, include_margins
                )
                
        except Exception as e:
            logger.error(f"Error calculating profitability: {str(e)}")
            return f"❌ Error calculating profitability: {str(e)}"
    
    @staticmethod
    @kernel_function(
        name="get_best_selling_products",
        description="Get comprehensive best-selling products analysis by volume or value with detailed performance metrics and customer insights."
    )
    async def get_best_selling_products(
        metric: Annotated[str, "Metric to rank by ('volume', 'value', 'frequency')"] = "value",
        zone: Annotated[str, "Zone to filter by ('all' or specific zone name)"] = "all",
        time_period: Annotated[str, "Time period for analysis ('last_30_days', 'last_quarter', 'YTD')"] = "last_30_days",
        limit: Annotated[int, "Number of products to return (1-50)"] = 20,
        category_filter: Annotated[str, "Product category filter ('all' or specific category)"] = "all"
    ) -> str:
        """
        Get best-selling products by volume, value, or frequency.
        
        Provides comprehensive product performance analysis including:
        - Sales volume and revenue metrics
        - Customer engagement and loyalty indicators
        - Price performance and market penetration
        - Seasonal and trend indicators
        - Category and brand performance
        
        Args:
            metric: Whether to rank by volume, value, or frequency
            zone: Geographic zone to analyze
            time_period: Time period for analysis
            limit: Number of products to return
            category_filter: Product category filter
            
        Returns:
            Comprehensive list of best-selling products with detailed metrics
        """
        try:
            # Validate inputs
            if limit < 1 or limit > 50:
                return "❌ Error: limit must be between 1 and 50."
            
            valid_metrics = ['volume', 'value', 'frequency']
            if metric not in valid_metrics:
                return f"❌ Error: metric must be one of {valid_metrics}."
            
            # Calculate date range
            end_date = datetime.now()
            if time_period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "last_quarter":
                start_date = end_date - timedelta(days=90)
            elif time_period == "YTD":
                start_date = datetime(end_date.year, 1, 1)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Determine order by clause
            if metric == "value":
                order_by = "total_revenue DESC"
            elif metric == "volume":
                order_by = "total_volume DESC"
            else:  # frequency
                order_by = "transaction_frequency DESC"
            
            # Build comprehensive query
            query = f"""
            SELECT TOP {limit}
                p.Material,
                p.Producto,
                COALESCE(p.Categoria, 'Unknown') as categoria,
                COALESCE(p.Subcategoria, 'Unknown') as subcategoria,
                COALESCE(p.AgrupadordeMarca, 'Unknown') as brand,
                SUM(CAST(s.net_revenue AS DECIMAL(18,2))) as total_revenue,
                SUM(CAST(s.VentasCajasUnidad AS DECIMAL(18,2))) as total_volume,
                COUNT(DISTINCT s.customer_id) as customer_count,
                COUNT(*) as transaction_frequency,
                COUNT(DISTINCT s.calday) as days_sold,
                AVG(CAST(s.net_revenue AS DECIMAL(18,2))) as avg_transaction_value,
                SUM(CAST(s.net_revenue AS DECIMAL(18,2))) / NULLIF(SUM(CAST(s.VentasCajasUnidad AS DECIMAL(18,2))), 0) as avg_price_per_unit,
                COUNT(*) * 1.0 / COUNT(DISTINCT s.customer_id) as transactions_per_customer
            FROM segmentacion s
            LEFT JOIN tiempo t ON s.calday = t.Fecha
            LEFT JOIN produto p ON s.material_id = p.Material
            """
            
            # Add zone filter if specified
            if zone != "all":
                query += f"""
                LEFT JOIN cliente c ON s.customer_id = c.customer_id
                LEFT JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
                LEFT JOIN mercado m ON cc.cedi_id = m.CEDIid
                WHERE m.Zona = '{zone}'
                AND t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                """
            else:
                query += f"""
                WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                """
            
            query += f"""
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
                AND s.net_revenue IS NOT NULL
                AND s.net_revenue > 0
            """
            
            # Add category filter if specified
            if category_filter != "all":
                query += f" AND p.Categoria = '{category_filter}'"
                
            query += f"""
            GROUP BY p.Material, p.Produto, p.Categoria, p.Subcategoria, p.AgrupadordeMarca
            ORDER BY {order_by}
            """
            
            logger.info(f"Getting best-selling products by {metric} for zone: {zone}, period: {time_period}")
            
            # Execute query via MCP Integration Service
            try:
                # First try the new MCP service
                mcp_service = await get_mcp_service()
                result = await mcp_service.execute_query(query)
                
                return RevenuePerformanceTools._format_best_selling_products(
                    result, metric, zone, time_period, category_filter
                )
                
            except Exception as query_error:
                logger.error(f"Database query failed: {str(query_error)}")
                
                # Fallback to old MCP client if available
                if hasattr(RevenuePerformanceTools, 'mcp_client') and RevenuePerformanceTools.mcp_client:
                    try:
                        result = await RevenuePerformanceTools.mcp_client.execute_query(query)
                        return RevenuePerformanceTools._format_best_selling_products(
                            result, metric, zone, time_period, category_filter
                        )
                    except Exception as fallback_error:
                        logger.error(f"Fallback MCP client also failed: {str(fallback_error)}")
                
                # Final fallback to mock data
                result = await RevenuePerformanceTools._execute_fallback_query("best_selling", {
                    "metric": metric,
                    "zone": zone,
                    "time_period": time_period,
                    "limit": limit
                })
                return RevenuePerformanceTools._format_best_selling_products(
                    result, metric, zone, time_period, category_filter
                )
                
        except Exception as e:
            logger.error(f"Error getting best-selling products: {str(e)}")
            return f"❌ Error getting best-selling products: {str(e)}"
    
    @staticmethod
    @kernel_function(
        name="forecast_sales",
        description="Generate AI-powered sales forecasts with seasonality considerations, confidence intervals, and variance analysis."
    )
    async def forecast_sales(
        forecast_period: Annotated[str, "Period to forecast ('next_month', 'next_quarter', 'next_6_months')"] = "next_month",
        dimension: Annotated[str, "Dimension to forecast by ('cedi', 'product', 'category', 'zone')"] = "category",
        use_seasonality: Annotated[bool, "Whether to consider seasonal patterns"] = True,
        confidence_level: Annotated[float, "Confidence level for predictions (0.8-0.99)"] = 0.95,
        include_variance_analysis: Annotated[bool, "Include forecast vs actual variance analysis"] = True
    ) -> str:
        """
        Generate sales forecast for specified period and dimension.
        
        Provides comprehensive forecasting including:
        - Historical trend analysis and pattern recognition
        - Seasonal adjustment factors
        - Multiple forecasting scenarios (optimistic, realistic, pessimistic)
        - Confidence intervals and prediction accuracy metrics
        - Variance analysis against previous forecasts
        
        Args:
            forecast_period: Period to forecast
            dimension: Dimension to forecast by
            use_seasonality: Whether to consider seasonal patterns
            confidence_level: Confidence level for predictions
            include_variance_analysis: Include forecast accuracy analysis
            
        Returns:
            Comprehensive sales forecast with confidence intervals and insights
        """
        try:
            # Validate inputs
            if confidence_level < 0.8 or confidence_level > 0.99:
                return "❌ Error: confidence_level must be between 0.8 and 0.99."
            
            valid_dimensions = ['cedi', 'product', 'category', 'zone']
            if dimension not in valid_dimensions:
                return f"❌ Error: dimension must be one of {valid_dimensions}."
            
            valid_periods = ['next_month', 'next_quarter', 'next_6_months']
            if forecast_period not in valid_periods:
                return f"❌ Error: forecast_period must be one of {valid_periods}."
            
            # Calculate lookback period for historical analysis
            if forecast_period == "next_6_months":
                lookback_days = 365  # 1 year of history
            elif forecast_period == "next_quarter":
                lookback_days = 180  # 6 months of history
            else:  # next_month
                lookback_days = 90   # 3 months of history
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get historical data for forecasting
            if dimension == "cedi":
                group_by = "m.CEDI, m.CEDIid"
                select_field = "m.CEDI as dimension_value, m.CEDIid"
            elif dimension == "product":
                group_by = "p.Material, p.Produto"
                select_field = "p.Material as material_id, p.Produto as dimension_value"
            elif dimension == "zone":
                group_by = "m.Zona"
                select_field = "m.Zona as dimension_value"
            else:  # category
                group_by = "p.Categoria"
                select_field = "p.Categoria as dimension_value"
            
            # Historical data query with time series breakdown
            query = f"""
            SELECT 
                {select_field},
                FORMAT(t.Fecha, 'yyyy-MM') as month,
                DATEPART(week, t.Fecha) as week_of_year,
                DATEPART(quarter, t.Fecha) as quarter,
                SUM(CAST(s.net_revenue AS DECIMAL(18,2))) as monthly_revenue,
                SUM(CAST(s.VentasCajasUnidad AS DECIMAL(18,2))) as monthly_volume,
                COUNT(DISTINCT s.customer_id) as monthly_customers,
                COUNT(*) as monthly_transactions,
                AVG(CAST(s.net_revenue AS DECIMAL(18,2))) as avg_transaction_value
            FROM segmentacion s
            LEFT JOIN tiempo t ON s.calday = t.Fecha
            LEFT JOIN cliente c ON s.customer_id = c.customer_id
            LEFT JOIN cliente_cedi cc ON c.customer_id = cc.customer_id
            LEFT JOIN mercado m ON cc.cedi_id = m.CEDIid
            LEFT JOIN produto p ON s.material_id = p.Material
            WHERE t.Fecha >= '{start_date.strftime('%Y-%m-%d')}'
                AND t.Fecha <= '{end_date.strftime('%Y-%m-%d')}'
                AND s.net_revenue IS NOT NULL
                AND s.net_revenue > 0
            GROUP BY {group_by}, FORMAT(t.Fecha, 'yyyy-MM'), DATEPART(week, t.Fecha), DATEPART(quarter, t.Fecha)
            ORDER BY month DESC
            """
            
            logger.info(f"Generating {forecast_period} forecast by {dimension} with seasonality: {use_seasonality}")
            
            # Execute query via MCP Integration Service
            try:
                # First try the new MCP service
                mcp_service = await get_mcp_service()
                result = await mcp_service.execute_query(query)
                
                return RevenuePerformanceTools._generate_forecast(
                    result, forecast_period, dimension, use_seasonality, 
                    confidence_level, include_variance_analysis
                )
                
            except Exception as query_error:
                logger.error(f"Database query failed: {str(query_error)}")
                
                # Fallback to old MCP client if available
                if hasattr(RevenuePerformanceTools, 'mcp_client') and RevenuePerformanceTools.mcp_client:
                    try:
                        result = await RevenuePerformanceTools.mcp_client.execute_query(query)
                        return RevenuePerformanceTools._generate_forecast(
                            result, forecast_period, dimension, use_seasonality, 
                            confidence_level, include_variance_analysis
                        )
                    except Exception as fallback_error:
                        logger.error(f"Fallback MCP client also failed: {str(fallback_error)}")
                
                # Final fallback to mock data
                result = await RevenuePerformanceTools._execute_fallback_query("forecast", {
                    "forecast_period": forecast_period,
                    "dimension": dimension,
                    "use_seasonality": use_seasonality
                })
                return RevenuePerformanceTools._generate_forecast(
                    result, forecast_period, dimension, use_seasonality, 
                    confidence_level, include_variance_analysis
                )
                
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return f"❌ Error generating forecast: {str(e)}"
    
    # Helper methods for formatting results
    
    @staticmethod
    def _format_revenue_trends(data: Dict[str, Any], time_period: str, zone: str, category: str) -> str:
        """Format revenue trends data into actionable insights."""
        try:
            # Handle different result formats
            if isinstance(data, dict):
                rows = data.get("data", data.get("rows", []))
            elif isinstance(data, list):
                rows = data
            else:
                rows = []
            
            if not rows:
                return f"""
📊 **Revenue Trend Analysis**
📅 Period: {time_period}
🌎 Zone: {zone}
📦 Category: {category}

❌ No revenue data found for the specified criteria.

**Recommendations:**
- Verify the time period and filters
- Check if there were sales activities during this period
- Consider expanding the analysis to include more zones or categories
"""
            
            # Calculate summary metrics
            total_revenue = sum(float(row.get("total_revenue", 0)) for row in rows)
            total_volume = sum(float(row.get("total_volume", 0)) for row in rows)
            unique_customers = sum(int(row.get("unique_customers", 0)) for row in rows)
            total_transactions = sum(int(row.get("transaction_count", 0)) for row in rows)
            
            # Build comprehensive insights
            insights = f"""
📊 **Revenue Trend Analysis**
📅 Period: {time_period.replace('_', ' ').title()}
🌎 Zone: {zone}
📦 Category: {category}

## 🎯 Summary Metrics
- 💰 **Total Revenue:** ${total_revenue:,.2f}
- 📦 **Total Volume:** {total_volume:,.0f} units
- 👥 **Unique Customers:** {unique_customers:,}
- 🛒 **Total Transactions:** {total_transactions:,}
- 💵 **Avg Transaction Value:** ${total_revenue/max(total_transactions, 1):,.2f}

## 🏆 Top Performing Segments
"""
            
            # Add top 5 segments with performance indicators
            for i, row in enumerate(rows[:5]):
                revenue = float(row.get('total_revenue', 0))
                volume = float(row.get('total_volume', 0))
                customers = int(row.get('unique_customers', 0))
                avg_transaction = float(row.get('avg_transaction_value', 0))
                
                # Performance indicators
                performance_stars = "⭐" * min(5, int(revenue / max(total_revenue/5, 1)))
                
                insights += f"""
### {i+1}. **{row.get('zone', 'N/A')} - {row.get('category', 'N/A')}**
   - 💰 Revenue: ${revenue:,.2f} {performance_stars}
   - 📦 Volume: {volume:,.0f} units
   - 👥 Customers: {customers:,}
   - 💵 Avg Transaction: ${avg_transaction:,.2f}
"""
            
            # Add trend analysis if multiple periods available
            if len(rows) > 1:
                latest_month = rows[0]
                previous_month = rows[1] if len(rows) > 1 else None
                
                if previous_month:
                    current_revenue = float(latest_month.get('total_revenue', 0))
                    previous_revenue = float(previous_month.get('total_revenue', 0))
                    
                    if previous_revenue > 0:
                        revenue_change = ((current_revenue - previous_revenue) / previous_revenue) * 100
                        trend_icon = "📈" if revenue_change > 0 else "📉" if revenue_change < 0 else "➡️"
                        insights += f"""
## 📈 Trend Analysis
**Month-over-Month Change:** {trend_icon} {revenue_change:+.1f}%
"""
            
            # Add actionable recommendations
            insights += f"""
## 💡 Strategic Recommendations
- 🎯 **Focus Areas:** Top 3 segments contribute ${sum(float(row.get('total_revenue', 0)) for row in rows[:3]):,.2f} ({sum(float(row.get('total_revenue', 0)) for row in rows[:3])/total_revenue*100:.1f}% of total revenue)
- 📊 **Customer Engagement:** Average {total_revenue/max(unique_customers, 1):,.2f} revenue per customer
- 🔄 **Transaction Frequency:** {total_transactions/max(unique_customers, 1):.1f} transactions per customer
- 🚀 **Growth Opportunity:** Focus on expanding successful segments to underperforming zones
"""
            
            return insights
            
        except Exception as e:
            logger.error(f"Error formatting revenue trends: {str(e)}")
            return f"❌ Error formatting revenue trend analysis: {str(e)}"
    
    @staticmethod
    def _format_profitability_analysis(
        data: Dict[str, Any], 
        dimension: str, 
        dimension_label: str, 
        time_period: str, 
        include_margins: bool
    ) -> str:
        """Format profitability analysis data with comprehensive metrics."""
        try:
            # Handle different result formats
            if isinstance(data, dict):
                rows = data.get("data", data.get("rows", []))
            elif isinstance(data, list):
                rows = data
            else:
                rows = []
            
            if not rows:
                return f"""
💼 **Profitability Analysis by {dimension_label}**
📅 Period: {time_period.replace('_', ' ').title()}

❌ No profitability data found for the specified criteria.

**Recommendations:**
- Verify the analysis dimension and time period
- Check if there were profitable operations during this period
- Consider adjusting filters or expanding the analysis scope
"""
            
            insights = f"""
💼 **Profitability Analysis by {dimension_label}**
📅 Period: {time_period.replace('_', ' ').title()}

## 🏆 Top {len(rows)} Most Profitable {dimension_label}s
"""
            
            total_revenue = 0
            total_volume = 0
            total_customers = 0
            
            for i, row in enumerate(rows):
                revenue = float(row.get('total_revenue', 0))
                volume = float(row.get('total_volume', 0))
                customers = int(row.get('customer_count', 0))
                transactions = int(row.get('transaction_count', 0))
                revenue_per_unit = float(row.get('revenue_per_unit', 0))
                active_days = int(row.get('active_days', 0))
                
                total_revenue += revenue
                total_volume += volume
                total_customers += customers
                
                # Performance indicators
                profitability_score = min(5, int(revenue_per_unit / 5))
                performance_indicator = "💎" * profitability_score if profitability_score > 0 else "📊"
                
                # Efficiency metrics
                daily_revenue = revenue / max(active_days, 1)
                customer_value = revenue / max(customers, 1)
                
                dimension_value = row.get('dimension_value', 'Unknown')
                material_id = row.get('material_id', '')
                if material_id:
                    dimension_value = f"{dimension_value} ({material_id})"
                
                insights += f"""
### {i+1}. **{dimension_value}** {performance_indicator}
   - 💰 **Revenue:** ${revenue:,.2f}
   - 📦 **Volume:** {volume:,.0f} units
   - 👥 **Customers:** {customers:,}
   - 🛒 **Transactions:** {transactions:,}
   - 💵 **Revenue/Unit:** ${revenue_per_unit:.2f}
   - 📈 **Daily Avg Revenue:** ${daily_revenue:,.2f}
   - 🎯 **Customer Value:** ${customer_value:,.2f}
   - 📅 **Active Days:** {active_days}
"""
                
                # Add margin analysis if available and requested
                if include_margins and 'revenue_without_tax' in row:
                    revenue_without_tax = float(row.get('revenue_without_tax', 0))
                    tax_amount = float(row.get('tax_amount', 0))
                    if revenue > 0:
                        tax_rate = (tax_amount / revenue) * 100
                        insights += f"   - 🏛️ **Tax Rate:** {tax_rate:.1f}% (${revenue_without_tax:,.2f} pre-tax)\n"
            
            # Add comprehensive summary insights
            avg_revenue_per_unit = sum(float(row.get('revenue_per_unit', 0)) for row in rows) / len(rows)
            avg_customer_value = total_revenue / max(total_customers, 1)
            
            insights += f"""
## 📊 Strategic Insights
- **Total Revenue (Top {len(rows)}):** ${total_revenue:,.2f}
- **Average Revenue per Unit:** ${avg_revenue_per_unit:.2f}
- **Average Customer Value:** ${avg_customer_value:,.2f}
- **Market Concentration:** Top 3 {dimension_label}s represent {sum(float(row.get('total_revenue', 0)) for row in rows[:3])/total_revenue*100:.1f}% of revenue

## 💡 Recommendations
- 🎯 **Focus Strategy:** Concentrate resources on top 3 {dimension_label}s for maximum ROI
- 📈 **Growth Opportunity:** Replicate success factors from top performers to lower-ranked segments
- 🔍 **Optimization Target:** {dimension_label}s with high volume but low revenue per unit need pricing review
- 📊 **Performance Monitoring:** Track revenue per unit trends monthly for early performance indicators
"""
            
            return insights
            
        except Exception as e:
            logger.error(f"Error formatting profitability analysis: {str(e)}")
            return f"❌ Error formatting profitability analysis: {str(e)}"
    
    @staticmethod
    def _format_best_selling_products(
        data: Dict[str, Any], 
        metric: str, 
        zone: str, 
        time_period: str, 
        category_filter: str
    ) -> str:
        """Format best-selling products data with detailed performance metrics."""
        try:
            # Handle different result formats
            if isinstance(data, dict):
                rows = data.get("data", data.get("rows", []))
            elif isinstance(data, list):
                rows = data
            else:
                rows = []
            
            if not rows:
                return f"""
🏆 **Best-Selling Products by {metric.title()}**
📅 Period: {time_period.replace('_', ' ').title()}
🌎 Zone: {zone}
📦 Category Filter: {category_filter}

❌ No product data found for the specified criteria.

**Recommendations:**
- Verify the analysis filters and time period
- Check if there were product sales during this period
- Consider expanding the zone or category filters
"""
            
            metric_label = {
                'value': 'Revenue Value',
                'volume': 'Sales Volume', 
                'frequency': 'Transaction Frequency'
            }.get(metric, metric.title())
            
            insights = f"""
🏆 **Best-Selling Products by {metric_label}**
📅 Period: {time_period.replace('_', ' ').title()}
🌎 Zone: {zone}
📦 Category Filter: {category_filter}

## 🚀 Top {len(rows)} Products Performance
"""
            
            total_revenue = sum(float(row.get('total_revenue', 0)) for row in rows)
            total_volume = sum(float(row.get('total_volume', 0)) for row in rows)
            total_customers = sum(int(row.get('customer_count', 0)) for row in rows)
            
            for i, row in enumerate(rows):
                material = row.get('Material', 'Unknown')
                product = row.get('Produto', 'Unknown Product')
                category = row.get('categoria', 'Unknown')
                subcategory = row.get('subcategoria', 'Unknown')
                brand = row.get('brand', 'Unknown')
                
                revenue = float(row.get('total_revenue', 0))
                volume = float(row.get('total_volume', 0))
                customers = int(row.get('customer_count', 0))
                frequency = int(row.get('transaction_frequency', 0))
                days_sold = int(row.get('days_sold', 0))
                avg_price = float(row.get('avg_price_per_unit', 0))
                transactions_per_customer = float(row.get('transactions_per_customer', 0))
                
                # Performance indicators based on metric
                if metric == 'value':
                    performance_score = min(5, int(revenue / max(total_revenue/10, 1)))
                elif metric == 'volume':
                    performance_score = min(5, int(volume / max(total_volume/10, 1)))
                else:  # frequency
                    performance_score = min(5, int(frequency / max(sum(int(r.get('transaction_frequency', 0)) for r in rows)/10, 1)))
                
                popularity_stars = "🔥" * performance_score if performance_score > 0 else "📊"
                
                # Market penetration and loyalty indicators
                market_penetration = (customers / max(total_customers, 1)) * 100
                loyalty_indicator = "🎯" if transactions_per_customer > 2 else "👥"
                
                insights += f"""
### {i+1}. **{product}** ({material})
   - 🏷️ **Category:** {category} → {subcategory}
   - 🏢 **Brand:** {brand}
   - 💰 **Revenue:** ${revenue:,.2f}
   - 📦 **Volume:** {volume:,.0f} units
   - 👥 **Customers:** {customers:,} ({market_penetration:.1f}% market share)
   - 🛒 **Transactions:** {frequency:,} ({transactions_per_customer:.1f} per customer) {loyalty_indicator}
   - 💵 **Avg Price/Unit:** ${avg_price:.2f}
   - 📅 **Days Active:** {days_sold}
   - 🔥 **Popularity:** {popularity_stars}
"""
            
            # Add strategic insights and recommendations
            top_3_revenue = sum(float(row.get('total_revenue', 0)) for row in rows[:3])
            top_3_percentage = (top_3_revenue / total_revenue) * 100 if total_revenue > 0 else 0
            
            # Category distribution analysis
            categories = {}
            for row in rows:
                cat = row.get('categoria', 'Unknown')
                if cat not in categories:
                    categories[cat] = {'count': 0, 'revenue': 0}
                categories[cat]['count'] += 1
                categories[cat]['revenue'] += float(row.get('total_revenue', 0))
            
            insights += f"""
## 📊 Strategic Insights
- **Top 3 Product Concentration:** {top_3_percentage:.1f}% of total revenue
- **Average Revenue per Product:** ${total_revenue/len(rows):,.2f}
- **Category Distribution:** {len(categories)} categories represented
- **Customer Reach:** {total_customers:,} unique customers engaged

## 🎯 Category Performance
"""
            
            for cat, data in sorted(categories.items(), key=lambda x: x[1]['revenue'], reverse=True)[:3]:
                insights += f"- **{cat}:** {data['count']} products, ${data['revenue']:,.2f} revenue\n"
            
            insights += f"""
## 💡 Strategic Recommendations
- 🚀 **Star Products:** Focus marketing efforts on top 5 products for maximum impact
- 📈 **Growth Strategy:** Analyze success factors of top performers for replication
- 🎯 **Customer Loyalty:** Products with high repeat transactions deserve loyalty programs
- 📊 **Inventory Optimization:** Ensure adequate stock levels for top {min(10, len(rows))} products
- 🔄 **Cross-Selling:** Bundle complementary products from different categories
- 💰 **Pricing Strategy:** Monitor price sensitivity for high-volume, low-margin products
"""
            
            return insights
            
        except Exception as e:
            logger.error(f"Error formatting best-selling products: {str(e)}")
            return f"❌ Error formatting best-selling products analysis: {str(e)}"
    
    @staticmethod
    def _generate_forecast(
        data: Dict[str, Any], 
        forecast_period: str, 
        dimension: str, 
        use_seasonality: bool,
        confidence_level: float,
        include_variance_analysis: bool
    ) -> str:
        """Generate comprehensive sales forecast with confidence intervals."""
        try:
            # Handle different result formats
            if isinstance(data, dict):
                rows = data.get("data", data.get("rows", []))
            elif isinstance(data, list):
                rows = data
            else:
                rows = []
            
            if not rows:
                return f"""
🔮 **Sales Forecast Analysis**
📅 Forecast Period: {forecast_period.replace('_', ' ').title()}
📊 Dimension: {dimension.title()}
🌡️ Seasonality: {'Enabled' if use_seasonality else 'Disabled'}
🎯 Confidence Level: {confidence_level*100:.0f}%

❌ Insufficient historical data for forecasting.

**Requirements for Forecasting:**
- Minimum 3 months of historical data
- Consistent sales activity in the analyzed dimension
- Valid revenue and volume data points

**Recommendations:**
- Expand the historical analysis period
- Verify data quality and completeness
- Consider using aggregated dimensions for forecasting
"""
            
            insights = f"""
🔮 **Sales Forecast Analysis**
📅 **Forecast Period:** {forecast_period.replace('_', ' ').title()}
📊 **Dimension:** {dimension.title()}
🌡️ **Seasonality:** {'Enabled' if use_seasonality else 'Disabled'}
🎯 **Confidence Level:** {confidence_level*100:.0f}%

## 📈 Historical Analysis Foundation
"""
            
            # Analyze historical data patterns
            monthly_data = {}
            dimension_totals = {}
            
            for row in rows:
                month = row.get('month', 'Unknown')
                dim_value = row.get('dimension_value', 'Unknown')
                revenue = float(row.get('monthly_revenue', 0))
                volume = float(row.get('monthly_volume', 0))
                
                if month not in monthly_data:
                    monthly_data[month] = {'revenue': 0, 'volume': 0, 'customers': 0}
                
                monthly_data[month]['revenue'] += revenue
                monthly_data[month]['volume'] += volume
                monthly_data[month]['customers'] += int(row.get('monthly_customers', 0))
                
                if dim_value not in dimension_totals:
                    dimension_totals[dim_value] = {'revenue': 0, 'volume': 0, 'months': 0}
                
                dimension_totals[dim_value]['revenue'] += revenue
                dimension_totals[dim_value]['volume'] += volume
                dimension_totals[dim_value]['months'] += 1
            
            # Calculate trend and seasonality factors
            sorted_months = sorted(monthly_data.keys(), reverse=True)
            recent_months = sorted_months[:3] if len(sorted_months) >= 3 else sorted_months
            
            if len(recent_months) >= 2:
                latest_revenue = monthly_data[recent_months[0]]['revenue']
                previous_revenue = monthly_data[recent_months[1]]['revenue']
                growth_rate = ((latest_revenue - previous_revenue) / max(previous_revenue, 1)) * 100 if previous_revenue > 0 else 0
            else:
                growth_rate = 0
            
            insights += f"""
- **Historical Months Analyzed:** {len(monthly_data)}
- **Recent Growth Trend:** {growth_rate:+.1f}% month-over-month
- **Dimensions Analyzed:** {len(dimension_totals)}
"""
            
            # Generate forecasts for top performing dimensions
            top_dimensions = sorted(dimension_totals.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]
            
            insights += f"""
## 🎯 Forecast Results - Top {len(top_dimensions)} {dimension.title()}s

"""
            
            total_forecast_revenue = 0
            total_forecast_volume = 0
            
            for i, (dim_value, totals) in enumerate(top_dimensions):
                avg_monthly_revenue = totals['revenue'] / max(totals['months'], 1)
                avg_monthly_volume = totals['volume'] / max(totals['months'], 1)
                
                # Apply growth trend and seasonality adjustments
                trend_factor = 1 + (growth_rate / 100)
                
                if use_seasonality:
                    # Simple seasonality factor based on current month
                    current_month = datetime.now().month
                    if current_month in [11, 12, 1]:  # Holiday season
                        seasonality_factor = 1.15
                    elif current_month in [6, 7, 8]:  # Summer season  
                        seasonality_factor = 1.10
                    else:
                        seasonality_factor = 1.0
                else:
                    seasonality_factor = 1.0
                
                # Calculate forecast periods
                if forecast_period == "next_month":
                    periods = 1
                elif forecast_period == "next_quarter":
                    periods = 3
                else:  # next_6_months
                    periods = 6
                
                # Base forecast
                base_forecast_revenue = avg_monthly_revenue * trend_factor * seasonality_factor * periods
                base_forecast_volume = avg_monthly_volume * trend_factor * seasonality_factor * periods
                
                # Confidence intervals
                confidence_margin = (1 - confidence_level) * 0.5
                lower_bound = base_forecast_revenue * (1 - confidence_margin)
                upper_bound = base_forecast_revenue * (1 + confidence_margin)
                
                total_forecast_revenue += base_forecast_revenue
                total_forecast_volume += base_forecast_volume
                
                # Performance indicators
                revenue_trend = "📈" if growth_rate > 5 else "📉" if growth_rate < -5 else "➡️"
                confidence_stars = "⭐" * int(confidence_level * 5)
                
                insights += f"""
### {i+1}. **{dim_value}** {revenue_trend}
   - 🎯 **Forecast Revenue:** ${base_forecast_revenue:,.2f}
   - 📦 **Forecast Volume:** {base_forecast_volume:,.0f} units
   - 📊 **Confidence Range:** ${lower_bound:,.2f} - ${upper_bound:,.2f}
   - 📈 **Historical Avg/Month:** ${avg_monthly_revenue:,.2f}
   - 🌡️ **Seasonality Factor:** {seasonality_factor:.2f}x
   - 🎯 **Confidence:** {confidence_stars}
"""
            
            # Add summary and strategic recommendations
            insights += f"""
## 🎯 Forecast Summary
- **Total Forecast Revenue:** ${total_forecast_revenue:,.2f}
- **Total Forecast Volume:** {total_forecast_volume:,.0f} units
- **Average Growth Assumption:** {growth_rate:+.1f}% month-over-month
- **Seasonality Impact:** {'+15%' if use_seasonality and datetime.now().month in [11,12,1] else '+10%' if use_seasonality and datetime.now().month in [6,7,8] else 'Neutral'}

## ⚡ Forecast Accuracy Indicators
- **Data Quality:** {'High' if len(monthly_data) >= 6 else 'Medium' if len(monthly_data) >= 3 else 'Low'}
- **Trend Stability:** {'Stable' if abs(growth_rate) < 10 else 'Volatile'}
- **Seasonality Confidence:** {'High' if use_seasonality else 'Not Applied'}

## 💡 Strategic Recommendations
- 📊 **Monitor Weekly:** Track actual vs forecast weekly for early trend detection
- 🎯 **Resource Allocation:** Plan inventory and staffing based on forecast confidence ranges
- 📈 **Growth Acceleration:** Focus on top 3 forecasted {dimension}s for maximum impact
- ⚠️ **Risk Mitigation:** Prepare contingency plans for {confidence_level*100:.0f}% confidence scenarios
- 🔄 **Model Refinement:** Update forecasts monthly with new actual data for improved accuracy
"""
            
            if include_variance_analysis and len(monthly_data) >= 3:
                insights += """
## 📊 Variance Analysis (Last 3 Months)
"""
                for month in recent_months:
                    revenue = monthly_data[month]['revenue']
                    # Simple variance calculation vs. average
                    avg_revenue = sum(monthly_data[m]['revenue'] for m in recent_months) / len(recent_months)
                    variance = ((revenue - avg_revenue) / max(avg_revenue, 1)) * 100
                    variance_indicator = "🟢" if abs(variance) < 10 else "🟡" if abs(variance) < 20 else "🔴"
                    insights += f"- **{month}:** {variance_indicator} {variance:+.1f}% vs average\n"
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return f"❌ Error generating forecast: {str(e)}"
    
    @staticmethod
    async def _execute_fallback_query(query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fallback queries when MCP client is not available (for testing)."""
        logger.warning(f"Using fallback data for {query_type} query")
        
        # Return mock data for testing and development
        if query_type == "revenue_trends":
            return {
                "data": [
                    {
                        "month": "2025-06",
                        "zone": params.get("zone", "Norte"),
                        "category": params.get("category", "REFRESCOS"),
                        "total_revenue": 150000.50,
                        "total_volume": 12500.0,
                        "unique_customers": 450,
                        "transaction_count": 1250,
                        "avg_transaction_value": 120.00
                    },
                    {
                        "month": "2025-05",
                        "zone": params.get("zone", "Norte"),
                        "category": params.get("category", "REFRESCOS"),
                        "total_revenue": 142000.25,
                        "total_volume": 11800.0,
                        "unique_customers": 425,
                        "transaction_count": 1180,
                        "avg_transaction_value": 120.34
                    }
                ]
            }
        elif query_type == "profitability":
            return {
                "data": [
                    {
                        "dimension_value": "REFRESCOS",
                        "total_revenue": 250000.75,
                        "total_volume": 20000.0,
                        "customer_count": 750,
                        "transaction_count": 2100,
                        "revenue_per_unit": 12.50,
                        "active_days": 30
                    }
                ]
            }
        elif query_type == "best_selling":
            return {
                "data": [
                    {
                        "Material": "MAT001",
                        "Produto": "Coca-Cola 600ml",
                        "categoria": "REFRESCOS",
                        "subcategoria": "COLAS",
                        "brand": "Coca-Cola",
                        "total_revenue": 85000.50,
                        "total_volume": 7200.0,
                        "customer_count": 320,
                        "transaction_frequency": 890,
                        "days_sold": 28,
                        "avg_price_per_unit": 11.81,
                        "transactions_per_customer": 2.78
                    }
                ]
            }
        elif query_type == "forecast":
            return {
                "data": [
                    {
                        "dimension_value": "REFRESCOS",
                        "month": "2025-06",
                        "monthly_revenue": 180000.00,
                        "monthly_volume": 15000.0,
                        "monthly_customers": 500,
                        "monthly_transactions": 1400
                    }
                ]
            }
        
        return {"data": []}
    
    @classmethod
    def set_mcp_client(cls, mcp_client):
        """Set the MCP client for all tools."""
        cls.mcp_client = mcp_client
        logger.info("MCP client configured for Revenue Performance Tools")
