"""Sales analysis tools using MCP client with enhanced async patterns."""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SalesAnalysisTools:
    """High-level sales analysis tools for agents with async optimization."""
    
    def __init__(self, mcp_client):
        """Initialize sales analysis tools.
        
        Args:
            mcp_client: MCP client instance
        """
        self.mcp_client = mcp_client
        # Import here to avoid circular imports
        from ..client import SalesDataAnalyzer
        self.analyzer = SalesDataAnalyzer(mcp_client)
    
    async def analyze_sales_performance(
        self, 
        period: str = "last_30_days",
        customer_filter: Optional[str] = None,
        product_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze sales performance for a given period using concurrent data fetching.
        
        Args:
            period: Time period (last_30_days, last_90_days, last_year, custom)
            customer_filter: Optional customer ID filter
            product_filter: Optional product/material ID filter
            
        Returns:
            Comprehensive sales performance analysis
        """
        try:
            # Calculate date range based on period
            end_date = datetime.now()
            
            if period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif period == "last_90_days":
                start_date = end_date - timedelta(days=90)
            elif period == "last_year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)  # default
            
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            # Execute all analytics concurrently for better performance
            tasks = [
                self.analyzer.get_sales_performance(start_str, end_str, customer_filter, product_filter),
                self.analyzer.get_sales_trends("weekly"),
                self.analyzer.get_top_customers(5),
                self.analyzer.get_product_analysis(5)
            ]
            
            performance, trends, top_customers, top_products = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            # Process results with error handling
            result = {
                "analysis_period": period,
                "date_range": f"{start_str} to {end_str}",
                "performance_metrics": performance if not isinstance(performance, Exception) else {"error": str(performance)},
                "sales_trends": trends[-4:] if isinstance(trends, list) and trends else [],
                "top_customers": top_customers if isinstance(top_customers, list) else [],
                "top_products": top_products if isinstance(top_products, list) else []
            }
            
            # Generate insights based on successful data
            result["insights"] = self._generate_insights(
                result["performance_metrics"], 
                result["sales_trends"], 
                result["top_customers"], 
                result["top_products"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sales performance analysis: {e}")
            return {"error": str(e)}
    
    async def get_customer_insights(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed customer insights.
        
        Args:
            customer_id: Specific customer ID or None for top customers
            
        Returns:
            Customer analysis and insights
        """
        try:
            if customer_id:
                # Analyze specific customer
                performance = await self.analyzer.get_sales_performance(
                    (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                    customer_id=customer_id
                )
                return {
                    "customer_id": customer_id,
                    "analysis": performance,
                    "type": "individual_customer"
                }
            else:
                # Get top customers analysis
                customers = await self.analyzer.get_top_customers(10)
                return {
                    "top_customers": customers,
                    "total_customers_analyzed": len(customers),
                    "type": "top_customers_overview"
                }
                
        except Exception as e:
            logger.error(f"Error in customer insights analysis: {e}")
            return {"error": str(e)}
    
    async def get_product_insights(self, material_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed product insights.
        
        Args:
            material_id: Specific material/product ID or None for top products
            
        Returns:
            Product analysis and insights
        """
        try:
            if material_id:
                # Analyze specific product
                performance = await self.analyzer.get_sales_performance(
                    (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                    material_id=material_id
                )
                return {
                    "material_id": material_id,
                    "analysis": performance,
                    "type": "individual_product"
                }
            else:
                # Get top products analysis
                products = await self.analyzer.get_product_analysis(15)
                return {
                    "top_products": products,
                    "total_products_analyzed": len(products),
                    "type": "top_products_overview"
                }
                
        except Exception as e:
            logger.error(f"Error in product insights analysis: {e}")
            return {"error": str(e)}
    
    async def get_territorial_performance(self) -> Dict[str, Any]:
        """Get territorial sales performance analysis.
        
        Returns:
            Territorial performance insights
        """
        try:
            territorial_data = await self.analyzer.get_territorial_analysis()
            
            if territorial_data:
                # Calculate totals and averages
                total_revenue = sum(t["total_revenue"] for t in territorial_data)
                total_customers = sum(t["unique_customers"] for t in territorial_data)
                
                return {
                    "territorial_breakdown": territorial_data,
                    "summary": {
                        "total_territories": len(territorial_data),
                        "total_revenue": total_revenue,
                        "total_customers": total_customers,
                        "avg_revenue_per_territory": total_revenue / len(territorial_data) if territorial_data else 0
                    },
                    "top_performing_territory": territorial_data[0] if territorial_data else None
                }
            else:
                return {"error": "No territorial data available"}
                
        except Exception as e:
            logger.error(f"Error in territorial performance analysis: {e}")
            return {"error": str(e)}
    
    def _generate_insights(
        self, 
        performance: Dict[str, Any], 
        trends: List[Dict[str, Any]], 
        customers: List[Dict[str, Any]], 
        products: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable insights from the data.
        
        Args:
            performance: Performance metrics
            trends: Sales trends data
            customers: Top customers data
            products: Top products data
            
        Returns:
            List of insight strings
        """
        insights = []
        
        try:
            # Performance insights
            if "metrics" in performance:
                metrics = performance["metrics"]
                if metrics.get("total_revenue", 0) > 0:
                    insights.append(f"Total revenue of ${metrics['total_revenue']:,.2f} across {metrics.get('unique_customers', 0)} customers")
                
                if metrics.get("daily_avg_revenue", 0) > 0:
                    insights.append(f"Average daily revenue: ${metrics['daily_avg_revenue']:,.2f}")
            
            # Customer insights
            if customers:
                top_customer = customers[0]
                insights.append(f"Top customer: {top_customer.get('customer_name', 'Unknown')} with ${top_customer.get('total_revenue', 0):,.2f} revenue")
            
            # Product insights
            if products:
                top_product = products[0]
                insights.append(f"Top product: {top_product.get('product_name', 'Unknown')} with ${top_product.get('total_revenue', 0):,.2f} revenue")
            
            # Trend insights
            if len(trends) >= 2:
                latest = trends[-1]
                previous = trends[-2]
                if latest.get("total_revenue", 0) > previous.get("total_revenue", 0):
                    insights.append("Sales are trending upward in recent periods")
                else:
                    insights.append("Sales show a decline in recent periods - attention needed")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append("Unable to generate insights due to data processing error")
        
        return insights
