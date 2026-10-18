"""Backward-compatibility shim for modelrouter.providers.provider."""
import os
import sys

_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "our-project", "code", "src"))
if os.path.isdir(_src_dir) and _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from modelrouter.providers.provider import *
from modelrouter.providers.provider import (
    BaseGeneratorProvider,
    OpenAIChatCompletionsProvider,
    OpenAICompatibleProvider,
    OpenAIResponsesProvider,
    AnthropicMessagesProvider,
    MockGeneratorProvider,
    OracleGeneratorProvider,
    GeneratorResponse,
    parse_react_response,
    load_generator_credentials,
    update_token_budget,
)
