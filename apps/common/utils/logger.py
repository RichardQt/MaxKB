from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import os
import logging
import shutil

maxkb_logger = logging.getLogger('max_kb')


class DailyTimedRotatingFileHandler(TimedRotatingFileHandler):
    def rotator(self, source, dest):
        """ Override the original method to rotate the log file daily."""
        dest = self._get_rotate_dest_filename(source)
        if os.path.exists(source) and not os.path.exists(dest):
            # 存在多个服务进程时, 保证只有一个进程成功 rotate
            try:
                os.rename(source, dest)
            except PermissionError:
                # Windows 上文件被占用时，使用复制+截断以避免崩溃
                try:
                    shutil.copy2(source, dest)
                    with open(source, 'w'):
                        pass
                except Exception as exc:
                    maxkb_logger.warning(
                        "Log rotation skipped due to file lock: %s -> %s (%s)",
                        source,
                        dest,
                        exc,
                    )

    @staticmethod
    def _get_rotate_dest_filename(source):
        date_yesterday = (
            datetime.now() - timedelta(days=1)
        ).strftime('%Y-%m-%d')
        path = [
            os.path.dirname(source),
            date_yesterday,
            os.path.basename(source)
        ]
        filename = os.path.join(*path)
        os.makedirs(os.path.dirname(filename), 0o700, exist_ok=True)
        return filename
