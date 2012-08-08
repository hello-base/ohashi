from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin

from storages.backends.s3boto import S3BotoStorage


class CachedStaticS3Storage(CachedFilesMixin, S3BotoStorage):
    def __init__(self, *args, **kwargs):
        self.bucket_name = getattr(settings, 'STATIC_STORAGE_BUCKET_NAME')
        super(CachedStaticS3Storage, self).__init__(*args, **kwargs)
