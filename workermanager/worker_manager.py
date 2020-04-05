import logging

from kubernetes import client, config

logging.basicConfig(level=logging.INFO)

config.load_kube_config()


class WorkerManager:

    _container_image = "monte-carlo-simulator:latest"
    _pod_labels = {"name": "monte-carlo-simulator", "type": "pod"}
    _job_labels = {"job_name": "monte-carlo-simulator", "type": "job"}

    def __init__(self, namespace):

        self.namespace = namespace

        # Parameters
        self._pod_parameters = None
        self._container_parameters = None
        self._job_parameters = None

        # Kubernetes API
        self.batch_api = client.BatchV1Api()
        self.core_api = client.CoreV1Api()

    @property
    def job_parameters(self):
        return self._job_parameters

    @job_parameters.setter
    def job_parameters(self, params):
        self._job_parameters = params

    @property
    def pod_parameters(self):
        return self._pod_parameters

    @pod_parameters.setter
    def pod_parameters(self, params):
        self._pod_parameters = params

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

        pod_metadata = client.V1ObjectMeta(
            name=f"mc-pod-{self._pod_parameters['pod_number']}-{self._pod_parameters['pod_id']}",
            labels=self._pod_labels,
        )
        pod_template = client.V1PodTemplateSpec(metadata=pod_metadata)
        pod_template.spec = client.V1PodSpec(
            containers=[self.create_container()], restart_policy="Never"
        )

        return pod_template

    def create_job(self):

        job_metadata = client.V1ObjectMeta(
            name=f"mc-job-{self._job_parameters['job_number']}-{self._job_parameters['job_id']}",
            labels=self._job_labels,
        )

        job = client.V1Job(
            spec=client.V1JobSpec(backoff_limit=0, template=self.create_pod_template()),
            metadata=job_metadata,
            kind="Job",
            api_version="batch/v1",
        )

        return job

    def launch_pod(self):

        batch_api = client.BatchV1Api()
        batch_api.create_namespaced_job(self.namespace, self.create_job())
        logging.info(f"Launching pod number {self._pod_parameters['pod_number']}.")

    def remove_old_jobs(self):

        """ Delete old jobs """
        jobs = self.batch_api.list_namespaced_job(namespace=self.namespace)

        for job in jobs.items:
            if job.status.succeeded:
                self.batch_api.delete_namespaced_job(
                    namespace=self.namespace, name=job.metadata.name,
                )

    def remove_old_pods(self):

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
