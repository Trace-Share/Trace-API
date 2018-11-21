import os.path
import re
import subprocess
import json
import tempfile

EXT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/../ext"


class TraceAnalyzerError(Exception):
    pass


class TraceNormalizerError(Exception):
    pass


class TraceAnalyzer:

    def analyze(self, filepath):
        cmd = subprocess.Popen('python3 {}/trace-analyzer/trace-analyzer.py -f "{}" -tcp -q'.format(EXT_FOLDER, filepath), shell=True, stdout=subprocess.PIPE)

        stdout, stderr = cmd.communicate()

        if cmd.returncode != 0:
            raise TraceAnalyzerError("error_code: %s" % cmd.returncode)

        parts = re.split(b"\n", stdout)
        try:
            out = dict(
                tcp_conversations=json.loads(parts[0].decode()),
                pairs_mac_ip=json.loads(parts[1].decode()),
                capture_info=json.loads(parts[2].decode()),
            )
        except json.decoder.JSONDecodeError:
            raise TraceAnalyzerError()

        return out


class TraceNormalizer:

    def normalize(self, target_file_location, output_file_location, configuration):

        with tempfile.NamedTemporaryFile(mode="w") as f:
            f.write(json.dumps(configuration))
            f.flush()
            f.file.close()

            configuration_file = f.name

            cmd = subprocess.Popen(
                'python3 {}/trace-normalizer/trace-normalizer.py -i "{}" -o "{}" -c "{}"'
                    .format(EXT_FOLDER, target_file_location, output_file_location, configuration_file),
            shell=True, stdout=subprocess.PIPE)

            cmd.wait(timeout=10)

            if cmd.returncode != 0:
                raise TraceNormalizerError("error_code: %s" % cmd.returncode)


if __name__ == "__main__":
    hydra_test_file = os.path.dirname(os.path.realpath(__file__)) + "/../tests/fixtures/hydra-1_tasks.pcap"

    ta = TraceAnalyzer()
    # print(ta.analyze(hydra_test_file)["tcp_conversations"])
    print(ta.analyze(hydra_test_file)["pairs_mac_ip"])

    tn = TraceNormalizer()
    configuration = dict(
        IP=[
            dict(original="240.0.1.2", new="127.0.0.1"),
            dict(original="240.125.0.2", new="127.0.0.2"),
            dict(original="240.125.1.2", new="127.0.0.3"),
        ],
        MAC=[
            dict(original="08:00:27:bd:c2:37", new="08:00:00:00:00:00"),
        ]
    )
    tn.normalize(hydra_test_file, "/tmp/hydra-1_tasks.pcap.converted", configuration)

    print(ta.analyze("/tmp/hydra-1_tasks.pcap.converted")["pairs_mac_ip"])
