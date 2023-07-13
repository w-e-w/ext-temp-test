import json
from pathlib import Path
import datetime
from re import compile
from collections import Counter

script_dir = Path(__file__).parent
git_url_pattern = compile(r'(https://[^ ]+?)(?:(?:\.git)$|$)')

def validate_index():
    with open(script_dir.joinpath('index.json')) as inf:
        d = json.load(inf)
        assert "tags" in d

        tags = set(d["tags"].keys())

        for extension in d["extensions"]:
            for required_key in [
                "name",
                "url",
                "description",
                "added",
                "tags",
            ]:
                assert required_key in extension, f"missing key: {required_key}"

            for _tag in extension["tags"]:
                assert _tag in tags

            datetime.date.fromisoformat(extension['added']), "Incorrect data format, should be YYYY-MM-DD"


with open(script_dir.joinpath('tags.json'), 'r') as f:
    tags = json.load(f)

tags_keys = tags.keys()

def validate_entry(file: Path):

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

    if extension.get('added'):
        try:
            datetime.date.fromisoformat(extension.get('added'))
        except:
            assert False, f"{file} Incorrect added data format, YYYY-MM-DD"
    git_url = git_url_pattern.match(extension['url'])
    assert git_url, f'invalid URL: "{extension["url"]}"'
    return git_url.group(1)


def validate_extension_entrys():
    urls = []
    for f in Path(script_dir.joinpath('extensions')).iterdir():
        if f.is_file() and f.suffix.lower() == '.json':        
            urls.append(validate_entry(f))
    counts = Counter(urls)
    duplicates = [element for element, count in counts.items() if count > 1]
    assert len(duplicates) == 0, f'duplicate extension: {duplicates}'


def validate():
    validate_index()
    validate_extension_entrys()

if __name__ == "__main__":
    validate()
