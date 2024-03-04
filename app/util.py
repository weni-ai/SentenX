import json

from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler


class ContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: dict) -> bytes:  # pragma: no cover
        input_str = json.dumps({"inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> list[list[float]]:  # pragma: no cover
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["vectors"]


def count_words(string: str):
    return len(string.split())
