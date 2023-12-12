from pydantic.v1 import root_validator
import time
from langchain.embeddings import SagemakerEndpointEmbeddings
from typing import Dict, List


class SagemakerEndpointEmbeddingsKeys(SagemakerEndpointEmbeddings):
    aws_key: str = ""
    aws_secret: str = ""

    @root_validator(skip_on_failure=True)
    def validate_environment(cls, values: Dict) -> Dict:
        import boto3

        session = boto3.Session(
        aws_access_key_id=values["aws_key"],
        aws_secret_access_key=values["aws_secret"]
        )

        values["client"] = session.client(
        "sagemaker-runtime", region_name=values["region_name"]
        )

        return values

    def embed_documents(
        self, texts: List[str], chunk_size: int = 32
    ) -> List[List[float]]:
        """Compute doc embeddings using a SageMaker Inference Endpoint.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size defines how many input texts will
                be grouped together as request. If None, will use the
                chunk size specified by the class.


        Returns:
            List of embeddings, one for each text.
        """
        results = []
        _chunk_size = len(texts) if chunk_size > len(texts) else chunk_size
        for i in range(0, len(texts), _chunk_size):
            response = self._embedding_func(texts[i:i + _chunk_size])
            results.extend(response)
        return results

    def _embedding_func(self, texts: List[str]) -> List[List[float]]:
        """Call out to SageMaker Inference embedding endpoint."""
        # replace newlines, which can negatively affect performance.
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        _model_kwargs = self.model_kwargs or {}
        _endpoint_kwargs = self.endpoint_kwargs or {}

        body = self.content_handler.transform_input(texts, _model_kwargs)
        content_type = self.content_handler.content_type
        accepts = self.content_handler.accepts

        # send request
        while True:
            try:
                response = self.client.invoke_endpoint(
                    EndpointName=self.endpoint_name,
                    Body=body,
                    ContentType=content_type,
                    Accept=accepts,
                    **_endpoint_kwargs,
                )
                return self.content_handler.transform_output(response["Body"])
            except Exception as e:
                print(
                    f"Error raised by inference endpoint: {e}\nBody: . Trying again in 5 seconds."
                )
                time.sleep(60 * 5)

        raise ValueError(
            f"Error raised by inference endpoint: {e}. Trying again in 5 seconds."
        )
        return self.content_handler.transform_output(response["Body"])