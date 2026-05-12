import uuid
import os
from minio import Minio
from django.conf import settings


def get_minio_client():
    endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
    
    return Minio(
        endpoint   = endpoint,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure     = settings.AWS_S3_ENDPOINT_URL.startswith('https'),
    )


def upload_to_minio(file, folder: str, content_type: str = "application/octet-stream") -> str:
    """
    Fayl yuklash — folder beriladi, filename UUID bilan avtomatik yasaladi.
    Qaytaradi: "folder/uuid.ext"
    """
    client = get_minio_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    ext         = os.path.splitext(file.name)[1]
    filename    = f"{uuid.uuid4()}{ext}"
    object_name = f"{folder}/{filename}"

    file.seek(0)
    client.put_object(
        bucket_name  = bucket,
        object_name  = object_name,
        data         = file,
        length       = -1,
        part_size    = 10 * 1024 * 1024,
        content_type = content_type,
    )

    return object_name


def upload_to_minio_with_key(file, object_name: str, content_type: str = "application/octet-stream") -> str:
    """
    To'liq object_name bilan yuklash — UUID qo'shilmaydi, nom siz belgilagan bo'ladi.
    Qaytaradi: berilgan object_name
    """
    client = get_minio_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    file.seek(0)
    client.put_object(
        bucket_name  = bucket,
        object_name  = object_name,
        data         = file,
        length       = -1,
        part_size    = 10 * 1024 * 1024,
        content_type = content_type,
    )

    return object_name


def delete_from_minio(object_name: str) -> bool:
    """
    MinIO dan fayl o'chirish.
    Qaytaradi: True (muvaffaqiyatli) yoki False (xato)
    """
    try:
        client = get_minio_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        client.remove_object(bucket, object_name)
        return True
    except Exception:
        return False


def get_minio_url(object_name: str) -> str:
    """
    Fayl uchun to'liq URL qaytaradi.
    """
    base_url = settings.AWS_S3_ENDPOINT_URL.rstrip('/')
    bucket   = settings.AWS_STORAGE_BUCKET_NAME
    return f"{base_url}/{bucket}/{object_name}"


# --- Qisqa helper funksiyalar ---

def upload_video_to_minio(file) -> str:
    """Video yuklash — lessons/videos/ papkasiga, UUID nom bilan"""
    return upload_to_minio(file, folder="lessons/videos", content_type="video/mp4")


def upload_image_to_minio(file) -> str:
    """Rasm yuklash — images/ papkasiga, UUID nom bilan"""
    return upload_to_minio(file, folder="images", content_type="image/jpeg")


def upload_project_video_to_minio(file, project_slug: str, order: int) -> str:
    """
    Project step videosi yuklash — aniq nom bilan.
    Natija: "projects/videos/{slug}/step-{order}.mp4"
    """
    object_name = f"projects/videos/{project_slug}/step-{order}.mp4"
    return upload_to_minio_with_key(file, object_name, content_type="video/mp4")


def upload_project_image_to_minio(file, project_slug: str) -> str:
    """
    Project rasmi yuklash — UUID nom bilan.
    Natija: "projects/images/{slug}/uuid.ext"
    """
    return upload_to_minio(file, folder=f"projects/images/{project_slug}", content_type="image/jpeg")