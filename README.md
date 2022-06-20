# LSP-gopls

Golang support for Sublime's LSP plugin.

Uses [Go Language Server][gopls-repo] to provide validation, formatting and other features for Go & Go Mod files. See linked repository for more information.

### Prerequisites

* Go (Golang) must be installed and configured in your `PATH`

#### Optionals

LSP-gopls implements the ability for results from Go Tests to be output into a panel. In order to support this, please install [Terminus][terminus]

### Installation

* Install [LSP][lsp-repo] and [LSP-gopls][lsp-gopls] from Package Control. Optionally install [Sublime Gomod][sublime-gomod] for gomod support.
* Restart Sublime.

### Configuration

Open configuration file using command palette with `Preferences: LSP-gopls Settings` command or opening it from the Sublime menu (`Preferences > Package Settings > LSP > Servers > LSP-gopls`).

## Settings

Configure the default Go language server ('gopls'). In most cases, configuring this section is unnecessary. See [the documentation][gopls-settings] for all available settings.


[lsp-repo]: https://packagecontrol.io/packages/LSP
[lsp-gopls]: https://packagecontrol.io/packages/LSP-gopls
[packagedev-repo]: https://packagecontrol.io/packages/PackageDev
[gopls-repo]: https://github.com/golang/tools/blob/master/gopls/README.md
[gopls-settings]: https://github.com/golang/tools/blob/master/gopls/doc/settings.md
[gopls-analyzers]: https://github.com/golang/tools/blob/master/gopls/doc/analyzers.md
[sublime-gomod]: https://packagecontrol.io/packages/Gomod
[golang-installation]: https://golang.org/doc/install
[terminus]: https://packagecontrol.io/packages/Terminus
