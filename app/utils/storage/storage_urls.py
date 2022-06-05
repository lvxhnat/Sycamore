from datetime import datetime


def trading_metadata_storage_url(
        job_params):
    return f"""{'/api/trading/historical'.strip('/api/')}/{job_params['instrument']}/{job_params['ticker']}/{job_params['resolution']}/{job_params['from_date']}/{job_params['to_date']}/"""


def twitter_followers_storage_url(
    num_users): return f"""{'/api/twitter/followers'.strip('/api/')}/{datetime.today().strftime("%Y-%m-%d")}/{num_users}/"""


def twitter_followings_storage_url(
    num_users): return f"""{'/api/twitter/followings'.strip('/api/')}/{datetime.today().strftime("%Y-%m-%d")}/{num_users}/"""


def ethanol_prod_storage_url():
    return f"""{'/api/agriculture/ethanolprod'.strip('/api/')}/{datetime.today().strftime("%Y-%m-%d")}/"""


def ethanol_stock_storage_url():
    return f"""{'/api/agriculture/ethanolstock'.strip('/api/')}/{datetime.today().strftime("%Y-%m-%d")}/"""
