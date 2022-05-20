class RateLimitException(Exception):
    def __str__(self):
        return "Rate limit errored out."
