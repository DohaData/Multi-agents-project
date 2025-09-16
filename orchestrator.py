from typing import Union

from entities import ErrorResponse, QuoteRequestSample


class MultiAgentOrchestrator:
    """
    A true multi-agent orchestrator that coordinates inventory, quoting, and ordering
    in a pipeline rather than one single agent holding all tools.
    """

    def __init__(self, inventory_agent, quoting_agent, ordering_agent):
        self.inventory_agent = inventory_agent
        self.quoting_agent = quoting_agent
        self.ordering_agent = ordering_agent

    def process_request(self, request: QuoteRequestSample) -> Union[str, ErrorResponse]:
        """
        Pipeline:
          1. Use InventoryAgent to check availability
          2. Use QuotingAgent to prepare a quote
          3. Use OrderingAgent to finalize an order
        """

        try:
            inv_prompt = (
                f"You are InventoryAgent working at Munder Difflin.\n"
                f"Check if requested items are available.\n\n"
                f"If the items in inventory lack specifics such as color or style or format A3-A4,"
                f" assume reasonable defaults close to the requested in the db.\n\n"
                f"Customer request: {request.request}\n"
                f"Need size: {request.need_size}\n"
                f"Event: {request.event}\n"
                f"Date: {request.request_date.date().isoformat()}"
            )
            inv_result = self.inventory_agent.run(inv_prompt)
            if inv_result is None or str(inv_result).strip().upper().startswith(
                "ERROR"
            ):
                return ErrorResponse(
                    error=f"Inventory check failed: {inv_result}", context="inventory"
                )

            quote_prompt = (
                f"You are QuotingAgent working at Munder Difflin.\n"
                f"Generate a professional price quote based on the inventory results.\n\n"
                f"Apply discounts for large orders or special events.\n\n"
                f"Inventory info: {inv_result}\n"
                f"Customer request: {request.request}\n"
                f"Job: {request.job}, Size: {request.need_size}, Event: {request.event}\n"
                f"Date: {request.request_date.date().isoformat()}"
            )
            quote_result = self.quoting_agent.run(quote_prompt)
            if quote_result is None or str(quote_result).strip().upper().startswith(
                "ERROR"
            ):
                return ErrorResponse(
                    error=f"Quote generation failed: {quote_result}", context="quoting"
                )

            order_prompt = (
                f"You are OrderingAgent working at Munder Difflin.\n"
                f"Finalize the order assuming customer accepts the quote.\n\n"
                f"Quote details: {quote_result}\n"
                f"Date: {request.request_date.date().isoformat()}"
            )
            order_result = self.ordering_agent.run(order_prompt)
            if order_result is None or str(order_result).strip().upper().startswith(
                "ERROR"
            ):
                return ErrorResponse(
                    error=f"Order finalization failed: {order_result}",
                    context="ordering",
                )

            # SUCCESS
            return str(order_result).strip()

        except Exception as e:
            return ErrorResponse(error=str(e), context="orchestrator.exception")
