import base64


def base_64_encode_string(string_to_encode: str):
    """Base 64 encodes a string

    Args:
        string_to_encode: str

    Returns:
        A base-64 encoded string
    """
    return base64.b64encode(string_to_encode.encode("ascii"))
