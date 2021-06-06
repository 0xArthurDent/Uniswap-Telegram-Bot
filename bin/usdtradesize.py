def usdtradesize(usdtotal, threshold=1000):
    # Format the wallet address as 0x..{Last ndigits characters}
    div = int(-(-usdtotal//threshold))
        
    return div
