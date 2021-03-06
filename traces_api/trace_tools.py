import logging
logger = logging.getLogger(__name__)

import os.path
import re
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
import yaml

from traces_api.compression import Compression

## 3p libs
import yaml

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
            with tempfile.TemporaryDirectory() as tmpdir:
                target_path = filepath
                docker_params_crawler = (
                        'sudo docker run '
                            '-v "{pcap_file}":/data/target.pcap '
                            '-v "{output_dir}":/data/ '
                            '--user $(id -u):$(id -g) '
                            'trace-tools'
                    ).format(
                        pcap_file=target_path,
                        output_dir=tmpdir,
                    )
                cmd = (
                        '{docker_params} '
                        'python trace-git/Trace-Normalizer/crawler.py '
                            '-p /data/target.pcap '
                            '-o /data/out.yml'
                    ).format(
                        docker_params=docker_params_crawler
                    )

                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                stdout, stderr = p.communicate()

                if p.returncode != 0:
                    raise TraceAnalyzerError("error_code: %s" % p.returncode)

                # if __debug__: ## TODO Cleanup and update to logg
                print("Analyzer stdout:", stdout)
                print("Analyzer stderr:", stderr)

                output = Path(tmpdir) / 'out.yml'
                with output.open('r') as handle:
                    raw_crawler_stats = yaml.load(handle.read(), Loader=yaml.FullLoader)
        except Exception as e:
            raise TraceAnalyzerError(f"{stderr}") from e ## TODO cleanup

        try:
            out = dict(
                tcp_conversations=json.loads(parts[0].decode()),
                pairs_mac_ip=json.loads(parts[1].decode()),
                capture_info=json.loads(parts[2].decode()),
            )
            out.update(raw_crawler_stats)
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

        with tempfile.NamedTemporaryFile(
                mode="w"
            ) as f, tempfile.TemporaryDirectory(
            ) as tmpdir:
            dumped_cfg = yaml.dump(configuration)
            f.write(dumped_cfg)
            f.flush()
            f.file.close()

            configuration_file = f.name

            docker_params = (
                    'docker run '
                        '--rm '
                        '-v "{target_file_location}":/data/target.pcap '
                        '-v "{output_file_location}":/data/output.pcap '
                        '-v "{configuration_file}":/data/config.conf '
                        '-v "{output_dir}":/data/ '
                        '--user $(id -u):$(id -g) '
                        'trace-tools'
                ).format(
                    target_file_location=target_file_location,
                    output_file_location=output_file_location, 
                    configuration_file=configuration_file,
                    output_dir=tmpdir
                )
            cmd = (
                    '{docker_param} python3 trace-git/Trace-Normalizer/normalizer.py '
                        '-p "{input_pcap}" '
                        '-o "{output_path}" '
                        '-l "/data/labels.yaml" '
                        '-c "{config_path}"'
                ).format(
                    docker_param=docker_params, 
                    input_pcap="/data/target.pcap", 
                    output_path="/data/output.pcap", 
                    config_path="/data/config.conf"
                )

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = p.communicate()

            # if __debug__: ## TODO Cleanup and update to logg

            if p.returncode != 0:
                # print("Configuartion: %s" % dumped_cfg)
                # print("Mix stdout: %s" % stdout.decode())
                # print("Mix stderr: %s" % stderr.decode())
                # print("TraceMixerError error_code %s" % p.returncode)
                logger.debug("Configuartion: %s", dumped_cfg)
                logger.debug("Normalize stdout: %s", stdout.decode())
                logger.debug("Normalize stderr: %s", stderr.decode())
                logger.error("TraceNormalizerError error_code %s", p.returncode)
                raise TraceNormalizerError("error_code: %s" % p.returncode)
            
            output = Path(tmpdir) / 'labels.yaml'
            with output.open('r') as handle:
                output_data = yaml.load(handle.read(), Loader=yaml.FullLoader)
        return output_data


    @staticmethod
    def prepare_configuration(
            ip_details, 
            mac_mapping, 
            tcp_timestamp_mapping,
        ):
        """
        Prepare configuration dict with given parameters

        :param ip_details:  detials object containing source, inter and target addresses
        :type ip_detail: IPDetails
        :param mac_mapping: Mac mapping, with mac key, and list of related ips
        :param tcp_timestamp_mapping: mapping of ip addresses to minimum tcp timestamp 
        :return: configuration dict
        """
        configuration = {
            "ip.groups" : {
                "source" : [],
                "intermediate" : [],
                "destination" : []
            },
            "mac.associations" : {},
            "tcp.timestamp.min" : []
        }
        if ip_details:
            ip_groups = configuration['ip.groups']
            if ip_details.source_nodes:
                ip_groups["source"] = ip_details.source_nodes.copy()
            if ip_details.intermediate_nodes:
                ip_groups["intermediate"] = ip_details.intermediate_nodes.copy()
            if ip_details.target_nodes:
                ip_groups["destination"] = ip_details.target_nodes.copy()


        if mac_mapping and mac_mapping.data:
            configuration[
                "mac.associations"
                ] = [
                        dict(mac=mac, ips=ips) 
                        for mac, ips 
                        in mac_mapping.data
                ]

        if tcp_timestamp_mapping and tcp_timestamp_mapping.data:
            configuration[
                    "tcp.timestamp.min"
                ] = [
                        dict(ip=ip, min=timestamp)
                        for ip, timestamp
                        in tcp_timestamp_mapping.data
                ]

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

    def mix(self, annotated_unit_file, config, at_timestamp):
        """
        Add annotated unit to mix
        :param annotated_unit_file:
        :return:
        """

        self._mix(annotated_unit_file, config, at_timestamp)

        self._previous_pcap = self._output_location

    def _mix(self, annotated_unit_file, config, at_timestamp):
        with tempfile.NamedTemporaryFile(mode="wb") as f_tmp, \
            tempfile.NamedTemporaryFile(mode="w") as tmp_config, \
            tempfile.TemporaryDirectory() as tmp_dir:
            with open(self._previous_pcap, "rb") as f_previouse:
                f_tmp.write(f_previouse.read())
            f_tmp.flush()
            f_tmp.file.close()
            tmp_file = f_tmp.name

            tmp_config.write(yaml.dump(config))
            tmp_config.flush()
            tmp_config_path = tmp_config.name

            tmp_dir_name = tmp_dir

            config['atk.file'] = '/data/mix_file.pcap'

            dec_anot_unit_file = str(
                Path(tmp_dir_name) / 'decompressed_annotated_unit.pcap'
            )
            Compression.decompress_file(annotated_unit_file, dec_anot_unit_file)

            docker_params = (
                    'docker run '
                        '--rm '
                        '-v "{}":/data/target.pcap '
                        '-v "{}":/data/config.yaml '
                        '-v "{}":/output ' 
                        '-v "{}":/data/mix_file.pcap '
                        '--user $(id -u):$(id -g) '
                        'trace-tools'
                ).format(
                    tmp_file, 
                    tmp_config_path,
                    tmp_dir_name, #pick from here 
                    dec_anot_unit_file
                )

            cmd = (
                    '{} ./trace-git/ID2T/id2t '
                        '-i "{}" '
                        '-o "{}" '
                        '-a Mix '
                            'custom.payload.file={} '
                            'inject.at-timestamp={} '
                ).format(
                    docker_params, 
                    "/data/target.pcap", 
                    "/output/output.pcap",
                    "/data/config.yaml",
                    at_timestamp
                )

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                logger.debug("Mix stdout: %s", stdout.decode())
                logger.debug("Mix stderr: %s", stderr.decode())
                logger.error("TraceMixerError error_code %s", p.returncode)
                raise TraceMixerError("error_code: %s" % p.returncode)

            output_pcap = Path(tmp_dir_name) / 'output.pcap'
            if not output_pcap.exists():
                logger.error("Pcap file doesn't exist")
                raise TraceMixerError("")

            shutil.move(str(output_pcap), self._output_location)

    @staticmethod
    def prepare_configuration(
            ip_mapping, 
            mac_mapping, 
            port_mapping,
        ):
        configuration = {
            'timestamp': {
                'generation': 'tcp_avg_shift',
                'postprocess': [],
                'generation.alt': 'timestamp_dynamic_shift',
                'random.treshold': 0.001,
            },
            'tcp.timestamp.shift' : [],
            'tcp.timestamp.shift.default' : 0,
            'ip.map' : [],
            'mac.map' : [],
            'port.ip.map' : [],
            'atk.file' : '/data/mix_file.pcap',
        }
        if ip_mapping and ip_mapping.data:
            configuration["ip.map"] = [dict(ip=dict(old=original, new=replacement)) for original, replacement in
                                   ip_mapping.data]

        if mac_mapping and mac_mapping.data:
            configuration["mac.map"] = [dict(mac=dict(old=original, new=replacement)) for original, replacement in
                                    mac_mapping.data]

        if port_mapping is not None:
            configuration['port.ip.map'] = port_mapping

        return configuration

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
