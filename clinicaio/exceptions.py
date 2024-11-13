
class DownloadError(Exception):
    """Base class for download errors exceptions."""


class ClinicaIOArgumentError(ValueError):
    """Base class for ClinicaIO CLI Arguments error."""


class ClinicaIOConfigurationError(ValueError):
    """Base class for ClinicaIO configurations error."""


class ClinicaIOException(Exception):
    """Base class for ClinicaIO exceptions."""


class MAPSError(ClinicaIOException):
    """Base class for MAPS exceptions."""


class ClinicaIONetworksError(ClinicaIOException):
    """Base class for Networks exceptions."""


class ClinicaIODataLeakageError(ClinicaIOException):
    """Base class for data leakage exceptions."""


class ClinicaIOTSVError(ClinicaIOException):
    """Base class for tsv files exceptions."""


class ClinicaIOBIDSError(ClinicaIOException):
    """Base class for tsv files exceptions."""


class ClinicaIOCAPSError(ClinicaIOException):
    """Base class for tsv files exceptions."""


class ClinicaIOConcatError(ClinicaIOException):
    """Base class for Concat Datasets exceptions."""
