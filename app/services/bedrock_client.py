import json
import logging

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

BEDROCK_CONFIG = Config(
    connect_timeout=2,
    read_timeout=10,
    retries={"max_attempts": 1},
)

SYSTEM_PROMPT_FORMAT = (
    "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n"
    "{prompt}\n"
    "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
)


class BedrockUnavailableError(Exception):
    pass


class BedrockClient:
    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime", region_name=region, config=BEDROCK_CONFIG
        )

    def invoke(self, prompt: str, max_gen_len: int = 512) -> str:
        formatted_prompt = SYSTEM_PROMPT_FORMAT.format(prompt=prompt)
        body = json.dumps(
            {
                "prompt": formatted_prompt,
                "max_gen_len": max_gen_len,
                "temperature": 0.3,
                "top_p": 0.9,
            }
        )
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                body=body,
            )
            decoded = response["body"].read().decode("utf-8")
            parsed = json.loads(decoded)
            if isinstance(parsed, dict) and isinstance(parsed.get("generation"), str):
                return parsed["generation"]
            return decoded
        except Exception as error:
            logger.warning("Error al invocar Bedrock: %s", error)
            raise BedrockUnavailableError("El servicio de IA no está disponible temporalmente") from error