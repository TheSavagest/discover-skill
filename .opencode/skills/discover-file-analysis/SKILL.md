---
name: discover-file-analysis
description: Inspect selected source files efficiently using bounded ranges, symbol search and structural queries instead of reading entire repositories.
compatibility: opencode
---

# Bounded File Analysis

Never read the entire repository into context. Minimize context while preserving evidence quality.

## Analysis Order

1. **Identify candidate files** - glob patterns, project references, import graphs
2. **Inspect metadata** - file size, line count, language
3. **Search symbols** - grep, ripgrep, AST symbol index
4. **Inspect relevant ranges** - read only necessary line ranges
5. **Follow references** - go to definition, find references
6. **Inspect adjacent code** - only when necessary for context

## Preferred Tools (Deterministic)

| Task | Tool |
|------|------|
| Find files by pattern | `find`, `glob`, `Get-ChildItem` |
| Search text | `rg`, `grep`, `Select-String` |
| Read file range | `sed -n '10,50p'`, `Get-Content -TotalCount` |
| C# symbols | Roslyn, `csharp-ls`, `dotnet-ast` |
| TypeScript symbols | `ts-morph`, TypeScript Compiler API, `tsc --noEmit` |
| Go to definition | LSP, Roslyn, TypeScript |
| Find references | LSP, Roslyn, TypeScript |

## Anti-Patterns to Avoid

- ❌ Reading entire large files (>500 lines)
- ❌ Loading multiple unrelated files into context
- ❌ Using LLM to parse code structure
- ❌ Grepping without context (false positives)

## Good Patterns

```bash
# Find all controller files
find src -name "*Controller.cs" -type f

# Get class definition only (lines 10-50)
sed -n '10,50p' src/Orders/OrderService.cs

# Search for DI registration pattern
rg "services\.Add" src/ --type cs

# Find all usages of IOrderService
rg "IOrderService" src/ --type cs

# Get method body only
# Use Roslyn/ts-morph to extract specific method
```

## Evidence Creation

When creating evidence from file analysis:

```bash
# Good - precise location
python knowledge.py add-evidence --data '{
  "source": "SRC-000001",
  "locator": {"type": "code_range", "path": "src/Orders/OrderService.cs", "line_start": 120, "line_end": 145},
  "observation": {"type": "text", "value": "class OrderService : IOrderService", "raw_text": "class OrderService : IOrderService {\n    ..."},
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-dotnet", "run": "RUN-000001"},
  "confidence": 1.0
}'

# Bad - vague location
# "somewhere in OrderService.cs"
```

## Caching

Cache parsed results in `.ai/cache/`:
- Key: `file_path + content_hash` (SHA256)
- Value: AST symbols, imports, exports, type declarations
- Invalidate on file change (git status / file mtime)