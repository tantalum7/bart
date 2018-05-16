from trader.trader import Trader
from trader.price_cache import LivePriceCache

if __name__ == "__main__":

    import time

    trader = Trader()

    lpc = LivePriceCache(trader._cfg, {"XAU_CAD": ["closeoutBid"], "NZD_SGD": ["closeoutBid"]})

    """
    stream = trader.test_stream("XAU_CAD,NZD_SGD,CAD_SGD,USD_NOK")
    for x in range(100):
        g = next(stream)
        if isinstance(g[1], Price):
            print("{}: {}".format(g[1].instrument, g[1].closeoutBid))
        time.sleep(0.25)
    

    for x in range(100):
        print("{}: {}".format(g[1].instrument, g[1].closeoutBid))

    """

    while True:
        pass
    print("done")