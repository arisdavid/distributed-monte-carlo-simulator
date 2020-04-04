import time
from quantmodels.market_risk_models import geometric_brownian_motion


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


if __name__ == "__main__":
    # Input Parameters
    num_simulations = 100000000 # 1 MILLION
    starting_value = 100
    mu = 0.18
    sigma = 0.12
    forecast_period_in_days = 365
    num_trading_days = 250

    start_time = time.time()
    asset_paths = monte_carlo_simulation(num_simulations,
                                         geometric_brownian_motion,
                                         starting_value=starting_value,
                                         mu=mu,
                                         sigma=sigma,
                                         forecast_period_in_days=forecast_period_in_days,
                                         num_trading_days=num_trading_days)

    print(next(asset_paths))
    print(f"{(time.time() - start_time)} seconds")