# Multi-Agent System Reflection Report

## 1. How the System Works

The system is organized around three main agents and a central orchestrator:

- **Inventory Agent**: Checks stock, suggests alternatives if items are low, and estimates delivery dates.
- **Quoting Agent**: Generates customer quotes, ensuring accurate pricing and applying discounts.
- **Ordering Agent**: Finalizes orders, records transactions, and updates inventory and cash balances.

The **orchestrator** coordinates everything. It receives customer requests, delegates tasks to the appropriate agents, collects their responses, and returns a clear, customer-friendly reply. This modular design allows for easy addition of new agents in the future.

Customer request → Inventory check → Quote generation → Order finalization → Response

## 2. What We Learned from the Test Results

[See test results.](results/test_results.csv)  
Testing with sample requests (`test_results.csv`) revealed:

- **Inventory handling works well**: Orders that couldn't be fulfilled due to stock shortages were clearly flagged (e.g., requests 6, 11, 20).
- **Quoting is accurate**: Prices, discounts, and totals matched expectations (e.g., requests 4, 13).
- **Transactions are properly recorded**: Each order received a unique transaction ID, ensuring nothing was lost or overwritten (e.g., requests 2, 9, 10).
- **Consistent state tracking**: Cash balances and inventory values updated correctly after each order.

Overall, the system handled both normal and edge cases smoothly, providing clear and actionable responses.

## 3. Ideas to Make It Better

- **Smarter Inventory Management**: Implement demand prediction and prioritized reordering to avoid stockouts of popular items.
- **Better Customer Communication**: Provide structured summaries or JSON outputs for easier integration with other tools (e.g., websites, dashboards).
- **Dynamic Pricing and Discounts**: Adjust quotes automatically based on stock levels, seasonality, or customer type to optimize revenue.
- **Faster Processing**: Enable parallel processing of multiple requests while maintaining correct inventory and cash updates.
