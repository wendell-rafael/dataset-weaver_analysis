# Análise Qualitativa Enriquecida: Exemplos Anônimos de Discussões

Este documento apresenta exemplos anônimos representativos extraídos das discussões da comunidade Service Weaver, organizados por categoria de problema, status de resolução e período temporal.

---

## 1. Exemplos por Categoria de Causa Raiz

Cada categoria apresenta exemplos reais (anonimizados) que ilustram os tipos de problemas enfrentados.

## 2. Exemplos por Status de Resolução

### Acknowledged Not Fixed

**Exemplo 1** (github_issue)

> runner.Test undefined (type weavertest.Runner has no field or method Test\n\nI'm running weaver v0.12. I followed the [official documentation](https://serviceweaver.dev/docs.html#testing) to create tests. I use a similar code:

```
func TestAdd(t *testing.T) {
     runner := weavertest.Local  // A runner that runs components in a single process
     runner.Test(t, func(t *testing.T, adder Adder) {
         ctx := context.Background()
         got, err := adder.Add(ctx, 1, 2)
         if err != nil {
             t.Fatal(err)
         }
         if want := 3; got != want {
             t.Fatalf("got %q, want %q", got, want)
         }
     })
}
```

It seems like weavertest.Local.Test does not exist.

**Causa Raiz:** unclear

---

**Exemplo 2** (github_issue)

> Enabling the errcheck linter\n\nCongratulations on the first release. ServiceWeaver looks very interesting and I'm looking for ways to contribute. I noticed that `errcheck` is disabled with a comment about too many errors. I've found this linter to be useful because unhandled errors can often cause bugs. Would you be interested in a few small PRs to fix or ignore the current warnings so that the `errcheck` linter can be enabled. I'll leave some more detail in a comment below about how I'd approach that change.

**Causa Raiz:** unclear

---

**Exemplo 3** (github_issue)

> 

**Causa Raiz:** unclear

---

### Unknown

**Exemplo 1** (github_pr)

> Expose the deployment identifier to the application.\n\nThis was a feature requested by one of our users so that they can distinct between multiple deployments of the same application. As far as the user is concerned, the string is an opaque identifier they can use to compare different deployments..

**Causa Raiz:** unclear

---

**Exemplo 2** (hackernews_comment)

> There has never been any issues with hiding distributed RPC calls.<p><a href="https:&#x2F;&#x2F;en.wikipedia.org&#x2F;wiki&#x2F;Fallacies_of_distributed_computing" rel="nofollow">https:&#x2F;&#x2F;en.wikipedia.org&#x2F;wiki&#x2F;Fallacies_of_distributed_compu...</a>.

**Causa Raiz:** unclear

---

**Exemplo 3** (github_pr)

> remove online_boutique binary from the repo\n\n.

**Causa Raiz:** unclear

---

## 3. Evolução Temporal das Discussões

### Decline

**Exemplo 1**

> Bump golang.org/x/crypto from 0.23.0 to 0.31.0\n\nBumps [golang.org/x/crypto](https://github.com/golang/crypto) from 0.23.0 to 0.31.0.

---

**Exemplo 2**

> Improve Hash Algorithm (Sha256 -> xxH3)\n\nHello, I'm deeply interested in ServiceWeaver project. And I want to contribute this project. I saw todo at /weaver/runtime/codegen/hash.go 
	// TODO: improve performance:
	// - do not accumulate everything; hash as we go
	// - use a non-cryptographically safe hasher

 To Improve hash performance, xxH3 Hash would be perfect for this case. xxHash is an extremely fast non-cryptographic hash algorithm, working at RAM speed limit. More detail on https://xxhash.com/



My machine is Macbook Pro, 13-inch, M1, 2020

These are the benchmark results, and just in case, I also included golang/x/crypto/blake2b for comparison.

---

**Exemplo 3**

> Is the project still alive. \n\nIs the project still alive. Is the idea and direction of the project right. Why didn't anyone answer questions for so long. Are contributors too busy?\n\n--- Comments ---\nHey @wind-c. Feel free to describe in more details what you're trying to do. Otherwise, feel free to ping me on discord and we can discuss in details your issues. We usually do that with people who're trying to adopt weaver and face various issues. .

---

### Early Adoption

**Exemplo 1**

> Tweaked website's page widths and line heights.\n\nThis PR tweaks the website's page widths and line heights. Specifically, I narrowed the default page width from 80rem to 65rem. I shrunk the blog posts to 50rem. I also increased the line-height from 1 to 1.5. I also some made some miscellaneous cleanups. I removed some unused CSS classes, fixed some padding issues, etc. | before | after |
| - | - | 
| ![before](https://user-images.githubusercontent.com/3654277/229226688-862bdfcf-74c5-44c5-a24d-564fee9ba1d7.png) | ![after](https://user-images.githubusercontent.com/3654277/229226685-40fedc28-d0ab-409f-8dfd-322fae89baa4.png) |
.

---

**Exemplo 2**

> Enable misspell linter and fix typos\n\nThis PR enables `misspell` linter in `golangci-lint` config. Also, correct typos in comments, tests, and error messages..

---

**Exemplo 3**

> Small example fixes.\n\n1. I added factors and onlineboutique to `examples_test.go`. Adding chat is hard because it requires a mysql database. 2. I made all examples `log.Fatal` the error returned by `weaver.Run`. Before, there was a mix of doing nothing, using `log.Fatal`, and writing to `os.Stderr`. 3. Quiet `examples_test.go` when -v isn't provided..

---

### Plateau

**Exemplo 1**

> Fixed RemoteWeavelet UpdateRoutingInfo bugs.\n\nThis PR fixes four bugs in RemoteWeavelet's UpdateRoutingInfo. 1. Before this PR, UpdateRoutingInfo would panic if you passed it a nil RoutingInfo. This PR fixes UpdateRoutingInfo to instead return an error. 2. Recall that a component is either always local or always remote. We don't currently allow a component to switch between the two. This PR adds code to UpdateRoutingInfo to check this. 3. Before this PR, we were using the assignment from one component as the assignment for all components' load collectors. 4. UpdateRoutingInfo updates a resolver, balancer, and load collector.

---

**Exemplo 2**

> Combine pipe.Cmd's WPipe and RPipe into a single method.\n\nCalls to WPipe and RPipe are always paired, so combine them into one method. The new method returns a struct so that we get good names for the four distinct values needed for the pair of pipes..

---

**Exemplo 3**

> How to implement a modular-design ERP product similar to Odoo using ServiceWeaver\n\nHi, we want to use ServiceWeaver to implement a modular design ERP product similar to Odoo. Is there a way to implement a feature similar to Odoo's dynamic loading/unloading of modules at runtime with ServiceWeaver. We believe that the success of Odoo among its partners and the opensource community is mainly due to its full modular architecture. From the user point of view, this is interesting since it allows to enable/disable features just by installing or uninstalling modules.

---

### Post Discontinuation

**Exemplo 1**

> Bump github.com/containerd/containerd from 1.7.11 to 1.7.27\n\nBumps [github.com/containerd/containerd](https://github.com/containerd/containerd) from 1.7.11 to 1.7.27.

---

**Exemplo 2**

> internal error: package "slices" without types was imported from "github.com/myPkg/pkg/listutil"\n\n
```go
package listutil

import "slices"

// SubtractLists subtracts the elements of the subtract list in the source list. //
// Parameters:
// - sourceList: The list from which the elements will be subtracted. // - subtractList: The list that will be subtracted from the source list. //
// Returns:
// - A new list that contains the elements of the source list minus the elements of the subtract list. //
// Explanation:
//
// It takes two slices of strings as input: source and subtract.

---

**Exemplo 3**

> Compatible with latest Go version\n\nWe need to ensure it works with the latest version of Golang. Can we get some guidance so I can open this final PR before archiving the project?\n\n--- Comments ---\nI have optimized a version that supports the latest version of Go

https://github.com/sagoo-cloud/weaver.

---

### Pre Launch

**Exemplo 1**

> Added InstrumentHandlerFunc function.\n\nThis PR adds an `InstrumentHandlerFunc` function that is pretty much identical to `InstrumentHandler`, but takes a `func(http.ResponseWriter, *http.Request)` instead of an `http.Handler`..

---

**Exemplo 2**

> Added "weaver help" subcommand.\n\nThis PR adds a `weaver help` subcommand. For example, `weaver help generate` shows a help message for the `weaver generate command`. The help command takes one of the following forms:

    weaver help
    weaver help generate
    weaver help <single|multi|ssh>
    weaver help <single|multi|ssh> <subcommand>
    weaver help <external>

It does not handle more complex help queries like

    // Flags aren't supported. weaver help multi profile --type=cpu

    // Deeper nested subcommands aren't supported. weaver help multi store list

    // External subcommands aren't supported.

---

**Exemplo 3**

> Added regex filter argument to "weaver metrics".\n\nThis PR adds a regex argument to `weaver single metrics` and `weaver multi metrics` that filters the set of displayed metrics. $ weaver single metrics
    Show application metrics

    Usage:
      weaver single metrics [metric regex]

    Flags:
      -h, --help    Print this help message. Description:
      "weaver single metrics" shows the latest value of every metric. You can filter
      metrics by providing a regular expression. Only the metrics with names that
      match the regular expression are shown. The command expects RE2 regular
      expressions, the same used by the built-in regexp module. See "go doc
      regexp/syntax" for details.

---


## Nota sobre Anonimização

Todos os IDs de autores foram anonimizados usando hashing MD5. Os textos foram mantidos integralmente (ou truncados quando muito longos) para preservar o contexto e a autenticidade das discussões.
