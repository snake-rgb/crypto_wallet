import boto3
from dependency_injector import containers, providers
from config import settings
from src.boto3.repositories.repository import Boto3Repository

from src.boto3.services.boto3 import Boto3Service


class Boto3Container(containers.DeclarativeContainer):
    session = providers.Dependency()
    boto3_client = providers.Singleton(
        boto3.client,
        service_name='s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='eu-north-1',
        config=boto3.session.Config(signature_version='s3v4'),
    )
    boto3_repository = providers.Factory(Boto3Repository, session)
    boto3_service = providers.Factory(Boto3Service, boto3_repository, boto3_client)
