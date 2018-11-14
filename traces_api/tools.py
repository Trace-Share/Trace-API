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

    def get_tcp_conversations(self, filepath):
        cmd = subprocess.Popen('python3 {}/trace-analyzer/trace-analyzer.py -f "{}" -t'.format(EXT_FOLDER, filepath), shell=True, stdout=subprocess.PIPE)
        cmd.wait(timeout=10)
        if cmd.returncode != 0:
            raise TraceAnalyzerError("error_code: %s" % cmd.returncode)

        stdout = list(cmd.stdout)

        for line in stdout:
            m = re.match(b"^\x1b\[37m(?P<name>.*)\x1b\[0m\s*$", line)
            if m:
                data = json.loads(m.group("name"))
                if not data:
                    raise TraceAnalyzerError(stdout)
                return data

        raise TraceAnalyzerError()

    def get_pairs_mac_ip(self, filepath):
        cmd = subprocess.Popen('python3 {}/trace-analyzer/trace-analyzer.py -f "{}" -p'.format(EXT_FOLDER, filepath), shell=True, stdout=subprocess.PIPE)
        cmd.wait(timeout=10)
        if cmd.returncode != 0:
            raise TraceAnalyzerError("error_code: %s" % cmd.returncode)

        stdout = list(cmd.stdout)

        for line in stdout:
            m = re.match(b"^\x1b\[37m(?P<name>.*)\x1b\[0m\s*$", line)
            if m:
                data = json.loads(m.group("name"))
                if not data:
                    raise TraceAnalyzerError(stdout)
                return data

        raise TraceAnalyzerError()

    def get_pcap_dump_information(self, filename):
        return dict(
            tcp_conversations=self.get_tcp_conversations(filename),
            pairs_mac_ip=self.get_pairs_mac_ip(filename),
        )


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
    # print(ta.get_tcp_conversations(hydra_test_file))
    print(ta.get_pairs_mac_ip(hydra_test_file))

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

    print(ta.get_pairs_mac_ip("/tmp/hydra-1_tasks.pcap.converted"))
