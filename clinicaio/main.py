
from pathlib import Path
from abc import abstractmethod
from typing import Union, Optional
from logging import getLogger

from .preprocessing import PreprocessingConfig, get_preprocessing
from .clinica_utils import container_from_filename, check_caps_folder, get_subject_session_list, clinicadl_file_reader
from .enum import Preprocessing

logger = getLogger("clinicaio.main")

class Reader:
    """Base reader class for BIDS and CAPS directories.

    Args:
        input_dir (Path): Path to the BIDS or CAPS directory.
    """
    def __init__(self, input_dir: Path) -> None:
        check_caps_folder(input_dir)
        self.input_directory = input_dir

    @abstractmethod
    def subject_path(self, **kwargs) -> Path:
        """Return the path to the subject directory."""
        pass


class CapsReader(Reader):
    """Reader class for CAPS directories."""
    def __init__(self, input_dir: Path) -> None:
        super().__init__(input_dir)

    def subject_path(self, **kwargs)-> Path:
        return Path("")
    
    def preprocessing_folder(
        self, subject: str, session: str, preprocessing: Preprocessing
    ) -> Path:
        
        return (
            self.input_directory
            / "subjects"
            / subject
            / session
            / (preprocessing.value).replace("-", "_")
        )

    def get_preprocessing(
        self, preprocessing: Union[str, Preprocessing]
    ) -> PreprocessingConfig:
        
        return get_preprocessing(preprocessing)()

    def tensor_dir(self, file, preprocessing: PreprocessingConfig) -> Path:
        return (
            self.input_directory
            / container_from_filename(file)
            / "deeplearning_prepare_data"
            / "image_based"
            / preprocessing.compute_folder(False)
        )
    
    def get_input_files(
        self, preprocessing: PreprocessingConfig, data_tsv: Optional[Path] = None
    ):
        subjects, sessions = get_subject_session_list(
            self.input_directory, data_tsv, False, False, None
        )
        logger.debug(f"List of subjects: \n{subjects}.")
        logger.debug(f"List of sessions: \n{sessions}.")

        file_type = preprocessing.get_filetype()

        input_files = clinicadl_file_reader(
            subjects, sessions, self.input_directory, file_type.model_dump()
        )[0]
        logger.debug(f"Selected image file name list: {input_files}.")

        return input_files
    

class BidsReader(Reader):
    """Reader class for BIDS directories."""
    def __init__(self, input_dir: Path) -> None:
        super().__init__(input_dir)

    def subject_path(self, **kwargs)-> Path:
        return Path("")
       