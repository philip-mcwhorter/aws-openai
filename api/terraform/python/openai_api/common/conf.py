# -*- coding: utf-8 -*-
# pylint: disable=no-member
# pylint: disable=E0213,C0103
"""
Configuration for Lambda functions.

This module is used to configure the Lambda functions. It uses the pydantic_settings
library to validate the configuration values. The configuration values are read from
environment variables, or alternatively these can be set when instantiating Settings().
"""

import logging

# python stuff
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this Lambda runs on
from typing import List, Optional

# 3rd party stuff
import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

# our stuff
from openai_api.common.exceptions import (
    OpenAIAPIConfigurationError,
    OpenAIAPIValueError,
)
from pydantic import Field, ValidationError, validator
from pydantic_settings import BaseSettings


# Default values
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SettingsDefaults:
    """Default values for Settings"""

    DEBUG_MODE = False
    AWS_PROFILE = None
    AWS_REGION = "us-east-1"
    AWS_DYNAMODB_TABLE_ID = "rekognition"
    AWS_REKOGNITION_COLLECTION_ID = AWS_DYNAMODB_TABLE_ID + "-collection"
    AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT = 10
    AWS_REKOGNITION_FACE_DETECT_THRESHOLD = 10
    AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES = "DEFAULT"
    AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER = "AUTO"
    LANGCHAIN_MEMORY_KEY = "chat_history"
    OPENAI_API_ORGANIZATION = None
    OPENAI_API_KEY = None
    OPENAI_ENDPOINT_IMAGE_N = 4
    OPENAI_ENDPOINT_IMAGE_SIZE = "1024x768"
    PINECONE_API_KEY = None


ec2 = boto3.Session().client("ec2")
regions = ec2.describe_regions()
AWS_REGIONS = [region["RegionName"] for region in regions["Regions"]]


def empty_str_to_bool_default(v: str, default: bool) -> bool:
    """Convert empty string to default boolean value"""
    if v in [None, ""]:
        return default
    return v.lower() in ["true", "1", "t", "y", "yes"]


def empty_str_to_int_default(v: str, default: int) -> int:
    """Convert empty string to default integer value"""
    if v in [None, ""]:
        return default
    try:
        return int(v)
    except ValueError:
        return default


