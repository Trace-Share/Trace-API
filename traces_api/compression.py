import gzip


class Compression:

    @staticmethod
    def compress_file(file_location, output_location):
        with open(file_location, "rb") as f_in:
            Compression.compress(f_in, output_location)

    @staticmethod
    def compress(file_stream, output_location):
        f_out = gzip.open(output_location, "wb")
        f_out.writelines(file_stream)
        f_out.close()

    @staticmethod
    def decompress_file(file_location, output_location):
        with gzip.open(file_location, "rb") as f_in:
            f_out = open(output_location, "wb")
            f_out.writelines(f_in)
            f_out.close()

