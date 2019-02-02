import pytest
import os.path
import tempfile

from traces_api.trace_tools import TraceNormalizer, TraceNormalizerError
from traces_api.trace_tools import TraceAnalyzer, TraceAnalyzerError


@pytest.fixture()
def analyzer():
    return TraceAnalyzer()


@pytest.fixture()
def normalizer():
    return TraceNormalizer()


@pytest.fixture()
def hydra_1_file():
    return os.path.dirname(os.path.realpath(__file__)) + "/fixtures/hydra-1_tasks.pcap"


def compare_list_dict(list_1, list_2):
    sl1 = sorted(sorted(i.items()) for i in list_1)
    sl2 = sorted(sorted(i.items()) for i in list_2)
    return sl1 == sl2


def test_analyzer_analyze_invalid_input(analyzer):
    with pytest.raises(TraceAnalyzerError):
        analyzer.analyze("/tmp/NON_EXISTING_FILE____")


def test_analyzer_get_pairs_mac_ip(analyzer, hydra_1_file):
    response = analyzer.analyze(hydra_1_file)["pairs_mac_ip"]

    expected = [{'MAC': '08:00:27:bd:c2:37', 'IP': '240.125.0.2'},
                {'MAC': '08:00:27:90:8f:c4', 'IP': '240.0.1.2'},
                {'MAC': '08:00:27:bd:c2:37', 'IP': '240.125.0.2'},
                {'MAC': '08:00:27:90:8f:c4', 'IP': '240.0.1.2'}]

    assert compare_list_dict(response, expected)


def test_analyzer_get_tcp_conversations(analyzer, hydra_1_file):
    response = analyzer.analyze(hydra_1_file)["tcp_conversations"]

    assert len(response) == 61

    for r in response:
        assert set(r.keys()) == {'IP A', 'Port A', 'IP B', 'Port B', 'Frames B-A', 'Bytes B-A', 'Frames A-B',
                                 'Bytes A-B', 'Frames', 'Bytes', 'Relative start'}


def test_normalizer_invalid_input(normalizer):
    with pytest.raises(TraceNormalizerError):
        normalizer.normalize("/tmp/NON_EXISTING_FILE____", "/tmp/NON_EXISTING_FILE____2", dict())


def test_normalizer(analyzer, normalizer, hydra_1_file):
    configuration = dict(
        IP=[
            dict(original="240.0.1.2", new="172.16.0.1"),
            dict(original="240.125.0.2", new="172.16.0.2"),
            dict(original="240.125.1.2", new="172.16.0.3"),
        ],
        MAC=[
            dict(original="08:00:27:bd:c2:37", new="00:00:00:00:00:00"),
        ]
    )

    with tempfile.NamedTemporaryFile() as f:
        f.file.close()

        normalizer.normalize(hydra_1_file, f.name, configuration)

        expected = [{'MAC': '08:00:27:bd:c2:37', 'IP': '172.16.0.2'},
                    {'MAC': '08:00:27:90:8f:c4', 'IP': '172.16.0.1'},
                    {'MAC': '00:00:00:00:00:00', 'IP': '172.16.0.3'},
                    {'MAC': '08:00:27:90:8f:c4', 'IP': '172.16.0.1'}]
        response = analyzer.analyze(f.name)

        compare_list_dict(response["pairs_mac_ip"], expected)
