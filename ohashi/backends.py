from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin

from boto.utils import parse_ts
from storages.backends.s3boto import S3BotoStorage


class CachedStaticS3Storage(CachedFilesMixin, S3BotoStorage):
    def __init__(self, *args, **kwargs):
        self.bucket_name = getattr(settings, 'STATIC_STORAGE_BUCKET_NAME')
        super(CachedStaticS3Storage, self).__init__(*args, **kwargs)

    def save(self, name, content):
        name = super(CachedStaticS3Storage, self).save(name, content)
        self.local_storage._save(name, content)
        return name

    def modified_time(self, name):
        name = self._normalize_name(self._clean_name(name))
        entry = self.entries.get(name)
        if entry is None:
            entry = self.bucket.get_key(self._encode_name(name))
        # Parse the last_modified string to a local datetime object.
        return parse_ts(entry.last_modified)
