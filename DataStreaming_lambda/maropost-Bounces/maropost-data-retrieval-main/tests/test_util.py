from util import base_64_encode_string


def test_base_64_encode_string():
    some_string = "Hello there, I am a test string."
    base_64_encoded_string = base_64_encode_string(some_string)

    assert isinstance(base_64_encoded_string, (bytes,))
