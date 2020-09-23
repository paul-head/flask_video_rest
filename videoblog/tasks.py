import os
from . import celery, session
from .s3client import upload_video
from .models import Video


@celery.task(name="pipeline.upload")
def upload(video_id, local_path, path, field):
    upload_video(local_path, path)
    try:
        video = Video.query.get(video_id)
        video.update(
            **{field: f"https://pvlhead.ams3.cdn.digitaloceanspaces.com/{path}"}
        )
    except Exception as e:
        session.rollback()
        return f"Uploading failed: {e}"
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
    return "success"
