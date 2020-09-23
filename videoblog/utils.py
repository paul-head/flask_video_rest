import os
from flask import current_app
from .tasks import upload


def upload_file(file, user_id, video_id, field="url"):
    dir_path = f"{current_app.root_path}/tmp/"
    local_path = f"{dir_path}{file.filename}"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file.save()

    upload.apply_async(
        args=[
            video_id,
            local_path,
            f"videoblog/{user_id}/{video_id}-{file.filename}",
            field,
        ]
    )
