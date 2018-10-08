from django.conf import settings
from django.utils.functional import LazyObject
from django.core.files.storage import DefaultStorage
from storages.backends.s3boto3 import S3Boto3Storage


class PublicStorage(LazyObject):
    def _setup(self):
        storage = DefaultStorage()

        public_bucket = settings.AWS_STORAGE_BUCKET_NAME
        if public_bucket:  # pragma: no cover
            storage = S3Boto3Storage(
                bucket=public_bucket, querystring_auth=False)

        self._wrapped = storage


public_storage = PublicStorage()
