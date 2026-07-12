# Distribution Guide

How to publish and disseminate omics-skills across registries, marketplaces, and ecosystems.

---

## Overview

The [Agent Skills open standard](https://agentskills.io/specification) (released December 2025) enables cross-platform skill portability. Your skills will work across Claude Code, Codex CLI, ChatGPT, and other platforms that adopt the standard.

**Good news:** Your repository already follows the Agent Skills specification! Each skill has a `SKILL.md` with YAML frontmatter, making it ready for distribution.

---

## Distribution Channels

### 1. Claude Code / Cowork Plugin Marketplace ⭐ (Recommended)

**URL:** <https://claude.com/docs/plugins/submit>

**Purpose:** Public plugin directory for Cowork and Claude Code. A plugin can bundle skills, agents, MCP connectors, commands, and hooks into one installable package.

**Repository status:** This repository includes:
- `.claude-plugin/plugin.json` — plugin metadata
- `.claude-plugin/marketplace.json` — marketplace catalog
- `agents/` and `skills/` at the plugin root, which Claude Code discovers as plugin components

**Validate before submitting:**
```bash
claude plugin validate .
claude plugin validate --strict .
```

**Test direct install from GitHub:**
```bash
claude plugin marketplace add fmschulz/omics-skills
claude plugin install omics-skills@omics-skills
```

**Submit for review:**
- Claude.ai: <https://claude.ai/settings/plugins/submit>
- Console: <https://platform.claude.com/plugins/submit>

Use the public GitHub repository URL, `https://github.com/fmschulz/omics-skills`, when submitting. Anthropic's review pipeline runs `claude plugin validate` plus automated screening. Approved community plugins are added to the public Claude community catalog and updates are picked up from the GitHub repository automatically.

### 2. Official Repositories

#### Anthropic Skills Repository ⭐ (Recommended)
**URL:** [github.com/anthropics/skills](https://github.com/anthropics/skills)

**Purpose:** Official Anthropic-maintained public repository for Agent Skills

**How to Submit:**
1. Fork the repository
2. Add your skill(s) to the `skills/` directory
3. Follow their structure (see existing skills as examples)
4. Test your skill with Claude Code
5. Submit a pull request with clear documentation

**Benefits:**
- Official Anthropic visibility
- Auto-indexed by Claude Code plugin marketplace
- High trust/credibility
- Direct user installation via `/plugin install skill-name`

**What to Submit:**
- Individual skills (one PR per skill, or related skills together)
- Start with high-impact skills: `bio-logic`, `scientific-writing`, `beautiful-data-viz`
- Consider submitting agent-agnostic skills first

#### OpenAI Codex Skills Repository
**URL:** [github.com/openai/skills](https://github.com/openai/skills)

**Purpose:** Skills Catalog for Codex CLI

**How to Submit:**
1. Fork the repository
2. Add skill to appropriate category
3. Follow their contribution guidelines
4. Submit pull request

**Benefits:**
- Codex CLI users can discover your skills
- Cross-platform exposure (Agent Skills standard)

### 3. Community Marketplaces

#### SkillsMP (Skills Marketplace) ⭐
**URL:** [skillsmp.com](https://skillsmp.com)

**Purpose:** Community-driven aggregator with 71,000+ skills

**How to Submit:**
- **Automatic indexing:** Push your skills to GitHub - SkillsMP automatically indexes public repositories
- **Manual submission:** Contact via their site or submit your GitHub repo URL
- **GitHub tag:** Add topic tags like `claude-skills`, `agent-skills`, `bioinformatics`

**Benefits:**
- Largest skill aggregator
- Compatible with Claude Code, Codex CLI, ChatGPT
- Search and discovery features
- No approval process needed

**Action:**
```bash
# Add GitHub topics to your repo
# Go to: https://github.com/fmschulz/omics-skills
# Add topics: claude-skills, agent-skills, bioinformatics,
#             computational-biology, scientific-writing, data-visualization
```

#### SkillHub
**URL:** [skillhub.club](https://www.skillhub.club/)

**Purpose:** AI-evaluated Claude skills marketplace (7,000+ skills)

**How to Submit:**
- Create a SKILL.md file, push to GitHub, and it's automatically indexed
- Uses AI evaluation for quality scoring
- Compatible with Claude Code, Codex CLI, Gemini CLI, OpenCode

**Benefits:**
- Quality scoring helps users find best skills
- Multi-platform support
- Automatic indexing

#### MCP Market
**URL:** [mcpmarket.com/tools/skills](https://mcpmarket.com/tools/skills)

**Purpose:** Agent Skills directory for Claude.ai, Claude Code, Codex

**How to Submit:**
- Submit via their website
- Provide GitHub repository URL
- Include skill descriptions and categories

---

## 4. Your GitHub Repository

#### Make Your Repo Discoverable

**Current URL:** [github.com/fmschulz/omics-skills](https://github.com/fmschulz/omics-skills)

**Optimize for Discovery:**

1. **Add GitHub Topics:**
   ```
   claude-skills, agent-skills, claude-code, codex-cli,
   bioinformatics, computational-biology, omics,
   scientific-writing, data-visualization, genomics
   ```

2. **Complete Repository Description:**
   ```
   4 expert agents and 34 specialized skills for bioinformatics,
   scientific writing, and data visualization. Compatible with
   Claude Code and Codex CLI.
   ```

3. **Keep README badges accurate if used:**
   - Agent Skills standard badge
   - Compatible platforms badge
   - License badge

4. **Maintain GitHub Pages:**
   - Publish the MkDocs documentation site
   - Keep installation, skill catalog, and routing pages current

#### Repository Structure for Marketplaces

Marketplaces look for:
- Present: `SKILL.md` files with YAML frontmatter
- Present: clear directory structure
- Present: README documentation
- Present: `LICENSE` in the repository root
- Pending: add GitHub topics and tags

---

## 5. Community Listings

#### Awesome Lists

**awesome-claude-skills:**
- [github.com/travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [github.com/ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

**How to Submit:**
1. Fork the repository
2. Add your repository to appropriate category
3. Submit pull request with description

**Benefits:**
- Community visibility
- Curated lists are often referenced
- Good for specialized domains (bioinformatics)

#### Reddit & Forums

**Communities:**
- r/ClaudeAI
- r/Bioinformatics
- Anthropic Discord
- Bioinformatics forums

**How to Share:**
- Create announcement post
- State the measured scope: four agents, 34 skills, routing tests, and supported installers
- Include installation instructions
- Request feedback

---

## Step-by-Step Action Plan

### Phase 1: Immediate Actions (1-2 hours)

1. **Add GitHub Topics:**
   ```bash
   # Go to: https://github.com/fmschulz/omics-skills
   # Click "About" gear icon
   # Add topics: claude-skills, agent-skills, bioinformatics,
   #             computational-biology, scientific-writing, etc.
   ```

2. **Keep the root LICENSE file current.**

3. **Refresh README badges only when they are maintained:**
   ```markdown
   [![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](https://agentskills.io)
   [![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-green)](https://code.claude.com)
   [![Codex CLI](https://img.shields.io/badge/Codex%20CLI-Compatible-green)](https://developers.openai.com/codex)
   ```

4. **Push Updates:**
   ```bash
   git add .
   git commit -m "docs: refresh distribution metadata"
   git push
   ```

### Phase 2: Marketplace Submissions (2-3 days)

1. **Wait for Automatic Indexing:**
   - SkillsMP will auto-index within 24-48 hours
   - SkillHub will auto-index your repo
   - No action needed except GitHub topics

2. **Submit to Anthropic Official Repo:**
   - Fork [github.com/anthropics/skills](https://github.com/anthropics/skills)
   - Choose 3-5 best skills to submit initially:
     - `bio-logic` (universal reasoning skill)
     - `scientific-writing` (manuscript generation)
     - `beautiful-data-viz` (publication figures)
     - `notebooks` (marimo-first notebooks; Jupyter supported)
     - `bio-reads-qc-mapping` (sequencing data QC)
   - Add to `skills/` directory
   - Submit pull request with description
   - Reference your full repository for more skills

3. **Submit to OpenAI Codex:**
   - Fork [github.com/openai/skills](https://github.com/openai/skills)
   - Add 2-3 representative skills
   - Submit pull request

4. **Submit to MCP Market:**
   - Visit [mcpmarket.com](https://mcpmarket.com)
   - Submit repository URL
   - Add descriptions and categories

### Phase 3: Community Outreach (1 week)

1. **Awesome Lists:**
   - Submit to awesome-claude-skills
   - Create specialized awesome-bioinformatics-ai-skills?

2. **Social/Community:**
   - Reddit announcement (r/ClaudeAI, r/Bioinformatics)
   - Anthropic Discord announcement
   - Bioinformatics Slack/Discord groups
   - Twitter/X announcement with hashtags:
     ```
     #ClaudeCode #AgentSkills #Bioinformatics #ComputationalBiology
     ```

3. **Blog Post/Article:**
   - Explain the repository architecture, validation, and maintenance process
   - Share on Medium, Dev.to, or your blog
   - Technical walkthrough of skill development
   - Use case examples

### Phase 4: Ongoing Maintenance

1. **Monitor Issues:**
   - Watch for GitHub issues
   - Respond to user questions
   - Accept community contributions

2. **Update Skills:**
   - Keep skills current with tool updates
   - Add new skills based on user requests
   - Improve documentation based on feedback

3. **Track Adoption:**
   - GitHub stars/forks
   - Clone counts (if visible)
   - User feedback and issues

---

## Submission Templates

## Release Process

Use GitHub Releases as the canonical release-note surface. Do not keep a
separate root `CHANGELOG.md` unless the project later needs generated
offline release history.

For each release:

1. Choose a semantic version tag such as `v1.0.0`.
2. Add human-written release notes at `.github/releases/vX.Y.Z.md`.
3. Commit and push the release-ready docs, skills, agents, catalog, and tests.
4. Wait for CI and Docs to pass on `main`, then run `scripts/check_release_sync.py --tag vX.Y.Z --main-ref origin/main`.
5. Create an annotated tag from the verified `main` commit.
6. Push the tag. `.github/workflows/release.yml` verifies the tag, both manifests, release notes, and `origin/main` before publishing the GitHub Release
   from `.github/releases/<tag>.md`.
7. Verify the GitHub Release, source archives, installed plugin version, and documentation site.

Release notes should cover:
   - major user-facing changes
   - agent and skill coverage
   - installation or compatibility notes
   - validation commands run before release
Keep the README version badge pointed at the repository releases page.

### Pull Request Template (for Anthropic/OpenAI repos)

```markdown
## Skill Submission: [Skill Name]

**Description:** [One-line description]

**Domain:** Bioinformatics / Scientific Writing / Data Visualization

**Use Cases:**
- [Use case 1]
- [Use case 2]

**Tested With:**
- Claude Code: OK
- Codex CLI: OK

**Additional Notes:**
This skill is part of the omics-skills collection available at:
https://github.com/fmschulz/omics-skills

The collection includes 34 specialized skills and 4 expert agents for
computational biology workflows.
```

### Reddit Announcement Template

```markdown
Title: [Release] Omics Skills - Agent Skills for Bioinformatics with Claude Code/Codex

Omics Skills packages Agent Skills for computational biology:

**What it includes:**
- 4 expert agents (omics-scientist, literature-expert, science-writer, dataviz-artist)
- 34 specialized skills (reads QC, assembly, annotation, phylogenomics, literature, writing, visualization, etc.)
- Make and shell installation paths
- Works with Claude Code and Codex CLI

**Use cases:**
- Genome/metagenome assembly and annotation
- Scientific manuscript writing with literature search
- Publication-quality data visualization

**Repository:** https://github.com/fmschulz/omics-skills

**Installation:**
```bash
git clone https://github.com/fmschulz/omics-skills.git
cd omics-skills
make install
```

Feedback and contributions are welcome.
```

---

## Expected Outcomes

### Short-term (1-2 weeks)
- Automatic indexing by SkillsMP and SkillHub
- GitHub stars and community interest
- Initial user feedback

### Medium-term (1-2 months)
- Official repo acceptance (Anthropic/OpenAI)
- Integration with Claude Code plugin marketplace
- Community contributions

### Long-term (3-6 months)
- Recurring use in bioinformatics projects
- Multiple contributors
- Adoption in academic/research settings

---

## Facts to Cite

Use claims that the repository can substantiate:

1. **Bioinformatics Workflow Coverage**
   - Covers reads, assembly, annotation, comparative analysis, literature, writing, and visualization
   - Routes tasks through a generated catalog with a regression benchmark

2. **Four Agent Definitions**
   - Includes omics-scientist, literature-expert, science-writer, and dataviz-artist
   - Each agent maps task patterns and workflow steps to installed skills

3. **Repository Validation**
   - Checks skill structure, links, catalog consistency, routing, installers, and documentation
   - Supports Make and shell installation paths

4. **Cross-Platform**
   - Claude Code
   - Codex CLI
   - Follows Agent Skills open standard

5. **Academic/Research Focus**
   - Literature-backed (summaries/ directories with papers)
   - Best practices from scientific community
   - Reproducibility emphasis

---

## Resources

### Official Documentation
- [Agent Skills Specification](https://agentskills.io/specification)
- [Anthropic Skills GitHub](https://github.com/anthropics/skills)
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)
- [Agent Skills Blog Post](https://claude.com/blog/skills)

### Community Resources
- [SkillsMP Marketplace](https://skillsmp.com)
- [SkillHub](https://www.skillhub.club/)
- [MCP Market](https://mcpmarket.com)
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)

### Tools
- [agent-skills-cli](https://github.com/Karanjot786/agent-skills-cli) - Universal CLI for syncing skills

---

## Questions to Consider

1. **Licensing:** Choose appropriate license (MIT, Apache 2.0, GPL)
2. **Contribution Guidelines:** Accept external contributions?
3. **Maintenance:** Who maintains? How often update?
4. **Versioning:** Use semantic versioning for skills?
5. **Support:** How to provide user support? (GitHub issues, Discord, etc.)

---

## Next Steps Checklist

- [ ] Add GitHub topics to repository
- [ ] Confirm root LICENSE file is current
- [ ] Refresh README badges only if they remain accurate
- [ ] Push updates to GitHub
- [ ] Wait for auto-indexing (SkillsMP, SkillHub)
- [ ] Submit to Anthropic skills repository
- [ ] Submit to OpenAI Codex skills
- [ ] Submit to MCP Market
- [ ] Post announcement on Reddit
- [ ] Share on Twitter/X
- [ ] Submit to awesome-claude-skills lists
- [ ] Write blog post/article
- [ ] Monitor and respond to feedback

---

Keep this page current when the agent or skill counts change.
