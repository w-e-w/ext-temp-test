from pathlib import Path
import json
import datetime
import subprocess
import validate_json


def run_command(command: list):
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, f'{["git", "switch", "master"]} {result.returncode}: {result.stderr}'
    return result


def read_extension(file: Path):
    with open(file, 'r') as f:
        extension = json.load(f)
    for required_key in [
        "name",
        "url",
        "description",
        "tags",
    ]:
        assert required_key in extension, f"{file} missing key: {required_key}"

    for _tag in extension["tags"]:
        assert _tag in tags, f'{file} tag: "{str(_tag)}" is not a valid tag'

    try:
        datetime.date.fromisoformat(extension.get('added'))
    except:
        # add "added": "YYYY-MM-DD"
        extension["added"] = str(datetime.datetime.now().date())
        with open(file, 'w') as f:
            json.dump(extension, f, indent=4)
    return extension

if __name__ == "__main__":

    run_command(["git", "config", "user.name", "'github-actions[bot]'"])
    run_command(["git", "config", "user.email", "'github-actions[bot]@users.noreply.github.com'"])

    # switch to extensions branch
    run_command(["git", "switch", "extensions"])

    with open('tags.json', 'r') as f:
        tags = json.load(f)

    tags_keys = tags.keys()

    extensions = {}
    for f in Path('extensions').iterdir():
        if f.is_file() and f.suffix.lower() == '.json':        
            extension = read_extension(f)
            extensions[extension['url']] = extension

    if run_command(["git", "status", "--short"]).stdout:
        validate_json.validate()
        run_command(["git", "commit", "--amend", "--no-edit", "--all"])
        run_command(["git", "push", "--force"])

    # switch to extensions branch
    run_command(["git", "fetch", "origin", "master", "--depth", "1"])
    run_command(["git", "switch", "master"])

    with open('index.json', 'r') as f:
        existing_extensions = {extension['url']: extension for extension in json.load(f)['extensions']}

    # update existing remove removed and add new extensions
    for extensions_url, extension in extensions.items():
        if extensions_url in existing_extensions.keys():
            existing_extensions[extensions_url].update(extension)
        else:
            existing_extensions[extensions_url] = extension
    extensions_list = [extension for extensions_url, extension in existing_extensions.items() if extensions_url in extensions]
    extension_index = {'tags': tags, 'extensions': extensions_list}

    with open('index.json', 'w') as f:
        json.dump(extension_index, f, indent=4)

    print(f'{len(tags)} tags, {len(extensions_list)} extensions')

    if run_command(["git", "status", "--short"]).stdout:
        validate_json.validate()
        run_command(["git", "commit", "--amend", "--no-edit", "--all"])
        run_command(["git", "push", "--force"])
