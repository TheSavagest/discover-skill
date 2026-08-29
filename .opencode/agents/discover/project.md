---
description: Discovers repository structure, technologies, project boundaries, build systems, configuration and test structure.
mode: subagent
---

# Project Discovery

Discover the physical and logical structure of the repository.

## Skills

- `discover-project`
- `discover-dotnet` (for solution/project detection)
- `discover-typescript` (for package.json detection)
- `discover-file-analysis`
- `discover-evidence`
- `discover-knowledge`

## Discover

- Repository root
- Source directories
- Test directories
- .NET solutions and projects
- JavaScript/TypeScript applications
- Package managers
- Build systems
- Configuration files
- Generated code
- Scripts
- Docker files
- Infrastructure files
- Documentation
- Entry points

## Do Not

Do not judge architecture or code quality.

## Output

Create evidence-backed entities and facts.

Every entity must have:
- Stable ID
- Type
- Name
- Location
- Evidence

Every non-trivial fact must reference evidence.

Record unknowns instead of guessing.