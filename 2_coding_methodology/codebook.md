# Codebook for Service Weaver Post-Mortem Analysis

**Version:** 1.0  
**Last Updated:** 2024-10-14  
**Purpose:** Systematic coding guide for thematic analysis of Service Weaver discontinuation

---

## Overview

This codebook defines the hierarchical coding scheme for analyzing data related to the Service Weaver framework discontinuation. Each code category represents a cluster of related problems or themes that emerged from the data.

### Coding Process

1. **Read full text** of the record (issue/post/comment)
2. **Identify primary theme** - What is the main problem or topic?
3. **Assign primary code** from the scheme
4. **Check for secondary theme** - Is there a strong secondary theme?
5. **Assign secondary code** if applicable
6. **Rate confidence** (0.0-1.0) based on clarity
7. **Document reasoning** in 1-2 sentences

### Confidence Score Guidelines

- **1.0:** Explicitly stated; no ambiguity
- **0.9:** Very clear from context
- **0.7-0.8:** Reasonably clear; minor ambiguity
- **0.5-0.6:** Ambiguous; multiple interpretations possible
- **< 0.5:** Unclear; guess based on limited info

---

## Category Definitions & Examples

### 1. DESIGN_ARCHITECTURE

**Description:** Issues stemming from fundamental architectural design choices.

#### 1.1 RPC_CORBA_PROBLEM

**Definition:** Criticism of RPC/CORBA-style communication patterns; tight synchronous coupling.

**When to use:**
- Mentions "RPC is outdated"
- Comparison to CORBA/DCOM failures
- Complaints about synchronous blocking calls

**Examples:**
- "This just reinvents CORBA's mistakes"
- "RPC-style communication is too tightly coupled"
- "Synchronous calls create cascading failures"

**NOT this code:**
- General "I don't like the API" (→ USABILITY_DX)
- Performance issues (→ PERFORMANCE_SCALE)

---

#### 1.2 COMPONENT_COUPLING

**Definition:** Components are too tightly coupled; hard to develop/test independently.

**When to use:**
- "Cannot test component X without Y"
- "Changes in one service break others"
- "Difficult to refactor"

**Examples:**
- Issue #42: "Testing requires spinning up entire app"
- "Changes to one component require redeploying everything"

---

#### 1.3 ALL_OR_NOTHING_DEPLOYMENT

**Definition:** Deployment model forces all-or-nothing; cannot deploy incrementally.

**When to use:**
- Mentions inability to deploy single service
- Complaints about monolithic deployment
- "Have to redeploy everything for one change"

---

#### 1.4 INADEQUATE_ABSTRACTIONS

**Definition:** Framework's abstractions don't match real-world use cases; force workarounds.

**When to use:**
- "Abstraction leaks"
- "Had to fight the framework"
- "Couldn't model X in Weaver"

---

### 2. USABILITY_DX

**Description:** Developer experience issues; friction in using the framework.

#### 2.1 LEARNING_CURVE

**Definition:** Difficult to learn; steep conceptual curve; requires paradigm shift.

**When to use:**
- "Hard to understand"
- "Took weeks to get productive"
- "Concepts are confusing"

**Examples:**
- "The mental model is unintuitive"
- Reddit: "Spent days on docs, still confused"

---

#### 2.2 COMPLEX_CONFIGURATION

**Definition:** Configuration is complex, verbose, or error-prone.

**When to use:**
- Complaints about config files
- "Too many knobs"
- Config-related bugs

---

#### 2.3 DEBUGGING_DIFFICULTY

**Definition:** Hard to debug; opaque errors; poor diagnostics.

**When to use:**
- "Error messages are cryptic"
- "Can't trace where problem is"
- "Debugging is a nightmare"

---

#### 2.4 INSUFFICIENT_DOCUMENTATION

**Definition:** Documentation gaps, outdated, or low quality.

**When to use:**
- "Docs are missing X"
- "Examples don't work"
- "Docs are out of sync"

**Examples:**
- Issue #89: "No docs on how to deploy to AWS"
- StackOverflow: "Found docs for v0.1, but using v0.5"

---

#### 2.5 WEAVER_GENERATE_FRICTION

**Definition:** Problems with code generation step (`weaver generate`).

**When to use:**
- "weaver generate is slow"
- "Generated code breaks my IDE"
- "Generation fails on my project"

---

### 3. ECOSYSTEM_INTEROP

**Description:** Integration issues with broader ecosystem (languages, tools, platforms).

#### 3.1 LACK_MULTILANGUAGE

**Definition:** Go-only; no multi-language support.

**When to use:**
- "Need Python support"
- "Our backend is Java"
- "Go-only is a dealbreaker"

---

#### 3.2 CI_CD_INTEGRATION

**Definition:** Difficult to integrate with CI/CD pipelines or automation.

**When to use:**
- "CI build takes too long"
- "Hard to automate deployment"
- "Doesn't fit our pipeline"

---

#### 3.3 LIMITED_OBSERVABILITY

