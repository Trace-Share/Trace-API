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
    """
    Analyze captured traffic dump

    This class uses external tool - trace-analyzer
    More information about this tool you can find here:
        https://github.com/CSIRT-MU/Trace-Share/tree/master/trace-analyzer
    """

    def analyze(self, filepath):
        """
        Analyze captured traffic dump

        Tool is able to extract this information from captured traffuc dump:
        - tcp conversations
        - ip paris
        - mac pairs
        - other capture informations

        :param filepath: path to file to be analyzed
        :return: dict that contains analyzed information
        """
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
    """
    Normalize captured traffic dump

    Tool is able to replace IP and mac addresses and reset timestamps in capture to epoch time.

    This class uses external tool - trace-normalizer
    More information about this tool you can find here:
        https://github.com/CSIRT-MU/Trace-Share/tree/master/trace-normalizer
    """

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

            stdout, stderr = cmd.communicate()

            if cmd.returncode != 0:
                raise TraceNormalizerError("error_code: %s" % cmd.returncode)

    @staticmethod
    def prepare_configuration(ip_mapping, mac_mapping, timestamp):
        """
        Prepare configuration dict with given parameters

        :param ip_mapping:
        :param mac_mapping:
        :param timestamp:
        :return: configuration dict
        """
        configuration = {}
        if ip_mapping:
            configuration["IP"] = [dict(original=original, new=replacement) for original, replacement in
                                   ip_mapping.data]

        if mac_mapping:
            configuration["MAC"] = [dict(original=original, new=replacement) for original, replacement in
                                    mac_mapping.data]

        if timestamp:
            configuration["timestamp"] = timestamp

        return configuration


class TraceMixer:
    """
    One specific mixing operation

    Example usage:
        tm = TraceMixer()
        tm.mix(ann_unit1)
        tm.mix(ann_unit2)
    """

    def __init__(self, output_location):
        self._output_location = output_location

    def mix(self, annotated_unit_file):
        """
        Add annotated unit to mix
        :param annotated_unit_file:
        :return:
        """
        pass

    def get_mixed_file_location(self):
        return self._output_location


class TraceMixing:
    """
    Provide ability to combine multiple annotated units into one mix
    """
    @staticmethod
    def create_new_mixer(output_location):
        """
        Create one Trace mixer instance
        :param output_location
        :return: TraceMixer
        """
        return TraceMixer(output_location)


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
