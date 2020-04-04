## Introduction
Distributing Monte Carlo Simulator jobs across multiple Kubernetes worker (ephemeral pods). 
Partition default is currently set to 50,000 simulations. 

#### Screenshots
![Image of K9s](https://github.com/arisdavid/distributed-monte-carlo-simulator/blob/master/static/img/mcgbm.png)
 

## Local Development

For local development and testing setup a Kubernetes cluster using minikube. 
The minikube cluster is where the python apps, redis and kafka server will be deployed.

https://kubernetes.io/docs/setup/learning-environment/minikube/ 

Launch a minikube cluster using the following command:

``` 
minikube start 
```

Create a namespace within the cluster called k8demo

``` 
minikube create namespace <namespace_name>
```

Minikube defaults to default namespace. Set namespace context to k8demo

```
kubectl config set-context $(kubectl config current-context) --namespace=<namespace_name>
```

Ensure you're inside the Kubernetes environment as this is where the images will be built
``` eval $(minikube docker-env) ```



### Build the Docker Image (inside minikube)
```
docker build -t monte-carlo-simulator:latest -f ./montecarlosimulator/Dockerfile montecarlosimulator
```

### How to execute
```
python simulator.py <namespace_name> <num_simulations> <starting_value> <mu> <sigma> <forecast_period> <num_trading_days>

```

Example:
```
namespace="k8demo"
num_simulations=100000
starting_value=200
mu=0.2
sigma=0.18
forecast_period=365
num_trading_days=250
```

CLI: 
```
python3 simulator.py k8demo 100000 200 0.2 0.18 365 250

```