import logging
import requests
from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement, convert_errors

app = Flask(__name__)
ask = Ask(app, "/")
# logger = logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# APIs
cmc_base_url_api = 'https://api.coinmarketcap.com/v1/'
ccp_url_api = 'https://min-api.cryptocompare.com/data/'

# ---------------------- Helper functions ------------------------------------ #

def replace_decimal_point(number):

    return str(number).replace('.', ',')


@app.template_filter()
def humanize_big_number(big_number):

    if big_number >= 10**12:

        formatted_number = replace_decimal_point(round(big_number/10**12))

        return formatted_number + ' ' + 'Billionen'

    if big_number >= 10**9:

        formatted_number = replace_decimal_point(round(big_number/10**9))

        return formatted_number + ' ' + 'Milliarden'

    if big_number >= 10**6:

        formatted_number = replace_decimal_point(round(big_number/10**6))

        return formatted_number + ' ' + 'Millionen'

    if big_number >= 10**3:

        formatted_number = replace_decimal_point(round(big_number/10**3))

        return formatted_number + ' ' + 'Tausend'


@app.template_filter()
def humanize_percent(percent):

    percent = float(percent)

    preposition = 'Plus von ' if percent > 0 else 'Minus von '

    percent = abs(percent)

    percent = replace_decimal_point(percent)

    return preposition + percent + ' Prozent'

@app.template_filter()
def humanize_price(price, currency='eur'):

    price = str(round(float(price),2))

    if currency == 'eur':

        return price[:-3] + ' Euro und ' + price[-2:] + ' Cent'

    if currency == 'usd':

        return price[:-3] + ' US Dollar und ' + price[-2:] + ' Dollar Cent'


# ----------------------- Intents -------------------------------------------- #

@ask.launch
def launch():

    welcome_text = render_template('welcome')

    return question(welcome_text).reprompt(welcome_text).simple_card('Hallo', welcome_text)


@ask.intent('get_market_update')
def get_market_update():

    api1 = cmc_base_url_api + 'global/?convert=EUR'
    api2 = cmc_base_url_api + 'ticker/?convert=EUR&limit=3'

    try:
        
        # Retrieving global info
        r = requests.get(api1).json()

        # Retrieving top 3 coins
        coins = requests.get(api2).json()

    except:

        return statement(api_error).simple_card('Fehler bei Datenquelle', api_error)

    # Collecting important global info
    global_info = {}

    global_info['mkt_cap'] = r['total_market_cap_eur']

    btc_dom = r['bitcoin_percentage_of_market_cap']
    global_info['btc_dom'] = replace_decimal_point(btc_dom)

    # Generate outputs
    speech_output = render_template('market_update', global_info=global_info,
                                    coins=coins)

    help_text = render_template('help')

    return question(speech_output).reprompt(help_text).simple_card('Crypto Markt Update', 
                                                speech_output)


@ask.intent('get_price')
def get_price(coin):

    if convert_errors:

        return question('''Ich hab die Coin nicht verstanden. Kannst du bitte
                           nochmal alles wiederholen.''')

    api = cmc_base_url_api + 'ticker/{}/?convert=EUR'.format(coin.lower())
    json = requests.get(api).json()[0]

    speech_output = render_template('get_price', coin=coin, json=json)

    return statement(speech_output).simple_card('Marktpreis %s' % coin, speech_output)


    







'https://api.coinmarketcap.com/v1/ticker/?convert=EUR&limit=3'
ccp = 'price?fsym=ETH&tsyms=BTC,USD,EUR'
ccp2 = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=ETH&tsyms=BTC,USD,EUR&ts=1452680400&extraParams=your_app_name'

app.run(debug=True)