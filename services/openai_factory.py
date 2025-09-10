from typing import Optional
from api.openai import OpenAIResponder, OpenAIConfig


def build_openai_client(self) -> Optional[OpenAIResponder]:
    if not self.ask_confirm("Configurer OpenAI maintenant ? (sinon placeholders)", True):
        return None

    model = self.ask_text("Modèle OpenAI", "gpt-5-nano")
    instructions = self.ask_text("Instructions globales", "Tu es concis, précis, et technique.")
    prompt_id = prompt_version = None
    prompt_vars = None

    try:
        return OpenAIResponder(OpenAIConfig(
            model=model, instructions=instructions,
            prompt_id=prompt_id, prompt_version=prompt_version, prompt_vars=prompt_vars
        ))

    except Exception as e:
        self.console.print(f"[yellow]Client OpenAI non initialisé:[/yellow] {e}\n"
                           "[yellow]Le script créera des placeholders.[/yellow]")
        return None
