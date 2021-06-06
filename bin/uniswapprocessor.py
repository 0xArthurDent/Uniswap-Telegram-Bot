import logging
import time
import bin.settings as settings
from bin.formataddress import formataddress
from bin.formatnumber import formatnumber
from bin.wallettostring import wallettostring
from bin.usdtradesize import usdtradesize
from api.etherscan.uniswaptransactionbatch import UniswapTransactionBatch
from api.etherscan.uniswaptransaction import UniswapTransaction
from api.etherscan.gettokenamount import gettokenamount
from api.telegram.telegramsendmessage import TelegramSendMessage

# Configure logging
logger = logging.getLogger(__name__)

class UniswapProcessor():
    def __init__(self):
        logger.info("Start Uniswap Processor")

    def process_uniswaptransactionbatch(self):
        # Get all transaction for the UniSwap address from the last processed
        # blocknumber
        logger.info("Start looking for a new Uniswap transaction batch")
        utb = UniswapTransactionBatch(settings.config.lastprocessedblocknumber)

        logger.info("Processing Uniswap transaction batch")
        # Foreach transaction has in the batch, get the information from the
        # transaction (amount, pair token, price etc. will be returned)
        for transactionhash in utb.transactionhashes:
            try:
                ut = UniswapTransaction(transactionhash)
            except:
                logger.warning("Transaction {} can't be processed".format(
                    transactionhash))
                continue

            # If wallet is None, skip to the next hash
            # Implemented for very rare transactions like (rare swap)
            # 0x02d3cd8e60ed3bac6bd32d75e32326d84ffdc38f1ab3d37c69127e050a07ac4c
            if ut.wallet == None:
                continue
            # Send message to active Telegram channels with the information
            # gathered earlier
            if ut.action == "Sold" or ut.action == "Bought":
                if ut.action == "Bought" and ut.usdpricetotal > 0:
                    actionicon = "\U0001f7e2"*(usdtradesize(ut.usdpricetotal))
                if ut.action == "Sold" and ut.usdpricetotal > 0:
                    actionicon = "\U0001f534"*(usdtradesize(ut.usdpricetotal))
                if ut.primarytokenamount > 0:
                    if ut.primarytokenamount > 0 and ut.primarytokenamount <=1000:
                        sizeicon = "\U0001f990" #shrimp
                    if ut.primarytokenamount > 1000 and ut.primarytokenamount <=3000:
                        sizeicon = "\U0001f980" #crab
                    if ut.primarytokenamount > 3000 and ut.primarytokenamount <=6000:
                        sizeicon = "\U0001f41f" #fish
                    if ut.primarytokenamount > 6000 and ut.primarytokenamount <=10000:
                        sizeicon = "\U0001f419" #octopus
                    if ut.primarytokenamount > 10000 and ut.primarytokenamount <=20000:
                        sizeicon = "\U0001f42c" #dolphin
                    if ut.primarytokenamount > 20000 and ut.primarytokenamount <=50000:
                        sizeicon = "\U0001f988" #shark
                    if ut.primarytokenamount > 50000 and ut.primarytokenamount <=200000:
                        sizeicon = "\U0001f40b" #whale
                    if ut.primarytokenamount > 200000:
                        sizeicon = "\U0001f433" #blue whale
                walletstring = wallettostring(ut.wallet)
                shortwallet = formataddress(walletstring)
                exchange = "Uniswap \U0001f984" #uniswap
                msg = (
                "<b>Last Price: ${usdpricepertoken} / {pairtokenpricept} {pairtokenname}</b>\n\n"
                "{actionicon}\n\n"
                "<a href=\"https://etherscan.io/address/{wallet}\">{shortwallet}</a> "
                "<b><a href=\"https://etherscan.io/tx/{txhash}\">{action}</a></b> "
                "<b>{primarytokenamount} {primarytokensymbol}</b> "
                "for <b>{pairtokenamount} {pairtokenname}</b> "
                "<i>(${usdpricetotal}</i> {sizeicon}) on "
                "<b><a href=\"https://v2.info.uniswap.org/token/{primarytokencontractaddress}\"> {exchange}</a></b>\n\n"
                "<b>Links:</b> "
                "<a href=\"https://etherscan.io/tx/{txhash}\">Tx</a> | "
                "<a href=\"https://v2.info.uniswap.org/pair/{uniswapaddress}\">Uni V2 LP</a> | "
                "<a href=\"https://behodler.io/\">Trade</a>\n\n"
                "Powered by <b><a href=\"https://behodler.io/\">Behodler Liquidity Protocol</a></b>"
                ).format(
                    action = ut.action,
                    laction = ut.action.lower(),
                    actionicon = actionicon,
                    primarytokenamount = formatnumber(ut.primarytokenamount),
                    primarytokenname = settings.config.primarytokenname,
                    primarytokensymbol = settings.config.primarytokensymbol,
                    pairtokenamount = formatnumber(ut.pairtokenamount),
                    pairtokenname = ut.pairtoken.tokenname,
                    pairtokeneurprice = formatnumber(ut.pairtoken.eurprice),
                    pairtokenusdprice = formatnumber(ut.pairtoken.usdprice),
                    eurpricetotal = formatnumber(ut.eurpricetotal),
                    usdpricetotal = formatnumber(ut.usdpricetotal),
                    txhash = ut.txhash,
                    blocknumber = ut.blocknumber,
                    eurpricepertoken= formatnumber(ut.eurpricepertoken),
                    usdpricepertoken= formatnumber(ut.usdpricepertoken),
                    pairtokenpricept = formatnumber(ut.pairtokenpricept,8),
                    wallet = wallettostring(ut.wallet),
                    uniswapaddress = settings.config.uniswapaddress,
                    shortwallet = shortwallet,
                    exchange = exchange,
                    primarytokencontractaddress = settings.config.primarytokencontractaddress,
                    sizeicon = sizeicon
                )
            elif ut.action == 'Liquidity Added' or \
                ut.action == 'Liquidity Removed':

                if ut.action == 'Liquidity Added' and ut.usdpricetotal > 0:
                    actionicon = "\U0001f4a7"*(usdtradesize(ut.usdpricetotal))
                if ut.action == 'Liquidity Removed' and ut.usdpricetotal > 0:
                    actionicon = "\U0001fa78"*(usdtradesize(ut.usdpricetotal))

                pairtokenatuniswap = gettokenamount(
                    settings.config.uniswapaddress,
                    ut.pairtoken.contractaddress
                )
                primarytokenatuniswap = gettokenamount(
                    settings.config.uniswapaddress,
                    settings.config.primarytokencontractaddress
                )
                walletstring = wallettostring(ut.wallet)
                shortwallet = formataddress(walletstring)
                exchange = "Uniswap \U0001f984" #uniswap
                msg = (
                 "<b>Last Price: ${usdpricepertoken} / {pairtokenpricept} {pairtokenname}</b>\n\n"
                "{actionicon}\n\n"
                "<a href=\"https://etherscan.io/address/{wallet}\">{shortwallet}</a> "
                "<b><a href=\"https://etherscan.io/tx/{txhash}\">{action}</a></b> "
                "<b>{primarytokenamount} {primarytokensymbol}</b> "
                "and <b>{pairtokenamount} {pairtokenname}</b> "
                "<i>(${usdpricetotal}</i> ) on "
                "<b><a href=\"https://v2.info.uniswap.org/token/{primarytokencontractaddress}\"> {exchange}</a></b>\n\n"
                "<b>{exchange} LP amounts:</b>\n"
                "Pooled {pairtokenname}: {pairtokenatuniswap}\n"
                "Pooled {primarytokensymbol}: {primarytokenatuniswap}"
                "\n\n<b>Links:</b> "
                "<a href=\"https://etherscan.io/tx/{txhash}\">Tx</a> | "
                "<a href=\"https://v2.info.uniswap.org/pair/{uniswapaddress}\">Uni V2 LP</a> | "
                "<a href=\"https://behodler.io/\">Trade</a>\n\n"
                "Powered by <b><a href=\"https://behodler.io/\">Behodler Liquidity Protocol</a></b>"
                ).format(
                    action = ut.action,
                    actionicon = actionicon,
                    primarytokenamount = formatnumber(ut.primarytokenamount),
                    primarytokensymbol = settings.config.primarytokensymbol,
                    pairtokenamount = formatnumber(ut.pairtokenamount),
                    pairtokenname = ut.pairtoken.tokenname,
                    eurpricetotal = formatnumber(ut.eurpricetotal * 2),
                    usdpricetotal = formatnumber(ut.usdpricetotal * 2),
                    txhash = ut.txhash,
                    blocknumber = ut.blocknumber,
                    wallet = wallettostring(ut.wallet),
                    pairtokenatuniswap = formatnumber(pairtokenatuniswap),
                    primarytokenatuniswap = formatnumber(primarytokenatuniswap),
                    uniswapaddress = settings.config.uniswapaddress,
                    shortwallet = shortwallet,
                    exchange = exchange,
                    primarytokencontractaddress = settings.config.primarytokencontractaddress,
                    eurpricepertoken= formatnumber(ut.eurpricepertoken),
                    usdpricepertoken= formatnumber(ut.usdpricepertoken),
                    pairtokenpricept = formatnumber(ut.pairtokenpricept,8)
                )

            for channel in settings.config.telegramactivatedchannels:
                TelegramSendMessage(channel,msg)

            # Change last blocknumber in settings file to last processed block
            # number + 1
            nextblocknumber = str((int(ut.blocknumber) + 1))
            settings.config.updateblocknumber(nextblocknumber)

    def start(self,pollinterval=60):
        logger.info("Starting Uniswap processor cycle "
        " with a poll interval of: {} seconds".format(pollinterval))
        while True:
            try:
                self.process_uniswaptransactionbatch()
                logger.info(("Uniswap processor cycle finished, waiting {} "
                "seconds").format(
                        pollinterval))
                time.sleep(pollinterval)
            except:
                logger.error("Uniswap Processor run failed")
                time.sleep(10)