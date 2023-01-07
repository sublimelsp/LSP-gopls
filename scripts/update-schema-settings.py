#! /usr/local/bin/python3

from typing import Union, Dict
import subprocess
import json
import os

PACKAGE_PATH = os.path.join(os.path.dirname(__file__), '..')

SCHEMA_TEMPLATE = {
    'contributions': {
        'settings': [
            {
                'file_patterns': ['/LSP-gopls.sublime-settings'],
                'schema': {
                    '$id': 'sublime://settings/LSP-gopls',
                    'definitions': {
                        'PluginConfig': {
                            'properties': {
                                'initializationOptions': {
                                    'additionalProperties': False,
                                    'type': 'object',
                                    'properties': {},
                                },
                                'settings': {
                                    'additionalProperties': False,
                                    'type': 'object',
                                    'properties': {},
                                },
                            }
                        }
                    },
                    'allOf': [
                        {'$ref': 'sublime://settings/LSP-plugin-base'},
                        {
                            '$ref': 'sublime://settings/LSP-gopls#/definitions/PluginConfig'
                        },
                    ],
                },
            },
            {
                'file_patterns': ['/*.sublime-project'],
                'schema': {
                    'properties': {
                        'settings': {
                            'properties': {
                                'LSP': {
                                    'properties': {
                                        'gopls': {
                                            '$ref': 'sublime://settings/LSP-gopls#/definitions/PluginConfig'
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        ],
    },
}

TYPE_MAP = {
    '[]string': 'array',
    'map[string]string': 'object',
    'enum': 'enum',
    'bool': 'boolean',
    'string': 'string',
    'time.Duration': 'string',
    'map[string]bool': 'object',
    # Handle bug in api-json command of gopls
    '': 'boolean',
}

# Custom LSP-gopls settings not provided by gopls directly
CUSTOM_PROPERTIES = {
    'closeTestResultsWhenFinished': {
        'default': False,
        'markdownDescription': 'Controls if the Terminus panel/tab will auto close on tests completing.\n',
        'type': 'boolean',
    },
    'runTestsInPanel': {
        'default': True,
        'markdownDescription': 'Controls if the test results output to a panel instead of a tab.\n',
        'type': 'boolean',
    },
}

BEGIN_LSP_GOPLS_SETTINGS = '''// Packages/User/LSP-gopls.sublime-settings
{
  "command": [
    "${storage_path}/LSP-gopls/bin/gopls"
  ],
  "selector": "source.go | source.gomod",
  "settings": {
'''
PREFIX_LSP_GOPLS_SETTINGS = '    '
END_LSP_GOPLS_SETTINGS = '''
  }
}
'''


class GoplsGenerator:
    def __init__(self) -> None:
        self.schema = SCHEMA_TEMPLATE
        self.properties = CUSTOM_PROPERTIES
        self.gopls_settings = ''

    @classmethod
    def _get_gopls_api_docs(cls) -> Union[str, None]:
        process = subprocess.Popen(
            ['gopls', 'api-json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        if stderr:
            print(stderr)
            return None
        return stdout

    @classmethod
    def to_json(cls, content: str) -> Dict:
        return json.loads(content)

    def generate_schema(self):
        data = self._get_gopls_api_docs()
        if data is None:
            return

        raw_schema = self.to_json(data)
        raw_settings = raw_schema['Options']['User']
        for _, value in enumerate(raw_settings):
            current_key = f"gopls.{value['Name']}"
            current_type = TYPE_MAP[value['Type']]
            resolved_type = current_type

            if resolved_type == 'enum':
                resolved_type = 'string'

            markdown_description = value['Doc']
            if value.get('Status', '') != '':
                markdown_description = f"({value.get('Status', '')}) {value['Doc']}"

            self.properties[current_key] = {
                'type': resolved_type,
                'default': json.loads(value['Default']),
                'markdownDescription': markdown_description,
            }

            if current_type == 'enum':
                self.properties[current_key]['enum'] = []
                self.properties[current_key]['markdownEnumDescriptions'] = []
                for _, enum in enumerate(value['EnumValues']):
                    self.properties[current_key]['enum'].append(
                        json.loads(enum['Value'])
                    )
                    self.properties[current_key]['markdownEnumDescriptions'].append(
                        enum.get('Doc', '').removeprefix('`{}`: '.format(enum['Value']))
                    )
            elif current_type == 'object':
                self.properties[current_key]['properties'] = {}
                keys = value['EnumKeys']['Keys']
                if keys is None:
                    continue

                enum_type = TYPE_MAP[value['EnumKeys'].get('ValueType', 'bool')]
                for _, enum in enumerate(keys):
                    property_name = json.loads(enum['Name'])
                    self.properties[current_key]['properties'][property_name] = {
                        'markdownDescription': enum['Doc'],
                        'type': enum_type,
                        'default': json.loads(enum['Default']),
                    }
        self.schema['contributions']['settings'][0]['schema']['definitions'][
            'PluginConfig'
        ]['properties']['settings']['properties'] = self.properties
        return self.schema

    def generate_lsp_settings(self) -> str:
        properties = self.schema['contributions']['settings'][0]['schema'][
            'definitions'
        ]['PluginConfig']['properties']['settings']['properties']
        compiled_settings = ''
        for prop in properties:
            lines = '\n'.join(
                [
                    f'{PREFIX_LSP_GOPLS_SETTINGS}// {line}'.rstrip()
                    for line in properties[prop]['markdownDescription'].split('\n')
                ][:-1]
            )
            defaults = json.dumps(properties[prop]["default"], indent=2)
            defaults = '\n'.join(
                [f'{PREFIX_LSP_GOPLS_SETTINGS}{line}' for line in defaults.split('\n')]
            )
            defaults = f'{PREFIX_LSP_GOPLS_SETTINGS}"{prop}": {defaults.lstrip()},'
            compiled_settings += lines + '\n' + defaults + '\n'
        self.gopls_settings = (
            BEGIN_LSP_GOPLS_SETTINGS
            + compiled_settings.rstrip()
            + END_LSP_GOPLS_SETTINGS
        )
        return self.gopls_settings

    def write_schema_out(self, path: str):
        with open(path, 'w') as outfile:
            outfile.write(json.dumps(self.schema, indent=2) + '\n')

    def write_settings_out(self, path: str):
        with open(path, 'w') as outfile:
            outfile.write(self.gopls_settings)


def main():
    processor = GoplsGenerator()
    sublime_package_schema = processor.generate_schema()
    if sublime_package_schema is None:
        return

    processor.write_schema_out(os.path.join(PACKAGE_PATH, 'sublime-package.json'))

    settings = processor.generate_lsp_settings()
    if settings == '':
        return None

    processor.write_settings_out(os.path.join(PACKAGE_PATH, '/LSP-gopls.sublime-settings'))


main()
