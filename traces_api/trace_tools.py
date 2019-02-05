import os.path
import re
import subprocess
import json
import tempfile

EXT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/../ext"


class TraceAnalyzerError(Exception):
    """
    Unknown error in trace analyzer occurs
    """
    pass


class TraceNormalizerError(Exception):
    """
    Unknown error in trace normalizer occurs
    """
    pass


class TraceMixerError(Exception):
    """
    Unknown error in trace mixer occurs
    """
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

        Tool is able to extract this information from captured traffic dump:
        - tcp conversations
        - ip paris
        - mac pairs
        - other capture information

        :param filepath: path to file to be analyzed
        :return: dict that contains analyzed information
        """
        docker_params = "docker run --rm  -v \"{}\":/dumps/file.pcap trace-tools".format(filepath)
        cmd = '{} python3 trace-analyzer/trace-analyzer.py -f "{}" -tcp -q'.format(docker_params, "/dumps/file.pcap")

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise TraceAnalyzerError("error_code: %s" % p.returncode)

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

            docker_params = 'docker run --rm -v "{}":/data/target.pcap -v "{}":/data/output.pcap ' \
                            '-v "{}":/data/config.conf trace-tools'.format(
                                target_file_location, output_file_location, configuration_file
                            )
            cmd = '{} python3 trace-normalizer/trace-normalizer.py -i "{}" -o "{}" -c "{}"'\
                .format(docker_params, "/data/target.pcap", "/data/output.pcap", "/data/config.conf")

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

            stdout, stderr = p.communicate()

            if p.returncode != 0:
                raise TraceNormalizerError("error_code: %s" % p.returncode)

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
        if ip_mapping and ip_mapping.data:
            configuration["IP"] = [dict(original=original, new=replacement) for original, replacement in
                                   ip_mapping.data]

        if mac_mapping and mac_mapping.data:
            configuration["MAC"] = [dict(original=original, new=replacement) for original, replacement in
                                    mac_mapping.data]

        if timestamp:
            configuration["timestamp"] = timestamp

        return configuration


class TraceMixer:
    """
    One specific mixing operation

    Example usage:
        tm = TraceMixer(output_location)
        tm.mix(ann_unit1)
        tm.mix(ann_unit2)
    """

    BASE_PCAP_FILE = EXT_FOLDER + "/trace-mixer/base.pcap"

    def __init__(self, output_location):
        self._previous_pcap = self.BASE_PCAP_FILE
        self._output_location = output_location

    def mix(self, annotated_unit_file):
        """
        Add annotated unit to mix
        :param annotated_unit_file:
        :return:
        """

        self._mix(annotated_unit_file)

        self._previous_pcap = self._output_location

    def _mix(self, annotated_unit_file):
        with tempfile.NamedTemporaryFile(mode="wb") as f_tmp:
            with open(self._previous_pcap, "rb") as f_previouse:
                f_tmp.write(f_previouse.read())
            f_tmp.flush()
            f_tmp.file.close()
            tmp_file = f_tmp.name

            docker_params = 'docker run --rm -v "{}":/data/target.pcap -v "{}":/data/output.pcap ' \
                            '-v "{}":/data/mix_file.pcap trace-tools'.format(
                                tmp_file, self._output_location, annotated_unit_file
                            )

            cmd = '{} python3 trace-mixer/trace-mixer.py -b "{}" -o "{}" -m "{}"'\
                      .format(docker_params, "/data/target.pcap", "/data/output.pcap", "/data/mix_file.pcap")

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                raise TraceMixerError("error_code: %s" % p.returncode)

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
