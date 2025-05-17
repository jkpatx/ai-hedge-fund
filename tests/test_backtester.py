from src.backtester import Backtester


def create_backtester(cash=1000.0, margin=0.0):
    return Backtester(
        agent=lambda **kwargs: None,
        tickers=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-01-31",
        initial_capital=cash,
        initial_margin_requirement=margin,
    )


def test_execute_trade_buy_and_sell():
    bt = create_backtester()

    qty = bt.execute_trade("AAPL", "buy", 10, 10.0)
    assert qty == 10
    assert bt.portfolio["cash"] == 900.0
    pos = bt.portfolio["positions"]["AAPL"]
    assert pos["long"] == 10
    assert pos["long_cost_basis"] == 10.0

    qty = bt.execute_trade("AAPL", "sell", 5, 15.0)
    assert qty == 5
    assert bt.portfolio["cash"] == 975.0
    assert pos["long"] == 5
    assert bt.portfolio["realized_gains"]["AAPL"]["long"] == 25.0


def test_execute_trade_short_and_cover():
    bt = create_backtester(margin=0.5)

    qty = bt.execute_trade("AAPL", "short", 5, 10.0)
    assert qty == 5
    pos = bt.portfolio["positions"]["AAPL"]
    assert pos["short"] == 5
    assert pos["short_cost_basis"] == 10.0
    assert bt.portfolio["cash"] == 1025.0
    assert bt.portfolio["margin_used"] == 25.0

    qty = bt.execute_trade("AAPL", "cover", 3, 8.0)
    assert qty == 3
    assert pos["short"] == 2
    assert bt.portfolio["cash"] == 1016.0
    assert bt.portfolio["margin_used"] == 10.0
    assert bt.portfolio["realized_gains"]["AAPL"]["short"] == 6.0
