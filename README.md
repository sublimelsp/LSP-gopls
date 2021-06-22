# LSP-gopls

Golang support for Sublime's LSP plugin.

Uses [Go Language Server][gopls-repo] to provide validation, formatting and other features for JSON files. See linked repository for more information.

### Prerequisites

* Gopls (Go Language Server) must be installed and configured in your `PATH`

#### How-to

1. Ensure `go` (golang) is installed and configured in your `PATH` See [Golang Installation](golang-installation)
1. Install `gopls` via `GO111MODULE=on go get golang.org/x/tools/gopls@latest`
1. Add `gopls` to your `PATH` if it is not already present

### Installation

* Install [LSP][lsp-repo] and `LSP-gopls` from Package Control.
* Restart Sublime.

#### Go Mod Support

To get proper support for Go.mod files and codelenses it is recommended you install the [Sublime Gomod][sublime-gomod] package for syntax highlighting and scoping.

### Configuration

Open configuration file using command palette with `Preferences: LSP-gopls Settings` command or opening it from the Sublime menu (`Preferences > Package Settings > LSP > Servers > LSP-gopls`).

### For users of PackageDev

The [PackageDev][packagedev-repo] package implements features that provide completions and tooltips when editing the Sublime settings files, which overlaps and conflicts with functionality provided by this package. To take advantage of the strict schemas that this package provides, disable corresponding functionality in `PackageDev` by opening `Preferences: PackageDev Settings` from the Command Palette and set the following settings on the right side:

```json
{
  "settings.auto_complete": false,
  "settings.tooltip": false
}
```

## Settings

__Taken from `gopls api-json`__

Configure the default Go language server ('gopls'). In most cases, configuring this section is unnecessary. See [the documentation][gopls-settings] for all available settings.

### `gopls.allowImplicitNetworkAccess`

allowImplicitNetworkAccess disables GOPROXY=off, allowing implicit module downloads rather than requiring user action. This option will eventually be removed.

Default: `false`

### `gopls.allowModfileModifications`

**Experimental**

allowModfileModifications disables -mod=readonly, allowing imports from
out-of-scope modules. This option will eventually be removed.


Default: `false`

### `gopls.buildFlags`

buildFlags is the set of flags passed on to the build system when invoked.
It is applied to queries like `go list`, which is used when discovering files.
The most common use is to set `-tags`.

If unspecified, values of `go.buildFlags, go.buildTags` will be propagated.

### `gopls.directoryFilters`

directoryFilters can be used to exclude unwanted directories from the
workspace. By default, all directories are included. Filters are an
operator, `+` to include and `-` to exclude, followed by a path prefix
relative to the workspace folder. They are evaluated in order, and
the last filter that applies to a path controls whether it is included.
The path prefix can be empty, so an initial `-` excludes everything.

Examples:

Exclude node_modules: `-node_modules`

Include only project_a: `-` (exclude everything), `+project_a`

Include only project_a, but not node_modules inside it: `-`, `+project_a`, `-project_a/node_modules`

### `gopls.env`

env adds environment variables to external commands run by `gopls`, most notably `go list`.

### `gopls.expandWorkspaceToModule`

**Experimental**

expandWorkspaceToModule instructs `gopls` to adjust the scope of the
workspace to find the best available module root. `gopls` first looks for
a go.mod file in any parent directory of the workspace folder, expanding
the scope to that directory if it exists. If no viable parent directory is
found, gopls will check if there is exactly one child directory containing
a go.mod file, narrowing the scope to that directory if it exists.


Default: `true`

### `gopls.experimentalPackageCacheKey`

**Experimental**

experimentalPackageCacheKey controls whether to use a coarser cache key
for package type information to increase cache hits. This setting removes
the user's environment, build flags, and working directory from the cache
key, which should be a safe change as all relevant inputs into the type
checking pass are already hashed into the key. This is temporarily guarded
by an experiment because caching behavior is subtle and difficult to
comprehensively test.


Default: `true`

### `gopls.experimentalTemplateSupport`

**Experimental**

experimentalTemplateSupport opts into the experimental support
for template files.


Default: `false`

### `gopls.experimentalWorkspaceModule`

**Experimental**

experimentalWorkspaceModule opts a user into the experimental support
for multi-module workspaces.


Default: `false`

### `gopls.memoryMode`

**Experimental**

memoryMode controls the tradeoff `gopls` makes between memory usage and
correctness.

Values other than `Normal` are untested and may break in surprising ways.
<br/>
Allowed Options:

