import argparse
import logging
import math

import numpy as np
import numpy.matlib as ml

logging.basicConfig(level=logging.INFO)


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

    starting_value = kwargs.get("starting_value")
    mu = kwargs.get("mu")
    sigma = kwargs.get("sigma")
    num_trading_days = kwargs.get("num_trading_days")
    num_per = kwargs.get("forecast_period_in_days")

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
        asset_path *= asset_path > 0

    return asset_path.mean(axis=0)


def monte_carlo_simulation(num_sims, model, **kwargs):
    """
    Monte Carlo Simulator
    :param num_sims: Number of iterations
    :param model: function to be iterated
    :param kwargs: keyword arguments
    :return: yield generator object
    """

    for n_sim in range(num_sims):
        yield model(**kwargs)


def main():

    parser = argparse.ArgumentParser("Monte Carlo Simulator")
    parser.add_argument("num_simulations", help="Number of simulations", type=int)
    parser.add_argument("starting_value", help="Starting value", type=float)
    parser.add_argument("mu", help="Expected annual return", type=float)
    parser.add_argument("sigma", help="Expected annual volatility", type=float)
    parser.add_argument("forecast_period", help="Forecast period in days", type=int)
    parser.add_argument(
        "num_trading_days", help="Number of trading days in year", type=int
    )

    args = parser.parse_args()
    asset_paths = monte_carlo_simulation(
        args.num_simulations,
        geometric_brownian_motion,
        starting_value=args.starting_value,
        mu=args.mu,
        sigma=args.sigma,
        forecast_period_in_days=args.forecast_period,
        num_trading_days=args.num_trading_days,
    )

    for asset_path in asset_paths:
        curve = +asset_path

    return curve


if __name__ == "__main__":

    _curve = main()

    print(_curve)
