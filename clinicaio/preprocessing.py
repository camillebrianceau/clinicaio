import abc
from logging import getLogger
from pathlib import Path
from typing import Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, computed_field

from .enum import (
    DTIMeasure,
    DTISpace,
    ImageModality,
    LinearModality,
    Preprocessing,
    SUVRReferenceRegions,
    Tracer,
)
from .file_type import FileType

logger = getLogger("clinicadl.modality_config")


class PreprocessingConfig(BaseModel):
    """
    Abstract config class for the preprocessing procedure.
    """

    from_bids: bool = False
    preprocessing: Preprocessing
    use_uncropped_image: bool = False

    # pydantic config
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @abc.abstractmethod
    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        """Abstract method to get the BIDS filetype."""
        pass

    @abc.abstractmethod
    def caps_nii(self) -> tuple:
        """Abstract method to retrieve CAPS file information."""
        pass

    @abc.abstractmethod
    def get_filetype(self) -> FileType:
        """Abstract method to obtain FileType details."""
        pass

    def compute_folder(self, from_bids: bool = False) -> str:
        return (
            self.preprocessing.value
            if from_bids
            else self.preprocessing.value.replace("-", "_")
        )

    @computed_field
    @property
    def file_type(self) -> FileType:
        if self.from_bids:
            return self.bids_nii()
        elif self.preprocessing not in Preprocessing:
            raise NotImplementedError(
                f"Extraction of preprocessing {self.preprocessing.value} is not implemented from CAPS directory."
            )
        else:
            return self.get_filetype()

    def linear_nii(self) -> FileType:
        """
        Constructs the file type for linear caps image data
        """
        needed_pipeline, modality = self.caps_nii()
        desc_crop = "" if self.use_uncropped_image else "_desc-Crop"

        file_type = FileType(
            pattern=f"*space-MNI152NLin2009cSym{desc_crop}_res-1x1x1_{modality.value}.nii.gz",
            description=f"{modality.value} Image registered in MNI152NLin2009cSym space using {needed_pipeline.value} pipeline "
            + (
                ""
                if self.use_uncropped_image
                else "and cropped (matrix size 169×208×179, 1 mm isotropic voxels)"
            ),
            needed_pipeline=needed_pipeline,
        )
        return file_type


class PETPreprocessingConfig(PreprocessingConfig):
    """
    Configuration for PET image preprocessing
    """

    tracer: Tracer = Tracer.FFDG
    suvr_reference_region: SUVRReferenceRegions = SUVRReferenceRegions.CEREBELLUMPONS2
    preprocessing: Preprocessing = Preprocessing.PET_LINEAR

    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        trc, rec, description = "", "", "PET data"
        if self.tracer:
            description += f" with {self.tracer.value} tracer"
            trc = f"_trc-{self.tracer.value}"
        if reconstruction:
            description += f" and reconstruction method {reconstruction}"
            rec = f"_rec-{reconstruction}"

        return FileType(pattern=f"pet/*{trc}{rec}_pet.nii*", description=description)

    def caps_nii(self) -> Tuple[Preprocessing, ImageModality]:
        return (self.preprocessing, ImageModality.PET)

    def get_filetype(self) -> FileType:
        des_crop = "" if self.use_uncropped_image else "_desc-Crop"

        return FileType(
            pattern=f"pet_linear/*_trc-{self.tracer.value}_space-MNI152NLin2009cSym{des_crop}_res-1x1x1_suvr-{self.suvr_reference_region.value}_pet.nii.gz",
            description="",
            needed_pipeline="pet-linear",
        )


class CustomPreprocessingConfig(PreprocessingConfig):
    """
    Configuration for custom preprocessing with a user-defined suffix.
    """

    custom_suffix: str = ""
    preprocessing: Preprocessing = Preprocessing.CUSTOM

    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        return FileType(
            pattern=f"*{self.custom_suffix}",
            description="Custom suffix",
        )

    def caps_nii(self) -> tuple:
        return (self.preprocessing, ImageModality.CUSTOM)

    def get_filetype(self) -> FileType:
        return self.bids_nii()


class DTIPreprocessingConfig(PreprocessingConfig):
    """
    Configuration for DTI-based preprocessing
    """

    dti_measure: DTIMeasure = DTIMeasure.FRACTIONAL_ANISOTROPY
    dti_space: DTISpace = DTISpace.ALL
    preprocessing: Preprocessing = Preprocessing.DWI_DTI

    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        return FileType(pattern="dwi/sub-*_ses-*_dwi.nii*", description="DWI NIfTI")

    def caps_nii(self) -> tuple:
        return (self.preprocessing, ImageModality.DWI)

    def get_filetype(self) -> FileType:
        """Return the query dict required to capture DWI DTI images.

        Parameters
        ----------
        config: DTIPreprocessingConfig

        Returns
        -------
        FileType :
        """
        measure = self.dti_measure
        space = self.dti_space

        return FileType(
            pattern=f"dwi/dti_based_processing/*/*_space-{space}_{measure.value}.nii.gz",
            description=f"DTI-based {measure.value} in space {space}.",
            needed_pipeline="dwi_dti",
        )


class T1PreprocessingConfig(PreprocessingConfig):
    preprocessing: Preprocessing = Preprocessing.T1_LINEAR

    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        return FileType(pattern="anat/sub-*_ses-*_T1w.nii*", description="T1w MRI")

    def caps_nii(self) -> tuple:
        return (self.preprocessing, LinearModality.T1W)

    def get_filetype(self) -> FileType:
        return self.linear_nii()


class FlairPreprocessingConfig(PreprocessingConfig):
    preprocessing: Preprocessing = Preprocessing.FLAIR_LINEAR

    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        return FileType(pattern="sub-*_ses-*_flair.nii*", description="FLAIR T2w MRI")

    def caps_nii(self) -> tuple:
        return (self.preprocessing, LinearModality.T2W)

    def get_filetype(self) -> FileType:
        return self.linear_nii()


class T2PreprocessingConfig(PreprocessingConfig):
    preprocessing: Preprocessing = Preprocessing.T2_LINEAR

    def bids_nii(self, reconstruction: Optional[str] = None) -> FileType:
        raise NotImplementedError(
            f"Extraction of preprocessing {self.preprocessing.value} is not implemented from BIDS directory."
        )

    def caps_nii(self) -> tuple:
        return (self.preprocessing, LinearModality.FLAIR)

    def get_filetype(self) -> FileType:
        return self.linear_nii()


ALL_PREPROCESSING_TYPES = Union[
    T1PreprocessingConfig,
    T2PreprocessingConfig,
    FlairPreprocessingConfig,
    PETPreprocessingConfig,
    CustomPreprocessingConfig,
    DTIPreprocessingConfig,
]


def get_preprocessing(
    preprocessing_type: Union[str, Preprocessing],
) -> type[ALL_PREPROCESSING_TYPES]:
    preprocessing_type = Preprocessing(preprocessing_type)
    if preprocessing_type == Preprocessing.T1_LINEAR:
        return T1PreprocessingConfig
    elif preprocessing_type == Preprocessing.PET_LINEAR:
        return PETPreprocessingConfig
    elif preprocessing_type == Preprocessing.FLAIR_LINEAR:
        return FlairPreprocessingConfig
    elif preprocessing_type == Preprocessing.CUSTOM:
        return CustomPreprocessingConfig
    elif preprocessing_type == Preprocessing.DWI_DTI:
        return DTIPreprocessingConfig
    else:
        raise ValueError(
            f"Preprocessing {preprocessing_type.value} is not implemented."
        )