import os
import pkg_resources


def load_local_resource(local_file: str, resource: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(local_file))
    prompt_template_path = os.path.join(current_dir, resource)

    if os.path.exists(prompt_template_path):
        with open(prompt_template_path, "r") as file:
            return file.read()
    else:
        return pkg_resources.resource_string(__name__, f"prompt/{resource}").decode()


def format_print_string(s: str, length: int = 100) -> str:
    # Remove newlines
    s = s.replace("\n", " ").replace("\r", "")

    if len(s) <= length:
        return s
    return s[: length - 3] + "..."
