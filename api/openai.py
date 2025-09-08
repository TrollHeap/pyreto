# --- OpenAI (Responses API) ---
from openai import OpenAI
from dataclasses import dataclass
from enum import Enum
import os


class ModelOPENAI(Enum):
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"


@dataclass
class OpenAIConfig:
    model: str = ModelOPENAI.GPT_5
    prompt_id: str | None = None
    prompt_version: str | None = None
    prompt_vars: dict | None = None
    instructions: str | None = "Tu es concis, précis, et technique."


class OpenAIResponder:

    def __init__(self, cfg: OpenAIConfig) -> None:
        # Préfère OPENAI_API_KEY ; fallback sur OPENAI_KEY
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
        if not api_key:
            raise RuntimeError(
                "La clé API OpenAI est manquante. "
                "Définis OPENAI_API_KEY (ou OPENAI_KEY) dans l'environnement."
            )
        # Passe explicitement la clé au client
        self.client = OpenAI(api_key=api_key)
        self.cfg = cfg

    def generate(self, *, input_text: str | None = None) -> str:
        """
        Utilise soit un prompt réutilisable du dashboard (prompt=id/version/variables),
        soit un input text classique. Retourne response.output_text.
        """
        kwargs: dict = {"model": self.cfg.model}

        if self.cfg.instructions:
            kwargs["instructions"] = self.cfg.instructions

        if self.cfg.prompt_id:
            # Reusable prompt (dashboard)
            prompt_obj = {"id": self.cfg.prompt_id}
            if self.cfg.prompt_version:
                prompt_obj["version"] = self.cfg.prompt_version
            if self.cfg.prompt_vars is not None:
                prompt_obj["variables"] = self.cfg.prompt_vars
            kwargs["prompt"] = prompt_obj
        else:
            if not input_text:
                raise ValueError(
                    "Aucun input_text fourni et aucun prompt réutilisable configuré."
                )
            kwargs["input"] = input_text

        resp = self.client.responses.create(**kwargs)
        # Agrégation sûre du texte produit
        return getattr(resp, "output_text", "").strip()
