import os

import dotenv
from smolagents import CodeAgent, tool
from smolagents.models import LiteLLMModel

from tools_functions import (
    create_transaction,
    generate_financial_report,
    get_all_inventory,
    get_cash_balance,
    get_stock_level,
    get_supplier_delivery_date,
    search_quote_history,
)

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Shared model for orchestration meta-prompts
llm = LiteLLMModel(
    api_key=OPENAI_API_KEY,
    model_id=f"openai/{MODEL_NAME}",
    temperature=0.5,
)


@tool
def get_inventory_tool(as_of_date: str) -> dict[str, int]:
    """
    Return inventory snapshot as of a date.

    Args:
        as_of_date (str): Date in ISO format (yyyy-mm-dd).
    Returns:
        dict: Inventory levels for all items as of the date.
    """
    return get_all_inventory(as_of_date)


@tool
def get_stock_tool(item_name: str, as_of_date: str) -> list[dict]:
    """
    Return stock level for an item as of a date.

    Args:
        item_name (str): Name of the item.
        as_of_date (str): Date in ISO format (yyyy-mm-dd).
    Returns:
        list[dict]: Stock level information for the item as of the date.
    """
    return get_stock_level(item_name, as_of_date).to_dict(orient="records")


@tool
def search_quotes_tool(search_terms: list[str], limit: int = 5) -> list[dict]:
    """
    Search historical quotes matching any of the search terms.

    Args:
        search_terms (list[str]): list of terms to search for.
        limit (int, optional): Max number of results to return. Default is 5.
    Returns:
        list[dict]: list of matching quotes with details.
    """
    return search_quote_history(search_terms, limit)


@tool
def create_transaction_tool(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: str,
) -> int:
    """
    Create a transaction record in the database.

    Args:
        item_name (str): Name of the item.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units.
        price (float): Total price of the transaction.
        date (str): Date of the transaction (ISO format).

    Returns:
        int: ID of the created transaction.
    """
    return create_transaction(item_name, transaction_type, quantity, price, date)


@tool
def estimate_delivery_tool(input_date: str, quantity: int) -> str:
    """
    Estimate supplier delivery date based on order quantity and input date.

    Args:
        input_date (str): Date in ISO format (yyyy-mm-dd).
        quantity (int): Number of units in the order.
    Returns:
        str: Estimated delivery date in ISO format (yyyy-mm-dd).
    """
    return get_supplier_delivery_date(input_date, quantity)


@tool
def get_cash_tool(as_of_date: str) -> float:
    """
    Return cash balance as of a date.

    Args:
        as_of_date (str): Date in ISO format (yyyy-mm-dd).
    Returns:
        float: Cash balance as of the date.
    """
    return get_cash_balance(as_of_date)


@tool
def financial_report_tool(as_of_date: str) -> dict:
    """
    Generate a financial report as of a date.

    Args:
        as_of_date (str): Date in ISO format (yyyy-mm-dd).
    Returns:
        dict: Financial report including cash, inventory value, total assets, and summaries.
    """
    return generate_financial_report(as_of_date)


inventory_agent = CodeAgent(
    name="InventoryAgent",
    model=llm,
    tools=[get_inventory_tool, get_stock_tool, estimate_delivery_tool],
    description="Performs inventory checks, recommends reorders and estimates delivery.",
    max_steps=5,
)

quoting_agent = CodeAgent(
    name="QuotingAgent",
    model=llm,
    tools=[search_quotes_tool, get_inventory_tool, get_stock_tool],
    description=(
        "Generates quotes from customer request; consults history and inventory to set price and discounts."
    ),
    max_steps=6,
)

ordering_agent = CodeAgent(
    name="OrderingAgent",
    model=llm,
    tools=[
        create_transaction_tool,
        get_cash_tool,
        estimate_delivery_tool,
        financial_report_tool,
    ],
    description="Finalizes sales, writes transactions and returns order confirmation with delivery ETA.",
    max_steps=6,
)