class Settings(BaseSettings):
    """Settings for Lambda functions"""

    _aws_session: boto3.Session = None

    debug_mode: Optional[bool] = Field(
        SettingsDefaults.DEBUG_MODE,
        env="DEBUG_MODE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DEBUG_MODE),
    )
    aws_profile: Optional[str] = Field(
        SettingsDefaults.AWS_PROFILE,
        env="AWS_PROFILE",
    )
    aws_regions: Optional[List[str]] = Field(AWS_REGIONS, description="The list of AWS regions")
    aws_region: Optional[str] = Field(
        SettingsDefaults.AWS_REGION,
        env="AWS_REGION",
    )
    aws_dynamodb_table_id: Optional[str] = Field(
        SettingsDefaults.AWS_DYNAMODB_TABLE_ID,
        env="AWS_DYNAMODB_TABLE_ID",
    )
    aws_rekognition_collection_id: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID,
        env="AWS_REKOGNITION_COLLECTION_ID",
    )

    aws_rekognition_face_detect_attributes: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES,
        env="AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES",
    )
    aws_rekognition_face_detect_attributes: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER,
        env="AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER",
    )
    aws_rekognition_face_detect_attributes: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT),
    )
    aws_rekognition_face_detect_attributes: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_THRESHOLD",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD),
    )
    langchain_memory_key: Optional[str] = Field(SettingsDefaults.LANGCHAIN_MEMORY_KEY, env="LANGCHAIN_MEMORY_KEY")
    openai_api_organization: Optional[str] = Field(
        SettingsDefaults.OPENAI_API_ORGANIZATION, env="OPENAI_API_ORGANIZATION"
    )
    openai_api_key: Optional[str] = Field(SettingsDefaults.OPENAI_API_KEY, env="OPENAI_API_KEY")
    openai_endpoint_image_n: Optional[str] = Field(
        SettingsDefaults.OPENAI_ENDPOINT_IMAGE_N, env="OPENAI_ENDPOINT_IMAGE_N"
    )
    openai_endpoint_image_size: Optional[str] = Field(
        SettingsDefaults.OPENAI_ENDPOINT_IMAGE_SIZE, env="OPENAI_ENDPOINT_IMAGE_SIZE"
    )
    pinecone_api_key: Optional[str] = Field(SettingsDefaults.PINECONE_API_KEY, env="PINECONE_API_KEY")

    @property
    def aws_session(self):
        """AWS session"""
        if not self._aws_session:
            if self.aws_profile:
                self._aws_session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
            else:
                self._aws_session = boto3.Session(region_name=self.aws_region)
        return self._aws_session

    @property
    def s3_client(self):
        """S3 client"""
        return self.aws_session.resource("s3")

    @property
    def dynamodb_client(self):
        """DynamoDB client"""
        return self.aws_session.resource("dynamodb")

    @property
    def rekognition_client(self):
        """Rekognition client"""
        return self.aws_session.client("rekognition")

    @property
    def dynamodb_table(self):
        """DynamoDB table"""
        return self.dynamodb_client.Table(self.aws_dynamodb_table_id)

    # use the boto3 library to initialize clients for the AWS services which we'll interact
    @property
    def cloudwatch_dump(self):
        """Dump settings to CloudWatch"""
        return {
            "environment": {
                "os": os.name,
                "system": platform.system(),
                "release": platform.release(),
                "boto3": boto3.__version__,
                "AWS_REKOGNITION_COLLECTION_ID": self.aws_rekognition_collection_id,
                "AWS_DYNAMODB_TABLE_ID": self.aws_dynamodb_table_id,
                "MAX_FACES": self.aws_rekognition_face_detect_attributes,
                "AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES": self.aws_rekognition_face_detect_attributes,
                "QUALITY_FILTER": self.aws_rekognition_face_detect_attributes,
                "DEBUG_MODE": self.debug_mode,
            }
        }

    # pylint: disable=too-few-public-methods
    class Config:
        """Pydantic configuration"""

        frozen = True

    @validator("aws_profile", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_profile(cls, v, values, **kwargs):
        """Validate aws_profile"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_PROFILE
        return v

    @validator("aws_region", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_region(cls, v, values, **kwargs):
        """Validate aws_region"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REGION
        if "aws_regions" in values and v not in values["aws_regions"]:
            raise OpenAIAPIValueError(f"aws_region {v} not in aws_regions")
        return v

    @validator("aws_dynamodb_table_id", pre=True)
    def validate_table_id(cls, v):
        """Validate aws_dynamodb_table_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_DYNAMODB_TABLE_ID
        return v

    @validator("aws_rekognition_collection_id", pre=True)
    def validate_collection_id(cls, v):
        """Validate aws_rekognition_collection_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID
        return v

    @validator("aws_rekognition_face_detect_attributes", pre=True)
    def validate_face_detect_attributes(cls, v):
        """Validate aws_rekognition_face_detect_attributes"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES
        return v

    @validator("debug_mode", pre=True)
    def parse_debug_mode(cls, v):
        """Parse debug_mode"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DEBUG_MODE
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @validator("aws_rekognition_face_detect_attributes", pre=True)
    def check_face_detect_max_faces_count(cls, v):
        """Check aws_rekognition_face_detect_attributes"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT
        return int(v)

    @validator("aws_rekognition_face_detect_attributes", pre=True)
    def check_face_detect_threshold(cls, v):
        """Check aws_rekognition_face_detect_attributes"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD
        return int(v)

    @validator("langchain_memory_key", pre=True)
    def check_langchain_memory_key(cls, v):
        """Check langchain_memory_key"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.LANGCHAIN_MEMORY_KEY
        return int(v)

    @validator("openai_api_organization", pre=True)
    def check_openai_api_organization(cls, v):
        """Check openai_api_organization"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_API_ORGANIZATION
        return int(v)

    @validator("openai_api_key", pre=True)
    def check_openai_api_key(cls, v):
        """Check openai_api_key"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_API_KEY
        return int(v)

    @validator("openai_endpoint_image_n", pre=True)
    def check_openai_endpoint_image_n(cls, v):
        """Check openai_endpoint_image_n"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_ENDPOINT_IMAGE_N
        return int(v)

    @validator("openai_endpoint_image_size", pre=True)
    def check_openai_endpoint_image_size(cls, v):
        """Check openai_endpoint_image_size"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_ENDPOINT_IMAGE_SIZE
        return int(v)

    @validator("pinecone_api_key", pre=True)
    def check_pinecone_api_key(cls, v):
        """Check pinecone_api_key"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.PINECONE_API_KEY
        return int(v)


settings = None
try:
    settings = Settings()
except ValidationError as e:
    raise OpenAIAPIConfigurationError("Invalid configuration: " + str(e)) from e

logger = logging.getLogger(__name__)
logger.debug("DEBUG_MODE: %s", settings.debug_mode)
logger.debug("AWS_REGION: %s", settings.aws_region)
logger.debug("AWS_DYNAMODB_TABLE_ID: %s", settings.aws_dynamodb_table_id)
logger.debug("AWS_REKOGNITION_COLLECTION_ID: %s", settings.aws_rekognition_collection_id)
logger.debug("AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT: %s", settings.aws_rekognition_face_detect_attributes)
logger.debug("AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES: %s", settings.aws_rekognition_face_detect_attributes)
logger.debug("AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER: %s", settings.aws_rekognition_face_detect_attributes)
logger.debug("AWS_REKOGNITION_FACE_DETECT_THRESHOLD: %s", settings.aws_rekognition_face_detect_attributes)
logger.debug("LANGCHAIN_MEMORY_KEY: %s", settings.langchain_memory_key)
logger.debug("OPENAI_API_ORGANIZATION: %s", settings.openai_api_organization)
logger.debug("OPENAI_API_KEY: %s", settings.openai_api_key)
logger.debug("OPENAI_ENDPOINT_IMAGE_N: %s", settings.openai_endpoint_image_n)
logger.debug("OPENAI_ENDPOINT_IMAGE_SIZE: %s", settings.openai_endpoint_image_size)
