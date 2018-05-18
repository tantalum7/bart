
# Library imports
import v20


class Trade(object):

    def __init__(self):
        self._v20_trade = None

    @property
    def id(self):
        return self._v20_trade.id

    @property
    def quantity(self):
        return self._v20_trade.currentUnits

    @property
    def instrument(self):
        return self._v20_trade.instrument

    @property
    def open_time(self):
        return self._v20_trade.openTime

    @property
    def price(self):
        return self._v20_trade.price

    @property
    def stop_loss_price(self):
        return self._v20_trade.stopLossOrder.price

    @property
    def take_profit_price(self):
        return self._v20_trade.takeProfitOrder.price

    @property
    def current_state(self):
        return self._v20_trade.state