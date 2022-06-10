from app.middleware.trading_metadata import historical_trading_metadata_middleware

# We only store the endpoints that are heavily rate limited
plugin_metadata_producer = {
    '/api/trading/historical': lambda job_params: historical_trading_metadata_middleware(job_params),
    '/api/twitter/followings': lambda x: True,
    '/api/twitter/followers': lambda x: True,
    "/api/agriculture/ethanolprod": lambda x: True,
    "/api/agriculture/ethanolstock": lambda x: True,
    "/api/agriculture/cropreports": lambda x: True,
}
