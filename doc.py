from typing import Union, Dict
import ast
import subprocess
import json

DEFAULT = {
    'contributions': {
        'settings': [
          {
              'file_patterns': [
                  '/LSP-gopls.sublime-settings'
              ],
              'schema': {
                  '$id': 'sublime://settings/LSP-gopls',
                  'definitions': {
                      'PluginConfig': {
                          'properties': {
                              'initializationOptions': {
                                  'additionalProperties': False,
                                  'type': 'object',
                                  'properties': {
                                  }
                              },
                              'settings': {
                                  'additionalProperties': False,
                                  'type': 'object',
                                  'properties': {}
                              }
                          }
                      }
                  },
                  'allOf': [
                      {
                          '$ref': 'sublime://settings/LSP-plugin-base'
                      },
                      {
                          '$ref': 'sublime://settings/LSP-gopls#/definitions/PluginConfig'
                      }
                  ]
              }
          },
            {
              'file_patterns': [
                  '/*.sublime-project'
              ],
              'schema': {
                  'properties': {
                      'settings': {
                          'properties': {
                              'LSP': {
                                  'properties': {
                                      'gopls': {
                                          '$ref': 'sublime://settings/LSP-gopls#/definitions/PluginConfig'
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
          }
        ]
    }
}

CUSTOM_SETTINGS = {
    'closeTestResultsWhenFinished': {
        'default': False,
        'markdownDescription': 'Controls if the Terminus panel/tab will auto close on tests completing.',
        'type': 'boolean'
    },
    'runTestsInPanel': {
        'default': True,
        'markdownDescription': 'Controls if the test results output to a panel instead of a tab.',
        'type': 'boolean'
    }
}

TYPE_MAP = {
    '[]string': 'array',
    'map[string]string': 'object',
    'enum': 'enum',
    'bool': 'boolean',
    'string': 'string',
    'time.Duration': 'string',
    'map[string]bool': 'object',
    '': 'boolean'
}


def gopls_api_docs() -> Union[Dict, str]:
    process = subprocess.Popen(
        ['gopls', 'api-json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    if stderr:
        return stderr

    settings = DEFAULT

    raw_settings = json.loads(stdout)
    properties = CUSTOM_SETTINGS
    for _, value in enumerate(raw_settings['Options']['User']):
        current_type = TYPE_MAP[value['Type']]
        properties[f"gopls.{value['Name']}"] = {}
        if current_type in ('string',  'array', 'boolean'):
            properties[f"gopls.{value['Name']}"]['type'] = current_type
            properties[f"gopls.{value['Name']}"]['default'] = json.loads(
                value['Default'])
            properties[f"gopls.{value['Name']}"]['markdownDescription'] = value['Doc'] if value.get(
                'Status', '') == '' else f"({value.get('Status', '')}) {value['Doc']}"
        elif current_type == 'enum':
            properties[f"gopls.{value['Name']}"]['type'] = current_type
            properties[f"gopls.{value['Name']}"]['default'] = json.loads(
                value['Default']),
            properties[f"gopls.{value['Name']}"]['markdownDescription'] = value['Doc'] if value.get(
                'Status', '') == '' else f"({value.get('Status', '')}) {value['Doc']}"
            properties[f"gopls.{value['Name']}"]['enum'] = []
            properties[f"gopls.{value['Name']}"]['markdownEnumDescriptions'] = [
            ]
            for _, enum in enumerate(value['EnumValues']):
                properties[f"gopls.{value['Name']}"]['enum'].append(
                    json.loads(enum['Value']))
                properties[f"gopls.{value['Name']}"]['markdownEnumDescriptions'].append(
                    enum.get('Doc', ''))
        elif current_type == 'object':
            properties[f"gopls.{value['Name']}"]['type'] = current_type
            properties[f"gopls.{value['Name']}"]['markdownDescription'] = value['Doc'] if value.get(
                'Status', '') == '' else f"({value.get('Status', '')}) {value['Doc']}"
            properties[f"gopls.{value['Name']}"]['default'] = json.loads(
                value['Default'])
            properties[f"gopls.{value['Name']}"]['properties'] = {}
            keys = value['EnumKeys']['Keys']
            if keys is not None:
                enum_type = TYPE_MAP[value['EnumKeys'].get(
                    'ValueType', 'bool')]
                for _, enum in enumerate(keys):
                    property_name = json.loads(enum['Name'])
                    properties[f"gopls.{value['Name']}"]['properties'][property_name] = {
                        'markdownDescription': enum['Doc'],
                        'type': enum_type,
                        'default': json.loads(enum['Default'])
                    }

    settings['contributions']['settings'][0]['schema']['definitions']['PluginConfig']['properties']['settings']['properties'] = properties
    return settings


def main():
    sublime_package_content = gopls_api_docs()
    with open('sublime-package.json', 'w') as outfile:
        outfile.write(json.dumps(sublime_package_content, indent=2))

main()