* `DegradeClosed`: `"DegradeClosed"`: In DegradeClosed mode, `gopls` will collect less information about
packages without open files. As a result, features like Find
References and Rename will miss results in such packages.
* `Normal`


Default: `"Normal"`

### `gopls.gofumpt`

gofumpt indicates if we should run gofumpt formatting.


Default: `false`

### `gopls.local`

local is the equivalent of the `goimports -local` flag, which puts
imports beginning with this string after third-party packages. It should
be the prefix of the import path whose imports should be grouped
separately.


Default: `""`

### `gopls.codelenses`

codelenses overrides the enabled/disabled state of code lenses. See the
"Code Lenses" section of the
[Settings page][gopls-settings]
for the list of supported lenses.

Example Usage:

```json5
"settings": {
...
  "gopls.codelens": {
    "generate": false,  // Don't show the `go generate` lens.
    "gc_details": true  // Show a code lens toggling the display of gc's choices.
  }
...
}
```

| Properties | Description |
| --- | --- |
| `gc_details` | Toggle the calculation of gc annotations. <br/> Default: `false` |
| `generate` | Runs `go generate` for a given directory. <br/> Default: `true` |
| `regenerate_cgo` | Regenerates cgo definitions. <br/> Default: `true` |
| `test` | Runs `go test` for a specific set of test or benchmark functions. <br/> Default: `false` |
| `tidy` | Runs `go mod tidy` for a module. <br/> Default: `true` |
| `upgrade_dependency` | Upgrades a dependency in the go.mod file for a module. <br/> Default: `true` |
| `vendor` | Runs `go mod vendor` for a module. <br/> Default: `true` |

### `gopls.completionBudget`

(For Debugging) completionBudget is the soft latency goal for completion requests. Most
requests finish in a couple milliseconds, but in some cases deep
completions can take much longer. As we use up our budget we
dynamically reduce the search scope to ensure we return timely
results. Zero means unlimited.


Default: `"100ms"`

### `gopls.experimentalPostfixCompletions`

**Experimental**

experimentalPostfixCompletions enables artifical method snippets
such as "someSlice.sort!".


Default: `true`

### `gopls.matcher`

(Advanced) matcher sets the algorithm that is used when calculating completion
candidates.
<br/>
Allowed Options: `CaseInsensitive`, `CaseSensitive`, `Fuzzy`

Default: `"Fuzzy"`

### `gopls.usePlaceholders`

placeholders enables placeholders for function parameters or struct
fields in completion responses.


Default: `false`

### `gopls.analyses`

analyses specify analyses that the user would like to enable or disable.
A map of the names of analysis passes that should be enabled/disabled.
A full list of analyzers that gopls uses can be found
[here][gopls-analyzers].

Example Usage:

```json5
...
"gopls.analyses": {
  "unreachable": false, // Disable the unreachable analyzer.
  "unusedparams": true  // Enable the unusedparams analyzer.
}
...
```

