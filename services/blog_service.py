import os
import json

def get_json_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", "blog_posts.json")


def load_posts():
    json_path = get_json_path()

    if not os.path.exists(json_path):
        print("JSON file not found at:", json_path)
        return {}

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_post(slug):
    posts = load_posts()
    print("Loaded posts:", posts)
    print("Looking for slug:", slug)
    return posts.get(slug)