import json
import os
import errno


DEFAULT_DATA_FILE = os.path.expanduser('~/.journal_lib.json')


def get_data_file_path(custom_path=None):
    if custom_path:
        return custom_path
    return DEFAULT_DATA_FILE


def load_data(file_path=None):
    path = get_data_file_path(file_path)
    if not os.path.exists(path):
        return {'journals': []}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'journals' not in data:
                data['journals'] = []
            return data
    except json.JSONDecodeError:
        return {'journals': []}
    except IOError as e:
        if e.errno == errno.ENOENT:
            return {'journals': []}
        raise


def save_data(data, file_path=None):
    path = get_data_file_path(file_path)
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_journals(file_path=None):
    data = load_data(file_path)
    return data.get('journals', [])


def save_journals(journals, file_path=None):
    data = load_data(file_path)
    data['journals'] = journals
    save_data(data, file_path)


def clear_data(file_path=None):
    path = get_data_file_path(file_path)
    if os.path.exists(path):
        os.remove(path)
