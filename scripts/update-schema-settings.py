#! /usr/local/bin/python3

import json
import os
import subprocess
from typing import Dict, Union

PACKAGE_PATH = os.path.join(os.path.dirname(__file__), "..")

SCHEMA_TEMPLATE = {
    "contributions": {
        "settings": [
            {
                "file_patterns": ["/LSP-gopls.sublime-settings"],
                "schema": {
                    "$id": "sublime://settings/LSP-gopls",
                    "definitions": {
                        "PluginConfig": {
                            "properties": {
                                "initializationOptions": {
                                    "additionalProperties": False,
                                    "type": "object",
                                    "properties": {},
                                },
                                "settings": {
                                    "additionalProperties": False,
                                    "type": "object",
                                    "properties": {},
                                },
                            }
                        }
                    },
                    "allOf": [
                        {"$ref": "sublime://settings/LSP-plugin-base"},
                        {
                            "$ref": "sublime://settings/LSP-gopls#/definitions/PluginConfig"
                        },
                    ],
                },
            },
            {
                "file_patterns": ["/*.sublime-project"],
                "schema": {
                    "properties": {
                        "settings": {
                            "properties": {
                                "LSP": {
                                    "properties": {
                                        "gopls": {
                                            "$ref": "sublime://settings/LSP-gopls#/definitions/PluginConfig"
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
    "any": "any",
    "[]string": "array",
    "map[string]string": "object",
    "map[enum]bool": "object",
    "enum": "enum",
    "bool": "boolean",
    "string": "string",
    "time.Duration": "string",
    "map[string]bool": "object",
    # Handle bug in api-json command of gopls
    "": "boolean",
}

TYPE_OVERRIDE_BY_KEY = {
    "gopls.linksInHover": ["string", "boolean"],
}

# Custom LSP-gopls settings not provided by gopls directly
CUSTOM_PROPERTIES = {
    "manageGoplsBinary": {
        "default": True,
        "markdownDescription": "Controls if LSP-gopls will automatically install and upgrade gopls.\nIf this option is set to `False` the user will need to update the\n`command` to point to a valid gopls binary.",
        "type": "boolean",
    },
    "closeTestResultsWhenFinished": {
        "default": False,
        "markdownDescription": "Controls if the Terminus panel/tab will auto close on tests completing.",
        "type": "boolean",
    },
    "runTestsInPanel": {
        "default": True,
        "markdownDescription": "Controls if the test results output to a panel instead of a tab.",
        "type": "boolean",
    },
}

BEGIN_LSP_GOPLS_SETTINGS = """// Packages/User/LSP-gopls.sublime-settings
{
  "command": [
    "${storage_path}/LSP-gopls/bin/gopls"
  ],
  "selector": "source.go | source.gomod",
  "settings": {
"""
PREFIX_LSP_GOPLS_SETTINGS = "    "
END_LSP_GOPLS_SETTINGS = """
  }
}
"""


class GoplsGenerator:
    def __init__(self) -> None:
        self.schema = SCHEMA_TEMPLATE
        self.properties = CUSTOM_PROPERTIES
        self.gopls_settings = ""

    @classmethod
    def _get_gopls_api_docs(cls) -> Union[str, None]:
        process = subprocess.Popen(
            ["gopls", "api-json"],
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
        raw_settings = raw_schema["Options"]["User"]
        for value in raw_settings:
            current_key = f"gopls.{value['Name']}"
            if current_key in TYPE_OVERRIDE_BY_KEY:
                current_type = TYPE_OVERRIDE_BY_KEY[current_key]
            else:
                current_type = TYPE_MAP.get(value["Type"], value["Type"])
            resolved_type = "string" if current_type == "enum" else current_type

            markdown_description = (
                f"({value.get('Status', '')}) {value['Doc']}"
                if value.get("Status", "")
                else value["Doc"]
            )

            self.properties[current_key] = {
                "type": resolved_type,
                "default": json.loads(value["Default"]),
                "markdownDescription": markdown_description,
            }

            if current_type == "enum":
                self.properties[current_key]["enum"] = [
                    json.loads(enum["Value"]) for enum in value["EnumValues"]
                ]
                self.properties[current_key]["markdownEnumDescriptions"] = [
                    enum.get("Doc", "").removeprefix(f"`{enum['Value']}`: ")
                    for enum in value["EnumValues"]
                ]
            elif current_type == "object":
                self.properties[current_key]["properties"] = {}
                keys = value["EnumKeys"]["Keys"]
                if keys is None:
                    continue

                enum_type = TYPE_MAP[value["EnumKeys"].get("ValueType", "bool")]
                for enum in keys:
                    property_name = json.loads(enum["Name"])
                    self.properties[current_key]["properties"][property_name] = {
                        "markdownDescription": enum["Doc"],
                        "type": enum_type,
                        "default": json.loads(enum["Default"]),
                    }
        self.schema["contributions"]["settings"][0]["schema"]["definitions"][
            "PluginConfig"
        ]["properties"]["settings"]["properties"] = self.properties
        return self.schema

    def generate_lsp_settings(self) -> str:
        properties = self.schema["contributions"]["settings"][0]["schema"][
            "definitions"
        ]["PluginConfig"]["properties"]["settings"]["properties"]
        compiled_settings = ""
        for prop in properties:
            lines = "\n".join(
                [
                    f"{PREFIX_LSP_GOPLS_SETTINGS}// {line}".rstrip()
                    for line in properties[prop]["markdownDescription"].split("\n")
                ]
            )
            defaults = json.dumps(properties[prop]["default"], indent=2)
            defaults = "\n".join(
                [f"{PREFIX_LSP_GOPLS_SETTINGS}{line}" for line in defaults.split("\n")]
            )
            defaults = f'{PREFIX_LSP_GOPLS_SETTINGS}"{prop}": {defaults.lstrip()},'
            compiled_settings += lines + "\n" + defaults + "\n\n"
        self.gopls_settings = (
            BEGIN_LSP_GOPLS_SETTINGS
            + compiled_settings.rstrip()
            + END_LSP_GOPLS_SETTINGS
        )
        return self.gopls_settings

    def write_schema_out(self, path: str):
        with open(path, "w") as outfile:
            outfile.write(json.dumps(self.schema, indent=2) + "\n")

    def write_settings_out(self, path: str):
        with open(path, "w") as outfile:
            outfile.write(self.gopls_settings)


def main():
    processor = GoplsGenerator()
    sublime_package_schema = processor.generate_schema()
    if sublime_package_schema is None:
        return

    processor.write_schema_out(os.path.join(PACKAGE_PATH, "sublime-package.json"))

    settings = processor.generate_lsp_settings()
    if settings == "":
        return None

    processor.write_settings_out(
        os.path.join(PACKAGE_PATH, "LSP-gopls.sublime-settings")
    )


main()
