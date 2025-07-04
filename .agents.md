# agents.md

## System Overview

This system ingests all readable knowledge files in a user-specified folder, consolidates and transforms them into a shuffled, chunked ePub for Kindle upload. It prevents re-processing of duplicate files by maintaining a memory ledger.

## Agent Registry

### Warp Agents

#### 1. `scanner-agent`

* **Role**: Worker
* **Task**: Recursively scans a user-specified directory for eligible files (.pdf, .md, .txt, .html).
* **Prompt**: Prompts the user to enter the path to the folder to scan.
* **Memory**: Uses a JSON memory ledger (`ledger.json`) to skip files already ingested.
* **Output**: Emits list of new files for ingestion.

#### 2. `merge-agent`

* **Role**: Worker
* **Task**: Merges the contents of all incoming files into a single unified text stream.
* **Coordination**: Triggered after `scanner-agent` completes.

#### 3. `chunk-agent`

* **Role**: Worker
* **Task**: Breaks the merged text into 20,000 character segments.
* **Output**: List of file-safe content chunks with metadata.

#### 4. `shuffle-agent`

* **Role**: Specialist
* **Task**: Randomizes the order of content chunks to introduce variety in ePub formatting.
* **Failure Handling**: Reverts to original order if shuffling fails.

#### 5. `epub-agent`

* **Role**: Specialist
* **Task**: Converts the shuffled chunks to `.epub` format using `pandoc` or similar CLI tool.
* **Output**: Stores resulting `.epub` files in `kindle/` directory.

### Codex Agents

#### 1. `dedup-agent`

* **Role**: Guardian
* **Task**: Maintains the state of ingested files by hashing file paths and contents.
* **Storage**: Updates `ledger.json` with hashes and timestamps.
* **Coordination**: Runs before every new ingestion pass.

#### 2. `path-checker`

* **Role**: Observer
* **Task**: Validates all paths and ensures symlink loops or unreadable files are excluded.
* **Fallback**: Skips files with unreadable characters or unsafe locations.

#### 3. `error-handler`

* **Role**: Orchestrator
* **Task**: Catches and logs agent errors, retries failed steps, and alerts via Warp terminal overlay.
* **Output**: Annotated `.log` files for human review.

## Agentic Workflow Protocol

* **Reasoning**: "Only process files not already ingested; convert and shuffle for reading diversity."
* **Tools**:

  * `!tool pandoc`
  * `!tool jq`
* **Directives**:

  * `!if file:new => scan > merge > chunk > shuffle > epub`
  * `!mutex_lock name:epub_build`

## State Management

* format: `json://ledger.json`
* fields:

  * `file_hashes`
  * `last_run`
  * `epub_count`

## Coordination Model

* **Orchestration**: Central control via `error-handler` and `scanner-agent`
* **Choreography**: Stateless agents triggered sequentially on output dependencies

## Change History

* **v1.0** – Initial agent specification for knowledgebase-to-epub pipeline
* **v1.1** – Modified `scanner-agent` to prompt user for path instead of using fixed `$USER/knowledgebase`
