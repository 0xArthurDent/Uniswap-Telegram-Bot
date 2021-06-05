def formataddress(address:str,ndigits=4):
    # Format the wallet address as 0x..{Last ndigits characters}
    lastchars = str(address)[-ndigits:]
    output = "0x.."+ lastchars
    
    return output