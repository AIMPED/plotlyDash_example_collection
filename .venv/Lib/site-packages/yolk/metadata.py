"""metadata.

Author   : Rob Cakebread <cakebread @ gmail>

License  : BSD (See COPYING)

Desc     : Return metadata for Python distribution installed by setuptools
           in a dict

           Note: The metadata uses RFC 2822-based message documents.

"""

import collections
import email


def get_metadata(dist):
    """Return dictionary of metadata for given dist.

    @param dist: distribution
    @type dist: pkg_resources Distribution object

    @returns: dict of metadata or None

    """
    metadata = collections.OrderedDict()

    if dist.has_metadata('PKG-INFO'):
        text = dist.get_metadata('PKG-INFO')
    elif dist.has_metadata('METADATA'):
        text = dist.get_metadata('METADATA')
    else:
        return metadata

    try:
        message = email.message_from_string(text)
        for header in [l for l in message._headers]:
            metadata[header[0]] = header[1]
    except IOError:
        # No egg-file, installed using other package manager.
        pass

    return metadata
