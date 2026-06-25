import asyncio

from app.core.llm_connector import BACKEND_SELF_HOSTED, LLMConnector


def test_hosted_llm_is_preferred_for_cloud_calls() -> None:
    llm = LLMConnector(
        local_base_url="http://localhost:11434",
        local_model="local",
        hosted_base_url="https://llm.example.com/v1",
        hosted_model="self-hosted-model",
        hosted_embedding_model="self-hosted-embed",
        cloud_base_url="https://api.groq.com/openai/v1",
        cloud_api_key="",
        cloud_model="groq-model",
    )

    assert llm.has_cloud
    assert llm.has_hosted
    assert llm._chat_url(use_cloud=True) == "https://llm.example.com/v1/chat/completions"  # noqa: SLF001
    assert llm._model(use_cloud=True) == "self-hosted-model"  # noqa: SLF001
    assert llm._backend_name(use_cloud=True) == BACKEND_SELF_HOSTED  # noqa: SLF001
    assert llm._remote_embedding_model() == "self-hosted-embed"  # noqa: SLF001
    asyncio.run(llm.close())
