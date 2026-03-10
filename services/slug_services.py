import re
import time

def generate_slug(title):

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    return f"{slug}-{int(time.time())}"