import math
import numpy as np
import numpy.matlib as ml


def geometric_brownian_motion(allow_negative=False, **kwargs):

    """
    Geometric Brownian Motion
    Step 1 - Calculate the Deterministic component - drift
    Alternative drift 1 - supporting random walk theory
    drift = 0
    Alternative drift 2 -
    drift = risk_free_rate - (0.5 * sigma**2)
    :return: asset path

    """

    starting_value = kwargs.get('starting_value')
    mu = kwargs.get('mu')
    sigma = kwargs.get('sigma')
    num_trading_days = kwargs.get('num_trading_days')
    num_per = kwargs.get('forecast_period_in_days')

    # Calculate Drift
    mu = mu / num_trading_days
    sigma = sigma / math.sqrt(num_trading_days)  # Daily volatility
    drift = mu - (0.5 * sigma ** 2)

    # Calculate Random Shock Component
    random_shock = np.random.normal(0, 1, (1, num_per))
    log_ret = drift + (sigma * random_shock)

    compounded_ret = np.cumsum(log_ret, axis=1)
    asset_path = starting_value + (starting_value * compounded_ret)

    # Include starting value
    starting_value = ml.repmat(starting_value, 1, 1)
    asset_path = np.concatenate((starting_value, asset_path), axis=1)

    if allow_negative:
        asset_path *= (asset_path > 0)

    return asset_path.mean(axis=0)
