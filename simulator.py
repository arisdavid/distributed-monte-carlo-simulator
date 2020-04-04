import argparse
import logging
import uuid

from workermanager.worker_manager import WorkerManager

logging.basicConfig(level=logging.INFO)


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


def main(
    namespace,
    num_simulations,
    starting_value,
    mu,
    sigma,
    forecast_period_in_days,
    num_trading_days,
):

    # Max Simulations Per Pod
    partition = 50_000

    q = 1
    r = 0
    if num_simulations > partition:
        q, r = divmod(num_simulations, partition)

    num_workers = q
    logging.info(
        f"App will create {num_workers} pod(s) to handle {num_simulations} simulations."
    )

    # Spin up worker pods
    container_parameters = dict(
        num_simulations=partition,
        starting_value=starting_value,
        mu=mu,
        sigma=sigma,
        forecast_period=forecast_period_in_days,
        num_trading_days=num_trading_days,
    )

    worker_obj = WorkerManager(namespace=namespace)

    # Delete old pods
    worker_obj.delete_previous_pods()

    for worker in range(num_workers):

        worker_obj.pod_id = uuid.uuid4()
        worker_obj.container_parameters = container_parameters
        worker_obj.pod_number = worker + 1
        worker_obj.launch_worker()


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Monte Carlo Simulator")
    parser.add_argument("namespace", help="Kubernetes cluster namespace", type=str)
    parser.add_argument("num_simulations", help="Number of simulations", type=int)
    parser.add_argument("starting_value", help="Starting value", type=float)
    parser.add_argument("mu", help="Expected annual return", type=float)
    parser.add_argument("sigma", help="Expected annual volatility", type=float)
    parser.add_argument("forecast_period", help="Forecast period in days", type=int)
    parser.add_argument(
        "num_trading_days", help="Number of trading days in year", type=int
    )

    args = parser.parse_args()

    main(
        args.namespace,
        args.num_simulations,
        args.starting_value,
        args.mu,
        args.sigma,
        args.forecast_period,
        args.num_trading_days,
    )
