from apps.courses.models import Technology


def get_technologies_by_category():
    """
    Returns technologies grouped by category in the format:
    [
        {
            "label": "Frontend",
            "options": [
                {"label": "React", "value": "react"},
                {"label": "Vue", "value": "vue"}
            ]
        },
        {
            "label": "Backend",
            "options": [
                {"label": "Node.js", "value": "node"},
                {"label": "Django", "value": "django"}
            ]
        }
    ]
    """
    technologies = Technology.objects.all().order_by('category', 'label')

    # Group by category
    categories = {}
    for tech in technologies:
        category_display = tech.get_category_display()
        if category_display not in categories:
            categories[category_display] = []

        categories[category_display].append({
            "label": tech.label,
            "value": tech.value
        })

    # Convert to the requested format
    result = []
    for category_label, options in categories.items():
        result.append({
            "label": category_label,
            "options": options
        })

    return result

import subprocess
import tempfile
import os

def get_video_duration(video_file) -> int:
    """
    Video fayldan duration ni soniyada qaytaradi.
    ffprobe ishlatadi (ffmpeg paketi kerak: apt install ffmpeg)
    """
    try:
        suffix = os.path.splitext(video_file.name)[-1] or '.mp4'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in video_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                tmp_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        os.unlink(tmp_path)  # Vaqtinchalik faylni o'chirish

        duration_str = result.stdout.decode().strip()
        if duration_str:
            return int(float(duration_str))  # soniyaga aylantirish
    except Exception as e:
        print(f"Duration olishda xato: {e}")
    return 0