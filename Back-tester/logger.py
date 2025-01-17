from typing import Dict, List, Tuple, Any
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade, Product, Position, Listing, ProsperityEncoder
import json


class Logger:
    # Set this to true, if u want to create
    # local logs
    local: bool
    # this is used as a buffer for logs
    # instead of stdout
    local_logs: "dict[int, str]" = {}

    def __init__(self, local=False, our_log_only=True, print_output=False) -> None:
        self.logs = ""
        self.local = local
        self.our_log_only = our_log_only
        self.print_output = print_output

    def testlogger_print(self, string: str) -> None:
        self.logs += string + "\n"

    # def testlogger_print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
    #     self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: "dict[Symbol, list[Order]]") -> None:
        if not self.our_log_only:
            output = json.dumps({
                "state": state,
                "orders": orders,
                "logs": self.logs,
            }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True)
        else:
            output = self.logs
        self.local_logs[state.timestamp] = output
        if self.print_output:
            print(output)

        self.logs = ""

    def compress_state(self, state: TradingState) -> "dict[str, Any]":
        listings = []
        for listing in state.listings.values():
            listings.append(
                [listing["symbol"], listing["product"], listing["denomination"]])

        order_depths = {}
        for symbol, order_depth in state.order_depths.items():
            order_depths[symbol] = [
                order_depth.buy_orders, order_depth.sell_orders]

        return {
            "t": state.timestamp,
            "l": listings,
            "od": order_depths,
            "ot": self.compress_trades(state.own_trades),
            "mt": self.compress_trades(state.market_trades),
            "p": state.position,
            "o": state.observations,
        }

    def compress_trades(self, trades: "dict[Symbol, list[Trade]]") -> "list[list[Any]]":
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.buyer,
                    trade.seller,
                    trade.price,
                    trade.quantity,
                    trade.timestamp,
                ])

        return compressed

    def compress_orders(self, orders: "dict[Symbol, list[Order]]") -> "list[list[Any]]":
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    # def run(self, state: TradingState):
    #     """
    #     Only method required. It takes all buy and sell orders for all symbols as an input,
    #     and outputs a list of orders to be sent
    #     """
    #     # Initialize the method output dict as an empty dict
    #     result = {}
    #     self.logger.flush(state, result)
    #     return result
