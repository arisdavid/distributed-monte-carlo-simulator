from kubernetes import client, config

config.load_kube_config()


class WorkerManager:

    __container_image = "monte-carlo-simulator:latest"

    def __init__(self, namespace, pod_id, container_parameters):
        self.container_parameters = container_parameters
        self.namespace = namespace
        self.pod_id = pod_id
        self.metadata = client.V1ObjectMeta(
            name=f"worker-{pod_id}",
            labels={"name": "monte-carlo-simulator", "type": "worker"},
        )

    def create_container(self):
        label = "monte-carlo-simulator"
        image_pull_policy = "Never"
        container = client.V1Container(name=label, image_pull_policy=image_pull_policy)
        container.args = [str(args) for args in self.container_parameters.values()]
        container.image = self.__container_image

        return container

    def create_pod_template(self):
        pod_template = client.V1PodTemplateSpec(metadata=self.metadata)
        pod_template.spec = client.V1PodSpec(
            containers=[self.create_container()], restart_policy="Never"
        )

        return pod_template

    def create_job(self):
        job = client.V1Job(
            spec=client.V1JobSpec(backoff_limit=0, template=self.create_pod_template()),
            metadata=self.metadata,
            kind="Job",
            api_version="batch/v1",
        )

        return job

    def launch_worker(self):
        batch_api = client.BatchV1Api()
        batch_api.create_namespaced_job(self.namespace, self.create_job())
