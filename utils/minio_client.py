import uuid
import os
from minio import Minio
from django.conf import settings


def get_minio_client():
    # AWS_S3_ENDPOINT_URL = 'http://16.170.235.75:9000'
    endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
    
    return Minio(
        endpoint   = endpoint,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure     = settings.AWS_S3_ENDPOINT_URL.startswith('https'),
    )


def upload_to_minio(file, folder: str, content_type: str = "application/octet-stream") -> str:
    client = get_minio_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    ext         = os.path.splitext(file.name)[1]
    filename    = f"{uuid.uuid4()}{ext}"
    object_name = f"{folder}/{filename}"

    client.put_object(
        bucket_name  = bucket,
        object_name  = object_name,
        data         = file,
        length       = -1,
        part_size    = 10 * 1024 * 1024,
        content_type = content_type,
    )

    return object_name  # "lessons/videos/uuid.mp4"


def upload_video_to_minio(file) -> str:
    return upload_to_minio(file, folder="lessons/videos", content_type="video/mp4")


def upload_image_to_minio(file) -> str:
    return upload_to_minio(file, folder="images", content_type="image/jpeg")