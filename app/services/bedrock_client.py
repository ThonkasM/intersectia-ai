import json
import logging

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

BEDROCK_CONFIG = Config(
    connect_timeout=2,
    read_timeout=25,
    retries={"max_attempts": 1},
)

CHAT_PROMPT_FORMAT = (
    "<|begin_of_text|>"
    "<|start_header_id|>system<|end_header_id|>\n"
    "{system}\n"
    "<|eot_id|>"
    "<|start_header_id|>user<|end_header_id|>\n"
    "{prompt}\n"
    "<|eot_id|>"
    "<|start_header_id|>assistant<|end_header_id|>\n"
)

DEFAULT_SYSTEM_PROMPT = (
    "Eres el Asistente de IntersectIA, un proyecto educativo sobre IoT y vehículos "
    "autónomos. Respondes SIEMPRE en español, de forma clara y concisa. Nunca respondas "
    "en otro idioma aunque los datos de contexto estén en inglés. Los identificadores "
    "técnicos (approach, queued, crossing, success, gone, frozen, crashed) se citan tal "
    "cual, pero toda la explicación va en español."
)


class BedrockUnavailableError(Exception):
    pass


class BedrockClient:
    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime", region_name=region, config=BEDROCK_CONFIG
        )

    def invoke(
        self,
        prompt: str,
        system: str | None = None,
        max_gen_len: int = 512,
    ) -> str:
        formatted_prompt = CHAT_PROMPT_FORMAT.format(
            system=system or DEFAULT_SYSTEM_PROMPT,
            prompt=prompt,
        )
        body = json.dumps(
            {
                "prompt": formatted_prompt,
                "max_gen_len": max_gen_len,
                "temperature": 0.2,
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