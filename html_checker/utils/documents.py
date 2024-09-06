import io
import os

from .paths import resolve_paths


def write_documents(destination, documents):
    """
    Write every given documents files into destination directory.

    Arguments:
        destination (string): Destination directory where to write files. If
            given directory path does not exist, it will be created.
        documents (list): List of document datas (``dict``) with item ``document`` for
            document relative (from ``destination``) filepath where to write and
            item ``content`` for content string to write to file.

    Returns:
        list: List of written documents.
    """
    files = []

    if not os.path.exists(destination):
        os.makedirs(destination)

    for doc in documents:
        file_destination = resolve_paths(destination, doc["document"])
        files.append(file_destination)

        with io.open(file_destination, 'w') as fp:
            fp.write(doc["content"])

    return files
