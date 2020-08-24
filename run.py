from cbpro_bot.System.portfolio_management_system import PortfolioManagementSystem


"""
Create and run a portfolio management system.

Args:
    client (cbpro.authenticated_client): an authenticated client that can interact with the Coinbase Pro API
    crypto (str): id of crypto currency (e.g. 'BTC', 'ETH')
    cash (str): id of cash currency (e.g. 'USD', 'EUR')
    time_frame (int):
    system_id (int):
    system_label (str): descriptive name for the system
    buy_order_size (float):
    sell_order_size (float):
"""

PortfolioManagementSystem(crypto='BTC',
                          cash='EUR',
                          time_frame=60,
                          system_id=1,
                          system_label='BTC_Bot',
                          buy_order_size=10.0,
                          sell_order_size=0.001
                          )