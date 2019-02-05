import gzip


class Compression:

    @staticmethod
    def compress_file(file_location, output_location):
        """
        Compress specific file
        :param file_location: file to be compressed
        :param output_location: compressed file
        :return:
        """
        with open(file_location, "rb") as f_in:
            Compression.compress(f_in, output_location)

    @staticmethod
    def compress(file_stream, output_location):
        """
        Compress file stream and save output to file
        :param file_stream: stream to be compressed
        :param output_location: compressed file
        :return:
        """
        f_out = gzip.open(output_location, "wb")
        f_out.writelines(file_stream)
        f_out.close()

    @staticmethod
    def decompress_file(file_location, output_location):
        """
        Decompress file
        :param file_location: compressed file location to be decompressed
        :param output_location: decompressed file
        :return:
        """
        with gzip.open(file_location, "rb") as f_in:
            f_out = open(output_location, "wb")
            f_out.writelines(f_in)
            f_out.close()

