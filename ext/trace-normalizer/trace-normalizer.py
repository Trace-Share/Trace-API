#!/usr/bin/env python

#
# BSD 3-Clause License
#
# Copyright (c) 2018, CSIRT-MU, Masaryk University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
Script facilitating packet trace normalization. Enables to easily change IP and MAC addresses, and reset capture
start time to zero.

Due to the tcprewrite and bittwiste, the sciprt converts given capture file to PCAP format and
at the end back to PCAP-Ng format.

Requirements:
    * tcprewrite
    * editcap
    * bittwiste
    * Python 3
    * Python modules: termcolor

Usage:
    $ ./trace-normalizer.py -i <input_capture_file> -o <output_capture_file> -c <configuration_json>
"""

# Common python modules
import sys  # Common system functions
import os  # Common operating system functions
import argparse  # Arguments parser
import subprocess  # Executes commands in shell
import shlex  # Split the string s using shell-like syntax
import shutil  # Copy files and directory trees
import json  # JSON processing functions
from distutils.spawn import find_executable  # Check if required tool is available in PATH

# Additional python modules
from termcolor import cprint  # Colors in the console output


def check_requirements():
    """
    Checks if all necessary programs are installed.

    :return: True if all tools are available, False otherwise
    """
    for tool in ["tcprewrite", "editcap", "bittwiste"]:
        if not find_executable(tool):
            return False
    return True


def run_command(command):
    """
    Run given command and provide its output as a result.

    :param command: command to be run
    :return: command output or None if error occurred
    """
    cprint("[info] Running command: " + command, "green")
    command_process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = command_process.communicate()

    if stderr and ("written" not in stderr.decode('utf-8')):
        cprint("[error] Command \"{command}\" returned an error:\n{error}".format(command=command, error=stderr), "red")
        return None
    else:
        return stdout


def convert_to_pcap(input_file, output_file):
    """
    Converts given input file to PCAP format and store it in the output_file.

    :param input_file: capture file to convert
    :param output_file: output file path
    """
    command = "editcap -F pcap {input_file} {output_file}".format(input_file=input_file, output_file=output_file)
    run_command(command)


def convert_to_pcapng(input_file, output_file):
    """
    Converts given input file to PCAP-Ng format and store it in the output_file.

    :param input_file: capture file to convert
    :param output_file: output file path
    """
    command = "editcap -F pcapng {input_file} {output_file}".format(input_file=input_file, output_file=output_file)
    run_command(command)


def reset_timestamp(input_file, output_file, configuration):
    """
    Reset timestamp to zero epoch time in given input file and writes result to the output_file.

    :param input_file: temporary capture file to reset timestamp
    :param output_file: temporary output file path
    :param configuration: parsed script configuration
    """
    command = "editcap -t -{timestamp} {input_file} {output_file}".format(
        timestamp=configuration["timestamp"], input_file=input_file, output_file=output_file
    )
    run_command(command)


def normalize_ip_addresses(input_file, output_file, configuration):
    """
    Change IP addresses based on given configuration and writes result to the output_file.

    :param input_file: temporary capture file to normalize
    :param output_file: temporary output file path
    :param configuration: parsed script configuration
    """
    addresses_mapping = ""
    for mapping in configuration["IP"]:
        addresses_mapping += "{original}:{new},".format(original=mapping["original"], new=mapping["new"])
    addresses_mapping = addresses_mapping[:-1]

    command = "tcprewrite --infile {input_file} --outfile {output_file} --pnat={addresses_mapping}".format(
        input_file=input_file, output_file=output_file, addresses_mapping=addresses_mapping
    )
    run_command(command)


def normalize_mac_addresses(input_file, output_file, configuration):
    """
    Change MAC addresses based on given configuration and writes result to the output_file.

    (Bittwiste tool can change only one MAC address in its run.)

    :param input_file: temporary capture file to normalize
    :param output_file: temporary output file path
    :param configuration: parsed script configuration
    """
    # Handlers for a current output files
    tmp_input = input_file
    tmp_output = output_file

    for mapping in configuration["MAC"]:
        command = "bittwiste -I {input_file} -O {output_file} -T eth -s {original},{new} -d {original},{new}".format(
            input_file=tmp_input, output_file=tmp_output, original=mapping["original"], new=mapping["new"]
        )
        run_command(command)
        # Switch output file handlers
        tmp_input, tmp_output = tmp_output, tmp_input

    # Copy last temporary file to output_file if it is not specified output_file
    if tmp_input != output_file:
        shutil.copy2(tmp_input, output_file)


if __name__ == "__main__":
    # Argument parser automatically creates -h argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Capture filename to normalize.", type=str, required=True)
    parser.add_argument("-o", "--output_file", help="Filename for a normalized capture.", type=str, required=True)
    parser.add_argument("-c", "--configuration", help="Configuration JSON with mapping of IP and MAC addresses.",
                        type=argparse.FileType('r'), required=False, default="./trace-normalizer.json")
    args = parser.parse_args()

    if not check_requirements():
        cprint("[error] Requirements missing, install \"tcprewrite\", \"editcap\", and \"bittwiste\" tools!", "red")
        sys.exit(1)

    try:
        configuration = json.load(args.configuration)
    except ValueError as exc:
        cprint("[error] JSON configuration not correctly loaded: " + str(exc), "red")
        sys.exit(1)

    # Define names for temporary capture files
    tmp_capture_1 = "normalizer_tmp_capture-1.pcap"
    tmp_capture_2 = "normalizer_tmp_capture-2.pcap"

    # PCAP format is required by tcprewrite and bittwiste tools
    cprint("[info] Converting input file to PCAP format...", "green")
    convert_to_pcap(args.input_file, tmp_capture_1)

    if "timestamp" in configuration:
        cprint("[info] Starting trace normalization...", "green")
        reset_timestamp(tmp_capture_1, tmp_capture_2, configuration)

    if "IP" in configuration:
        cprint("[info] Starting IP addresses normalization...", "green")
        normalize_ip_addresses(tmp_capture_1, tmp_capture_2, configuration)

    if "MAC" in configuration:
        cprint("[info] Starting MAC addresses normalization...", "green")
        normalize_mac_addresses(tmp_capture_1, tmp_capture_2, configuration)

    cprint("[info] Converting output file to PCAP-Ng format...", "green")
    convert_to_pcapng(tmp_capture_2, args.output_file)

    os.remove(tmp_capture_1)
    os.remove(tmp_capture_2)

    cprint("[info] Trace file normalized!", "green")
