from pydantic import BaseModel
from types import SimpleNamespace
from unittest.mock import patch

from src.utils.llm import call_llm


class DummyLLM:
    def __init__(self, result):
        self.result = result
        self.with_structured_called = False
        self.model = None

    def with_structured_output(self, model_cls, method="json_mode"):
        self.with_structured_called = True
        self.model = model_cls
        return self

    def invoke(self, prompt):
        return self.result


class JSONModel(BaseModel):
    foo: str


def test_call_llm_json_mode():
    expected = JSONModel(foo="bar")
    dummy_llm = DummyLLM(expected)

    class Info:
        def has_json_mode(self):
            return True

    with patch("src.utils.llm.get_model_info", return_value=Info()), \
         patch("src.utils.llm.get_model", return_value=dummy_llm):
        result = call_llm("prompt", "model", "provider", JSONModel)

    assert result == expected
    assert dummy_llm.with_structured_called
    assert dummy_llm.model is JSONModel


def test_call_llm_non_json_mode():
    response = SimpleNamespace(content="```json\n{\"foo\": \"bar\"}\n```")
    dummy_llm = DummyLLM(response)

    class Info:
        def has_json_mode(self):
            return False

    with patch("src.utils.llm.get_model_info", return_value=Info()), \
         patch("src.utils.llm.get_model", return_value=dummy_llm):
        result = call_llm("prompt", "model", "provider", JSONModel)

    assert isinstance(result, JSONModel)
    assert result.foo == "bar"
    assert not dummy_llm.with_structured_called
