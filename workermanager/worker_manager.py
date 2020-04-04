import logging

from kubernetes import client, config

logging.basicConfig(level=logging.INFO)

config.load_kube_config()


class WorkerManager:

    _container_image = "monte-carlo-simulator:latest"
    _pod_labels = {"name": "monte-carlo-simulator", "type": "pod"}

    def __init__(self, namespace):

        self.namespace = namespace

        # Pod parameters
        self._pod_number = None
        self._pod_id = None

        # Container parameters
        self.container_parameters = None

        # Kubernetes API
        self.batch_api = client.BatchV1Api()
        self.core_api = client.CoreV1Api()

    @property
    def pod_number(self):
        return self._pod_number

    @pod_number.setter
    def pod_number(self, n):
        self._pod_number = n

    @property
    def pod_id(self):
        return self._pod_id

    @pod_id.setter
    def pod_id(self, pid):
        self._pod_id = pid

    @property
    def container_parameters(self):
        return self._container_parameters

    @container_parameters.setter
    def container_parameters(self, params):
        self._container_parameters = params

    def create_container(self):
        label = "monte-carlo-simulator"
        image_pull_policy = "Never"
        container = client.V1Container(name=label, image_pull_policy=image_pull_policy)
        container.args = [str(args) for args in self.container_parameters.values()]
        container.image = self._container_image

        return container

    def create_pod_template(self):

        metadata = client.V1ObjectMeta(
            name=f"worker-pod{self.pod_number}-{self.pod_id}", labels=self._pod_labels
        )
        pod_template = client.V1PodTemplateSpec(metadata=metadata)
        pod_template.spec = client.V1PodSpec(
            containers=[self.create_container()], restart_policy="Never"
        )

        return pod_template

    def create_job(self):
        metadata = client.V1ObjectMeta(
            name=f"worker-pod{self.pod_number}-{self.pod_id}",
            labels={"name": "monte-carlo-simulator", "type": "job"},
        )

        job = client.V1Job(
            spec=client.V1JobSpec(backoff_limit=0, template=self.create_pod_template()),
            metadata=metadata,
            kind="Job",
            api_version="batch/v1",
        )

        return job

    def launch_worker(self):
        batch_api = client.BatchV1Api()
        batch_api.create_namespaced_job(self.namespace, self.create_job())
        logging.info(f"Pod with id {self.pod_id} launched.")

    def delete_previous_pods(self):

        """ Delete pods that succeeded previously """
        pods = self.core_api.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=f"name={self._pod_labels.get('name')}",
        )

        for pod in pods.items:
            if pod.status.phase == "Succeeded":
                logging.info(f"Deleting old pod {pod.metadata.name}")
                self.core_api.delete_namespaced_pod(
                    name=pod.metadata.name, namespace=self.namespace
                )