| Properties | Description |
| --- | --- |
| `asmdecl` | report mismatches between assembly files and Go declarations <br/> Default: `true` |
| `assign` | check for useless assignments <br/> This checker reports assignments of the form x = x or a[i] = a[i]. These are almost always useless, and even when they aren't they are usually a mistake. <br/> Default: `true` |
| `atomic` | check for common mistakes using the sync/atomic package <br/> The atomic checker looks for assignment statements of the form: <br/> <pre>x = atomic.AddUint64(&x, 1)</pre><br/> which are not atomic. <br/> Default: `true` |
| `atomicalign` | check for non-64-bits-aligned arguments to sync/atomic functions <br/> Default: `true` |
| `bools` | check for common mistakes involving boolean operators <br/> Default: `true` |
| `buildtag` | check that +build tags are well-formed and correctly located <br/> Default: `true` |
| `cgocall` | detect some violations of the cgo pointer passing rules <br/> Check for invalid cgo pointer passing. This looks for code that uses cgo to call C code passing values whose types are almost always invalid according to the cgo pointer sharing rules. Specifically, it warns about attempts to pass a Go chan, map, func, or slice to C, either directly, or via a pointer, array, or struct. <br/> Default: `true` |
| `composites` | check for unkeyed composite literals <br/> This analyzer reports a diagnostic for composite literals of struct types imported from another package that do not use the field-keyed syntax. Such literals are fragile because the addition of a new field (even if unexported) to the struct will cause compilation to fail. <br/> As an example, <br/> <pre>err = &net.DNSConfigError{err}</pre><br/> should be replaced by: <br/> <pre>err = &net.DNSConfigError{Err: err}</pre><br/> <br/> Default: `true` |
| `copylocks` | check for locks erroneously passed by value <br/> Inadvertently copying a value containing a lock, such as sync.Mutex or sync.WaitGroup, may cause both copies to malfunction. Generally such values should be referred to through a pointer. <br/> Default: `true` |
| `deepequalerrors` | check for calls of reflect.DeepEqual on error values <br/> The deepequalerrors checker looks for calls of the form: <br/>     reflect.DeepEqual(err1, err2) <br/> where err1 and err2 are errors. Using reflect.DeepEqual to compare errors is discouraged. <br/> Default: `true` |
| `errorsas` | report passing non-pointer or non-error values to errors.As <br/> The errorsas analysis reports calls to errors.As where the type of the second argument is not a pointer to a type implementing error. <br/> Default: `true` |
| `fieldalignment` | find structs that would use less memory if their fields were sorted <br/> This analyzer find structs that can be rearranged to use less memory, and provides a suggested edit with the optimal order. <br/> Note that there are two different diagnostics reported. One checks struct size, and the other reports "pointer bytes" used. Pointer bytes is how many bytes of the object that the garbage collector has to potentially scan for pointers, for example: <br/> <pre>struct { uint32; string }</pre><br/> have 16 pointer bytes because the garbage collector has to scan up through the string's inner pointer. <br/> <pre>struct { string; *uint32 }</pre><br/> has 24 pointer bytes because it has to scan further through the *uint32. <br/> <pre>struct { string; uint32 }</pre><br/> has 8 because it can stop immediately after the string pointer. <br/> <br/> Default: `false` |
| `fillreturns` | suggested fixes for "wrong number of return values (want %d, got %d)" <br/> This checker provides suggested fixes for type errors of the type "wrong number of return values (want %d, got %d)". For example: <pre>func m() (int, string, *bool, error) {<br/>  return<br/>}</pre>will turn into <pre>func m() (int, string, *bool, error) {<br/> return 0, "", nil, nil<br/>}</pre><br/> This functionality is similar to https://github.com/sqs/goreturns. <br/> <br/> Default: `true` |
| `fillstruct` | note incomplete struct initializations <br/> This analyzer provides diagnostics for any struct literals that do not have any fields initialized. Because the suggested fix for this analysis is expensive to compute, callers should compute it separately, using the SuggestedFix function below. <br/> <br/> Default: `true` |
| `httpresponse` | check for mistakes using HTTP responses <br/> A common mistake when using the net/http package is to defer a function call to close the http.Response Body before checking the error that determines whether the response is valid: <br/> <pre>resp, err := http.Head(url)<br/>defer resp.Body.Close()<br/>if err != nil {<br/>  log.Fatal(err)<br/>}<br/>// (defer statement belongs here)</pre><br/> This checker helps uncover latent nil dereference bugs by reporting a diagnostic for such mistakes. <br/> Default: `true` |
| `ifaceassert` | detect impossible interface-to-interface type assertions <br/> This checker flags type assertions v.(T) and corresponding type-switch cases in which the static type V of v is an interface that cannot possibly implement the target interface T. This occurs when V and T contain methods with the same name but different signatures. Example: <br/> <pre>var v interface {<br/> Read()<br/>}<br/>_ = v.(io.Reader)</pre><br/> The Read method in v has a different signature than the Read method in io.Reader, so this assertion cannot succeed. <br/> <br/> Default: `true` |
| `loopclosure` | check references to loop variables from within nested functions <br/> This analyzer checks for references to loop variables from within a function literal inside the loop body. It checks only instances where the function literal is called in a defer or go statement that is the last statement in the loop body, as otherwise we would need whole program analysis. <br/> For example: <br/> <pre>for i, v := range s {<br/>  go func() {<br/>    println(i, v) // not what you might expect<br/> }()<br/>}</pre><br/> See: https://golang.org/doc/go_faq.html#closures_and_goroutines <br/> Default: `true` |
| `lostcancel` | check cancel func returned by context.WithCancel is called <br/> The cancellation function returned by context.WithCancel, WithTimeout, and WithDeadline must be called or the new context will remain live until its parent context is cancelled. (The background context is never cancelled.) <br/> Default: `true` |
| `nilfunc` | check for useless comparisons between functions and nil <br/> A useless comparison is one like f == nil as opposed to f() == nil. <br/> Default: `true` |
| `nilness` | check for redundant or impossible nil comparisons <br/> The nilness checker inspects the control-flow graph of each function in a package and reports nil pointer dereferences, degenerate nil pointers, and panics with nil values. A degenerate comparison is of the form x==nil or x!=nil where x is statically known to be nil or non-nil. These are often a mistake, especially in control flow related to errors. Panics with nil values are checked because they are not detectable by <br/> <pre>if r := recover(); r != nil {</pre><br/> This check reports conditions such as: <br/> <pre>if f == nil { // impossible condition (f is a function)<br/>}</pre><br/> and: <br/> <pre>p := &v<br/>...<br/>if p != nil { // tautological condition<br/>}</pre><br/> and: <br/> <pre>if p == nil {<br/>  print(*p) // nil dereference<br/>}</pre><br/> and: <br/> <pre>if p == nil {<br/>  panic(p)<br/>}</pre><br/> <br/> Default: `false` |
| `nonewvars` | suggested fixes for "no new vars on left side of :=" <br/> This checker provides suggested fixes for type errors of the type "no new vars on left side of :=". For example: <pre>z := 1<br/>z := 2</pre>will turn into <pre>z := 1<br/>z = 2</pre><br/> <br/> Default: `true` |
| `noresultvalues` | suggested fixes for "no result values expected" <br/> This checker provides suggested fixes for type errors of the type "no result values expected". For example: <pre>func z() { return nil }</pre>will turn into <pre>func z() { return }</pre><br/> <br/> Default: `true` |
| `printf` | check consistency of Printf format strings and arguments <br/> The check applies to known functions (for example, those in package fmt) as well as any detected wrappers of known functions. <br/> A function that wants to avail itself of printf checking but is not found by this analyzer's heuristics (for example, due to use of dynamic calls) can insert a bogus call: <br/> <pre>if false {<br/>  _ = fmt.Sprintf(format, args...) // enable printf checking<br/>}</pre><br/> The -funcs flag specifies a comma-separated list of names of additional known formatting functions or methods. If the name contains a period, it must denote a specific function using one of the following forms: <br/> <pre>dir/pkg.Function<br/>dir/pkg.Type.Method<br/>(*dir/pkg.Type).Method</pre><br/> Otherwise the name is interpreted as a case-insensitive unqualified identifier such as "errorf". Either way, if a listed name ends in f, the function is assumed to be Printf-like, taking a format string before the argument list. Otherwise it is assumed to be Print-like, taking a list of arguments with no format string. <br/> <br/> Default: `true` |
| `shadow` | check for possible unintended shadowing of variables <br/> This analyzer check for shadowed variables. A shadowed variable is a variable declared in an inner scope with the same name and type as a variable in an outer scope, and where the outer variable is mentioned after the inner one is declared. <br/> (This definition can be refined; the module generates too many false positives and is not yet enabled by default.) <br/> For example: <br/> <pre>func BadRead(f *os.File, buf []byte) error {<br/> var err error<br/>  for {<br/>    n, err := f.Read(buf) // shadows the function variable 'err'<br/>   if err != nil {<br/>      break // causes return of wrong value<br/>    }<br/>    foo(buf)<br/> }<br/>  return err<br/>}</pre><br/> <br/> Default: `false` |
| `shift` | check for shifts that equal or exceed the width of the integer <br/> Default: `true` |
| `simplifycompositelit` | check for composite literal simplifications <br/> An array, slice, or map composite literal of the form: <pre>[]T{T{}, T{}}</pre>will be simplified to: <pre>[]T{{}, {}}</pre><br/> This is one of the simplifications that "gofmt -s" applies. <br/> Default: `true` |
| `simplifyrange` | check for range statement simplifications <br/> A range of the form: <pre>for x, _ = range v {...}</pre>will be simplified to: <pre>for x = range v {...}</pre><br/> A range of the form: <pre>for _ = range v {...}</pre>will be simplified to: <pre>for range v {...}</pre><br/> This is one of the simplifications that "gofmt -s" applies. <br/> Default: `true` |
| `simplifyslice` | check for slice simplifications <br/> A slice expression of the form: <pre>s[a:len(s)]</pre>will be simplified to: <pre>s[a:]</pre><br/> This is one of the simplifications that "gofmt -s" applies. <br/> Default: `true` |
| `sortslice` | check the argument type of sort.Slice <br/> sort.Slice requires an argument of a slice type. Check that the interface{} value passed to sort.Slice is actually a slice. <br/> Default: `true` |
| `stdmethods` | check signature of methods of well-known interfaces <br/> Sometimes a type may be intended to satisfy an interface but may fail to do so because of a mistake in its method signature. For example, the result of this WriteTo method should be (int64, error), not error, to satisfy io.WriterTo: <br/> <pre>type myWriterTo struct{...}</pre>        func (myWriterTo) WriteTo(w io.Writer) error { ... } <br/> This check ensures that each method whose name matches one of several well-known interface methods from the standard library has the correct signature for that interface. <br/> Checked method names include: <pre>Format GobEncode GobDecode MarshalJSON MarshalXML<br/>Peek ReadByte ReadFrom ReadRune Scan Seek<br/>UnmarshalJSON UnreadByte UnreadRune WriteByte<br/>WriteTo</pre><br/> <br/> Default: `true` |
| `stringintconv` | check for string(int) conversions <br/> This checker flags conversions of the form string(x) where x is an integer (but not byte or rune) type. Such conversions are discouraged because they return the UTF-8 representation of the Unicode code point x, and not a decimal string representation of x as one might expect. Furthermore, if x denotes an invalid code point, the conversion cannot be statically rejected. <br/> For conversions that intend on using the code point, consider replacing them with string(rune(x)). Otherwise, strconv.Itoa and its equivalents return the string representation of the value in the desired base. <br/> <br/> Default: `true` |
| `structtag` | check that struct field tags conform to reflect.StructTag.Get <br/> Also report certain struct tags (json, xml) used with unexported fields. <br/> Default: `true` |
| `testinggoroutine` | report calls to (*testing.T).Fatal from goroutines started by a test. <br/> Functions that abruptly terminate a test, such as the Fatal, Fatalf, FailNow, and Skip{,f,Now} methods of *testing.T, must be called from the test goroutine itself. This checker detects calls to these functions that occur within a goroutine started by the test. For example: <br/> func TestFoo(t *testing.T) {     go func() {         t.Fatal("oops") // error: (*T).Fatal called from non-test goroutine     }() } <br/> <br/> Default: `true` |
| `tests` | check for common mistaken usages of tests and examples <br/> The tests checker walks Test, Benchmark and Example functions checking malformed names, wrong signatures and examples documenting non-existent identifiers. <br/> Please see the documentation for package testing in golang.org/pkg/testing for the conventions that are enforced for Tests, Benchmarks, and Examples. <br/> Default: `true` |
| `undeclaredname` | suggested fixes for "undeclared name: <>" <br/> This checker provides suggested fixes for type errors of the type "undeclared name: <>". It will insert a new statement: "<> := ". <br/> Default: `true` |
| `unmarshal` | report passing non-pointer or non-interface values to unmarshal <br/> The unmarshal analysis reports calls to functions such as json.Unmarshal in which the argument type is not a pointer or an interface. <br/> Default: `true` |
| `unreachable` | check for unreachable code <br/> The unreachable analyzer finds statements that execution can never reach because they are preceded by an return statement, a call to panic, an infinite loop, or similar constructs. <br/> Default: `true` |
| `unsafeptr` | check for invalid conversions of uintptr to unsafe.Pointer <br/> The unsafeptr analyzer reports likely incorrect uses of unsafe.Pointer to convert integers to pointers. A conversion from uintptr to unsafe.Pointer is invalid if it implies that there is a uintptr-typed word in memory that holds a pointer value, because that word will be invisible to stack copying and to the garbage collector. <br/> Default: `true` |
| `unusedparams` | check for unused parameters of functions <br/> The unusedparams analyzer checks functions to see if there are any parameters that are not being used. <br/> To reduce false positives it ignores: - methods - parameters that do not have a name or are underscored - functions in test files - functions with empty bodies or those with just a return stmt <br/> Default: `false` |
| `unusedresult` | check for unused results of calls to some functions <br/> Some functions like fmt.Errorf return a result and have no side effects, so it is always a mistake to discard the result. This analyzer reports calls to certain functions in which the result of the call is ignored. <br/> The set of functions may be controlled using flags. <br/> Default: `true` |
| `unusedwrite` | checks for unused writes <br/> The analyzer reports instances of writes to struct fields and arrays that are never read. Specifically, when a struct object or an array is copied, its elements are copied implicitly by the compiler, and any element write to this copy does nothing with the original object. <br/> For example: <br/> <pre>type T struct { x int }<br/>func f(input []T) {<br/> for i, v := range input {  // v is a copy<br/>    v.x = i  // unused write to field x<br/>  }<br/>}</pre><br/> Another example is about non-pointer receiver: <br/> <pre>type T struct { x int }<br/>func (t T) f() {  // t is a copy<br/>  t.x = i  // unused write to field x<br/>}</pre><br/> <br/> Default: `false` |

### `gopls.annotations`

**Experimental**

annotations specifies the various kinds of optimization diagnostics
that should be reported by the gc_details command.

| Properties | Description |
| --- | --- |
| `bounds` | `"bounds"` controls bounds checking diagnostics. <br/> <br/> Default: `true` |
| `escape` | `"escape"` controls diagnostics about escape choices. <br/> <br/> Default: `true` |
| `inline` | `"inline"` controls diagnostics about inlining choices. <br/> <br/> Default: `true` |
| `nil` | `"nil"` controls nil checks. <br/> <br/> Default: `true` |
### `gopls.experimentalDiagnosticsDelay`

**Experimental**

experimentalDiagnosticsDelay controls the amount of time that gopls waits
after the most recent file modification before computing deep diagnostics.
Simple diagnostics (parsing and type-checking) are always run immediately
on recently modified packages.

This option must be set to a valid duration string, for example `"250ms"`.


Default: `"250ms"`

### `gopls.staticcheck`

**Experimental**

staticcheck enables additional analyses from staticcheck.io.


Default: `false`

### `gopls.hoverKind`

hoverKind controls the information that appears in the hover text.
SingleLine and Structured are intended for use only by authors of editor plugins.
<br/>
Allowed Options:

* `FullDocumentation`
* `NoDocumentation`
* `SingleLine`
* `Structured`: `"Structured"` is an experimental setting that returns a structured hover format.
This format separates the signature from the documentation, so that the client
can do more manipulation of these fields.<br/>This should only be used by clients that support this behavior.
* `SynopsisDocumentation`


Default: `"FullDocumentation"`

### `gopls.linkTarget`

linkTarget controls where documentation links go.
It might be one of:

* `"godoc.org"`
* `"pkg.go.dev"`

If company chooses to use its own `godoc.org`, its address can be used as well.


Default: `"pkg.go.dev"`

### `gopls.linksInHover`

linksInHover toggles the presence of links to documentation in hover.


Default: `true`

### `gopls.importShortcut`

importShortcut specifies whether import statements should link to
documentation or go to definitions.
<br/>
Allowed Options: `Both`, `Definition`, `Link`

Default: `"Both"`

### `gopls.symbolMatcher`

(Advanced) symbolMatcher sets the algorithm that is used when finding workspace symbols.
<br/>
Allowed Options: `CaseInsensitive`, `CaseSensitive`, `Fuzzy`

Default: `"Fuzzy"`

### `gopls.symbolStyle`

**Advanced**

symbolStyle controls how symbols are qualified in symbol responses.

Example Usage:

```json5
"gopls": {
...
  "symbolStyle": "dynamic",
...
}
```
<br/>
Allowed Options:

* `Dynamic`: `"Dynamic"` uses whichever qualifier results in the highest scoring
match for the given symbol query. Here a "qualifier" is any "/" or "."
delimited suffix of the fully qualified symbol. i.e. "to/pkg.Foo.Field" or
just "Foo.Field".
* `Full`: `"Full"` is fully qualified symbols, i.e.
"path/to/pkg.Foo.Field".
* `Package`: `"Package"` is package qualified symbols i.e.
"pkg.Foo.Field".


Default: `"Dynamic"`

### `gopls.semanticTokens`

**Experimental**

semanticTokens controls whether the LSP server will send
semantic tokens to the client.


Default: `false`

### `gopls.verboseOutput`

**For Debugging**

verboseOutput enables additional debug logging.


Default: `false`



[lsp-repo]: https://packagecontrol.io/packages/LSP
[packagedev-repo]: https://packagecontrol.io/packages/PackageDev
[gopls-repo]: https://github.com/golang/tools/blob/master/gopls/README.md
[gopls-settings]: https://github.com/golang/tools/blob/master/gopls/doc/settings.md
[gopls-analyzers]: https://github.com/golang/tools/blob/master/gopls/doc/analyzers.md
[sublime-gomod]: https://packagecontrol.io/packages/Gomod
[golang-installation]: https://golang.org/doc/install
