
from traces_api.tools import escape


def test_escape():
    assert escape(None) is None
    assert escape(1) == 1
    assert escape([]) == []
    assert escape([{"a": 3}]) == [{"a": 3}]
    assert escape([{">": 3}]) == [{"": 3}]

    assert escape(["abc", "<script>aaa"]) == ["abc", "scriptaaa"]
