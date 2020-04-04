import time
from montecarlosimulator.market_risk_models import geometric_brownian_motion
import uuid
from workermanager.worker_manager import WorkerManager


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
    namespace = "k8demo"
    partition = 10_000

    # Input Parameters
    num_simulations = 22_000  # 1 MILLION
    starting_value = 500
    mu = 0.18
    sigma = 0.12
    forecast_period_in_days = 365
    num_trading_days = 250

    container_parameters = dict(
                num_simulations=num_simulations,
                starting_value=starting_value,
                mu=0.18,
                sigma=sigma,
                forecast_period=forecast_period_in_days,
                num_trading_days=num_trading_days
            )
    q = 0
    r = 0
    if num_simulations > partition:
        q, r = divmod(num_simulations, partition)

    num_workers = q
    if num_workers > 0:
        # Spin up a worker pod
        for worker in range(num_workers):
            worker_obj = WorkerManager(namespace=namespace,
                                       pod_id=uuid.uuid4(),
                                       container_parameters=container_parameters)
            worker_obj.launch_worker()

    asset_paths = monte_carlo_simulation(num_simulations,
                                         geometric_brownian_motion,
                                         starting_value=starting_value,
                                         mu=mu,
                                         sigma=sigma,
                                         forecast_period_in_days=forecast_period_in_days,
                                         num_trading_days=num_trading_days)

    for asset_path in asset_paths:
        total = + asset_path

    return total
    print(f"{(time.time() - start_time)} seconds")


if __name__ == "__main__":
    a = main()
