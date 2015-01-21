from .s3_boto import S3BotoStorage

class GzipCompressorFileStorage(S3BotoStorage):
    """
    The standard compressor file system storage that gzips storage files
    additionally to the usual files.
    """
    def _save(self, *args, **kwargs):
        self.gzip = True # Set true here instead of in the settings file to avoid globally gzipping anything sent to s3.
                         # Gzipping doesn't make sense for image formats.
        return super(GzipCompressorFileStorage, self)._save(*args, **kwargs)