**Definition:** Observability gaps; metrics/tracing incomplete or non-standard.

**When to use:**
- "Can't integrate with Prometheus"
- "Tracing is broken"
- "Metrics are non-standard"

---

#### 3.4 VENDOR_LOCK_IN

**Definition:** Perceived or actual vendor lock-in to Google/GCP.

**When to use:**
- "Too Google-specific"
- "Hard to migrate away"
- "Feels like lock-in"

---

#### 3.5 TOOLING_IMMATURITY

**Definition:** Missing or immature tooling (IDE plugins, CLI, etc.).

**When to use:**
- "No VS Code plugin"
- "CLI is clunky"
- "Tooling is bare-bones"

---

### 4. PERFORMANCE_SCALE

**Description:** Performance or scalability concerns.

#### 4.1 RUNTIME_OVERHEAD

**Definition:** Framework adds noticeable performance overhead.

**When to use:**
- Benchmarks showing slowdown
- "Weaver is slower than plain gRPC"
- Latency concerns

---

#### 4.2 GRANULARITY_ISSUES

**Definition:** Granularity of components is wrong (too fine or too coarse).

**When to use:**
- "Components are too small"
- "Overhead from too many calls"
- "Hard to decide component boundaries"

---

#### 4.3 SPECIFIC_BOTTLENECKS

**Definition:** Identified specific performance bottlenecks.

**When to use:**
- "Serialization is slow"
- "Lock contention in X"
- Profiling data showing bottleneck

---

#### 4.4 TRADE_OFF_CONCERNS

**Definition:** Performance trade-offs not worth complexity.

**When to use:**
- "Complexity not justified by gains"
- "Only 5% faster"
- "Marginal benefit"

---

### 5. COMMUNITY_ADOPTION

**Description:** Issues related to community engagement and adoption.

#### 5.1 LACK_ENGAGEMENT

**Definition:** Low community activity; few contributors.

**When to use:**
- "No one is using this"
- "Issues go unanswered"
- "Community is dead"

---

#### 5.2 PARADIGM_RESISTANCE

**Definition:** Developers resist the paradigm/approach.

**When to use:**
- "Why not just use X?"
- "This approach feels wrong"
- "Standard patterns are better"

---

#### 5.3 ALTERNATIVE_PREFERRED

**Definition:** Existing alternatives (gRPC, K8s, etc.) are preferred.

**When to use:**
- "gRPC + K8s does this"
- "Already solved problem"
- "Don't need framework"

---

#### 5.4 UNCLEAR_VALUE_PROPOSITION

**Definition:** Value proposition is not clear or compelling.

**When to use:**
- "What problem does this solve?"
- "Why not just use microservices?"
- "Value is unclear"

---

### 6. POST_MORTEM_ANALYSIS (Meta-Category)

**Description:** Retrospective discussions about why the project failed.

#### 6.1 ROOT_CAUSE_IDENTIFIED

**Definition:** Author explicitly identifies a root cause of failure.

**When to use:**
- "The real problem was X"
- "This is why it failed"
- Causal analysis

---

#### 6.2 CONTRIBUTING_FACTOR

**Definition:** Factor acknowledged as contributing (but not root cause).

**When to use:**
- "This made it worse"
- "Compounded the problem"

---

#### 6.3 SPECULATION_ON_FAILURE

**Definition:** Speculation about discontinuation reasons.

**When to use:**
- "I think Google killed it because..."
- "Probably failed due to..."
- Hypothesizing

---

## Edge Cases & Ambiguities

### Multiple Themes Present

**Rule:** Code all significant themes. Use primary + secondary.

**Example:**  
Issue: "Weaver is hard to learn (DX) and Go-only (interop)"  
→ Primary: `USABILITY_DX.LEARNING_CURVE`  
→ Secondary: `ECOSYSTEM_INTEROP.LACK_MULTILANGUAGE`

---

### Ambiguous Wording

**Rule:** If confidence < 0.7, document uncertainty in notes.

**Example:**  
Comment: "Just doesn't feel right"  
→ Primary: `COMMUNITY_ADOPTION.PARADIGM_RESISTANCE` (confidence: 0.6)  
→ Note: "Vague; could be UX or architectural concern"

---

### Feature Requests vs. Problems

**Rule:** Code based on the underlying problem, not the request.

**Example:**  
Issue: "Please add Python support"  
→ Primary: `ECOSYSTEM_INTEROP.LACK_MULTILANGUAGE`

---

### Off-Topic / Spam

**Rule:** Mark as `EXCLUDE` in primary_code; do not code further.

---

## Inter-Rater Reliability

For the pilot study (15% of dataset), two coders will independently code the same records. Agreement is measured via Cohen's Kappa.

**Target:** κ ≥ 0.70 (substantial agreement)

**If κ < 0.70:**
1. Review disagreements
2. Clarify ambiguous definitions
3. Re-code problematic records
4. Re-test reliability

---

## Changelog

- **2024-10-14:** Initial version 1.0
