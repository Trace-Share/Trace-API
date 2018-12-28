from traces_api.compression import Compression
import uuid
import tempfile


def create_empty_file():
    random_file_path = "/tmp/trace_api_%s" % str(uuid.uuid4())
    with open(random_file_path, "wb"):
        pass
    return random_file_path


def read_file(file_location):
    with open(file_location, "rb") as f:
        return f.read()


def test_compression():
    gzip = Compression()

    with tempfile.NamedTemporaryFile(mode="wb") as f:
        f.write(b"TEST INPUT")
        f.flush()

        compressed_file = create_empty_file()

        gzip.compress_file(f.name, compressed_file)

        assert read_file(f.name) == b"TEST INPUT"
        assert read_file(compressed_file) != b"TEST INPUT"

    decompressed_file = create_empty_file()
    gzip.decompress_file(compressed_file, decompressed_file)
    assert read_file(decompressed_file) == b"TEST INPUT"
