from trader.trader import Trader
from v20.pricing import Price

if __name__ == "__main__":

    import time

    trader = Trader()

    stream = trader.test_stream("XAU_CAD,NZD_SGD,CAD_SGD,USD_NOK")

    """
    for x in range(100):
        g = next(stream)
        if isinstance(g[1], Price):
            print("{}: {}".format(g[1].instrument, g[1].closeoutBid))
        time.sleep(0.25)
    """

    for x in range(100):
        print("{}: {}".format(g[1].instrument, g[1].closeoutBid))

        
    print("done")