import logging
import requests
from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

app = Flask(__name__)
ask = Ask(app, "/")
logger = logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# APIs
cmc_url_api = 'https://api.coinmarketcap.com/v1/'
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

    preposition = 'plus von ' if percent > 0 else 'minus von '

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

    api = cmc_url_api + 'global/?convert=EUR'
    r = requests.get(api).json()

    global_info = {}

    # Marketcap
    global_info['mkt_cap'] = r['total_market_cap_eur']

    # Bitcoin dominance
    btc_dom = r['bitcoin_percentage_of_market_cap']
    global_info['btc_dom'] = replace_decimal_point(btc_dom)

    # Top 3 Coins
    api = cmc_url_api + 'ticker/?convert=EUR&limit=3'
    coins = requests.get(api).json()

    speech_output = render_template('market_update', global_info=global_info,
                                    coins=coins)

    help_text = render_template('help')

    return question(speech_output).reprompt(help_text).simple_card('Crypto Markt Update', 
                                                speech_output)


app.run(debug=True)