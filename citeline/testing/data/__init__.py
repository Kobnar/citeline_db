import json
import pkg_resources


def _load_json_file(filename):
    path = 'testing/data/' + filename
    json_data = pkg_resources.resource_string('citeline', path)
    return json.loads(json_data.decode('utf-8'))


def _load_db_data(key):
    test_data = _load_json_file('db.json')
    return test_data[key]


def people():
    return _load_db_data('people')


def orgs():
    return _load_db_data('organizations')


def _load_validation_data(key):
    test_data = _load_json_file('validation.json')
    return test_data[key]


def valid_usernames():
    return _load_validation_data('valid_usernames')


def invalid_usernames():
    return _load_validation_data('invalid_usernames')


def valid_emails():
    return _load_validation_data('valid_emails')


def invalid_emails():
    return _load_validation_data('invalid_emails')


def valid_passwords():
    return _load_validation_data('valid_passwords')


def invalid_passwords():
    return _load_validation_data('invalid_passwords')


def valid_uris():
    return _load_validation_data('valid_uris')


def invalid_uris():
    return _load_validation_data('invalid_uris')


def valid_keys():
    return _load_validation_data('valid_keys')


def invalid_keys():
    return _load_validation_data('invalid_keys')


def valid_object_ids():
    return _load_validation_data('valid_object_ids')


def invalid_object_ids():
    return _load_validation_data('invalid_object_ids')


def valid_isbn13s():
    return _load_validation_data('valid_isbn13s')


def valid_isbn10s():
    return _load_validation_data('valid_isbn10s')


def invalid_isbns():
    return _load_validation_data('invalid_isbns')
