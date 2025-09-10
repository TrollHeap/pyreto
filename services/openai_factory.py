from typing import Optional
from api.openai import OpenAIResponder, OpenAIConfig
import json


def build_openai_client(self) -> Optional[OpenAIResponder]:
    if not self.ask_confirm("Configurer OpenAI maintenant ? (sinon placeholders)", True):
        return None

    model = self.ask_text("Modèle OpenAI", "gpt-5")
    instructions = self.ask_text("Instructions globales", "Tu es concis, précis, et technique.")
    prompt_id = prompt_version = None
    prompt_vars = None

    if self.ask_confirm("Utiliser un prompt réutilisable (dashboard) ?", False):
        prompt_id = self.ask_text("Prompt ID (dashboard)")
        sver = self.ask_text("Prompt version (optionnel)", "")
        prompt_version = sver or None
        vars_str = self.ask_text('Variables JSON (optionnel, ex: {"topic":"awk"})', "")

        try:
            prompt_vars = json.loads(vars_str) if vars_str else None
        except Exception as e:
            self.console.print(f"[yellow]Variables JSON ignorées:[/yellow] {e}")

    try:
        return OpenAIResponder(OpenAIConfig(
            model=model, instructions=instructions,
            prompt_id=prompt_id, prompt_version=prompt_version, prompt_vars=prompt_vars
        ))

    except Exception as e:
        self.console.print(f"[yellow]Client OpenAI non initialisé:[/yellow] {e}\n"
                           "[yellow]Le script créera des placeholders.[/yellow]")
        return None
