# LSP-gopls

Golang support for Sublime's LSP plugin.

Uses [Go Language Server][gopls-repo] to provide validation, formatting and other features for Go & Go Mod files. See linked repository for more information.

### Prerequisites

* Go (Golang) must be installed and configured in your `PATH`

### Installation

* Install [LSP][lsp-repo] and [LSP-gopls][lsp-gopls] from Package Control. Optionally install [Sublime Gomod][sublime-gomod] for gomod support.
* Restart Sublime.

### Configuration

Open configuration file using command palette with `Preferences: LSP-gopls Settings` command or opening it from the Sublime menu (`Preferences > Package Settings > LSP > Servers > LSP-gopls`).

## Settings

Configure the default Go language server ('gopls'). In most cases, configuring this section is unnecessary. See [the documentation][gopls-settings] for all available settings.
