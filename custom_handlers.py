import os
import time
from logging.handlers import TimedRotatingFileHandler
from cloud.azure.blob_storage import upload_logs_blob


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, maxDays=7, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDays = maxDays

    def doRollover(self):
        super().doRollover()
        self.upload_old_logs()

    def upload_old_logs(self):
        current_time = time.time()
        for filename in os.listdir(os.path.dirname(self.baseFilename)):
            if filename == ".gitignore" or filename == "app.log":
                continue
            file_path = os.path.join(
                os.path.dirname(self.baseFilename), filename)
            if os.path.isfile(file_path):
                file_creation_time = os.path.getctime(file_path)
                if (current_time - file_creation_time) // (24 * 3600) >= self.maxDays:
                    self.upload_to_azure(file_path, filename)
                    os.remove(file_path)

    def upload_to_azure(self, file_path, filename):
        with open(file_path, "rb") as data:
            upload_logs_blob(data.read(), filename)
