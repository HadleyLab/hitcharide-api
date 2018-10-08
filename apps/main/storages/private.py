from django.conf import settings
from django.utils.functional import LazyObject
from django.core.files.storage import DefaultStorage
from storages.backends.s3boto3 import S3Boto3Storage


class PrivateStorage(LazyObject):
    def _setup(self):
        storage = DefaultStorage()

        private_bucket = settings.AWS_STORAGE_BUCKET_NAME
        if private_bucket:  # pragma: no cover
            storage = S3Boto3Storage(bucket=private_bucket)

        self._wrapped = storage


private_storage = PrivateStorage()
