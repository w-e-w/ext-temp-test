from pathlib import Path
import json
import datetime
import validate_json

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


def read_extension_dir():
    extensions = {}
    for f in Path('./extensions/extensions').iterdir():
        if f.is_file() and f.suffix.lower() == '.json':        
            extension = read_extension(f)
            extensions[extension['url']] = extension
    return extensions


def update_index(index_path: Path, exts: dict, tags: dict):
    with open(index_path, 'r') as f:
        existing_extensions = {extension['url']: extension for extension in json.load(f)['extensions']}

    # update existing remove removed and add new extensions
    for extensions_url, extension in exts.items():
        if extensions_url in existing_extensions.keys():
            existing_extensions[extensions_url].update(extension)
        else:
            existing_extensions[extensions_url] = extension
    extensions_list = [extension for extensions_url, extension in existing_extensions.items() if extensions_url in extensions]
    extension_index = {'tags': tags, 'extensions': extensions_list}

    with open(index_path, 'w') as f:
        json.dump(extension_index, f, indent=4)
    return extension_index


if __name__ == "__main__":
    # read tads
    with open(Path('./extensions/tags.json'), 'r') as f:
        tags = json.load(f)

    # read entries
    extensions = read_extension_dir()

    # update indexs
    extension_index_ext = update_index(Path('./extensions/index.json'), extensions, tags)
    extension_index_master = update_index(Path('./master/index.json'), extensions, tags)

    # validate
    validate_json.validate_index('./extensions/index.json')
    validate_json.validate_index('./master/index.json')

    assert len(extension_index_ext["extensions"]) == len(extension_index_master["extensions"]), f'entry count mismatch: {len(extension_index_ext["extensions"])} {len(extension_index_master["extensions"])}'
    print(f'{len(tags)} tags, {len(extension_index_ext["extensions"])} extensions')    
