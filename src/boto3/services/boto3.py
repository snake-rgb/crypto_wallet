import base64
import uuid
from io import BytesIO
import logging
from botocore.exceptions import ClientError
from propan import RabbitBroker

from config import settings
from src.boto3.repositories.repository import Boto3Repository
from src.ibay.schemas import ProductSchema


class Boto3Service:

    def __init__(self, boto3_repository: Boto3Repository, boto3_client):
        self.boto3_client = boto3_client
        self.boto3_repository = boto3_repository
        self.bucket_name = 'cryptowalletbucket'

    # Temporary link on image
    def create_presigned_url(self, bucket_name, object_name, expiration):
        """Generate a presigned URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a presigned URL for the S3 object
        try:
            response = self.boto3_client.generate_presigned_url('get_object',
                                                                Params={'Bucket': bucket_name,
                                                                        'Key': object_name},
                                                                ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response

    async def upload_image(self, base64_image: str) -> str:
        # convert image to binary
        base64_image = base64_image.replace('data:image/jpeg;base64,', '')
        image_data = base64.b64decode(base64_image)

        # generate file path and name
        unique_filename = str(uuid.uuid4()) + ".jpg"
        file_path = f'images/{unique_filename}'

        # upload image and return url
        with BytesIO(image_data) as image_stream:
            self.boto3_client.upload_fileobj(image_stream, self.bucket_name, file_path)
            return await self.create_public_url(file_path)

    async def create_public_url(self, file_path) -> str:
        try:
            # set public access
            self.boto3_client.put_object_acl(
                ACL='public-read',
                Bucket=self.bucket_name,
                Key=file_path
            )
            public_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_path}"
            return public_url
        except Exception as e:
            print("Ошибка:", e)

    # async def upload_product_image(
    #         self,
    #         base64_image: str,
    #         name: str,
    #         price: float,
    #         wallet_address: str
    # ) -> None:
    #
    #     image_url: str = await self.upload_image(base64_image)
    #     print(image_url)
    #     async with RabbitBroker(settings.RABBITMQ_URL) as broker:
    #         await broker.publish(
    #             ProductSchema(
    #                 image=image_url,
    #                 name=name,
    #                 price=price,
    #                 wallet_address=wallet_address
    #             ).model_dump(),
    #             queue='upload_product_image',
    #             exchange='ibay_exchange')
