import argparse
import subprocess
import json


def parse_configuration(config_file):
    with open(config_file, "r") as f:
        raw = f.read()
        data = json.loads(raw)
    return data


def mix(base_file, mixed_file, output_file):
    command = ["mergecap", base_file, mixed_file, "-w", output_file]

    command_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = command_process.communicate()

    if stderr:
        raise Exception("Error occurred: %s" % stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mix_file", help="File to be mixed.", type=str, required=True)
    parser.add_argument("-b", "--base_file", help="Base pcap file", type=str, required=True)
    parser.add_argument("-o", "--output", help="Output file", type=str, required=True)
    args = parser.parse_args()

    mix(args.base_file, args.mix_file, args.output)
