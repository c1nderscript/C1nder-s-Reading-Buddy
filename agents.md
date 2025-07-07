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

# agents.md

## System Overview

This system provides a modular pipeline for consolidating knowledge bases into chunked PDF documents. It recursively scans directories, converts supported file formats to PDF, merges them per folder, and splits results into ~20,000 word chunks. The system maintains a ledger to track processed files and avoid duplicate work.

## Agent Registry

### Core Processing Agents

#### 1. `scanner-agent`
* **Role**: Discovery Worker
* **Implementation**: `orchestrate_all.py::scan_and_convert()`
* **Task**: Recursively scans user-specified directories for eligible files (.pdf, .md, .txt, .html, .docx, etc.)
* **Prompt**: Interactive prompts for source folder path and output configuration
* **Memory**: Uses JSON ledger (`ledger.json`) with file hashes to skip already processed files
* **Output**: Converted PDF files in `Converted/` directory structure
* **Features**: Supports 15+ file formats including Markdown, DOCX, HTML, TOML, and ebook formats

#### 2. `converter-agent`
* **Role**: Transformation Worker  
* **Implementation**: `orchestrate_all.py::convert_file()`
* **Task**: Converts supported file formats to PDF using appropriate conversion methods
* **Methods**:
  - Direct PDF copy for existing PDFs
  - FPDF rendering for Markdown/MDX (avoids LaTeX dependency)
  - Pandoc conversion for other formats (DOCX, HTML, TOML, etc.)
* **Font Handling**: Uses DejaVu Sans TrueType font for Unicode character support
* **Error Handling**: Graceful fallback and cleanup for failed conversions

#### 3. `merge-agent`
* **Role**: Consolidation Worker
* **Implementation**: `orchestrate_all.py::merge_pdfs()`
* **Task**: Merges all PDFs in a folder into a single unified document
* **Library**: Uses PyPDF2/pypdf for PDF manipulation
* **Output**: Single merged PDF in `Merged/` directory
* **Validation**: Skips empty or corrupted PDF files during merge

#### 4. `chunk-agent`
* **Role**: Segmentation Worker
* **Implementation**: `orchestrate_all.py::chunk_pdf()`
* **Task**: Splits merged PDFs into ~20,000 word segments
* **Method**: Text extraction followed by word-based chunking
* **Output**: Numbered PDF chunks in configurable output directory
* **Format**: `{base_name}_{chunk_number:03d}.pdf`

### Legacy Pipeline Agents (Shell-based)

#### 1. `markdown-merge-agent`
* **Role**: Text Consolidation Worker
* **Implementation**: `merge.sh`
* **Task**: Merges markdown files with JSX filtering into single document
* **Features**: Removes JSX components, adds file headers and separators
* **Output**: `Merged/merged_output.md`

#### 2. `text-splitter-agent`
* **Role**: Text Segmentation Worker
* **Implementation**: `split_markdown.sh`
* **Task**: Splits large markdown files into 20,000 character chunks
* **Method**: Character-based splitting with line preservation
* **Output**: Numbered markdown files in `Split/` directory

#### 3. `shuffle-agent`
* **Role**: Randomization Specialist
* **Implementation**: `shuffle_split_files.sh`
* **Task**: Randomizes order of split files for reading variety
* **Method**: Uses `shuf` utility for index randomization
* **Safety**: Temporary file renaming to prevent overwrites

#### 4. `kindle-converter-agent`
* **Role**: E-reader Format Specialist
* **Implementation**: `convert_to_kindle.sh`
* **Task**: Converts markdown chunks to Kindle-compatible formats
* **Methods**: 
  - Pandoc for MD → EPUB conversion
  - Optional kindlegen for EPUB → MOBI conversion
* **Output**: E-reader files in `Kindle/` directory

### Support Agents

#### 1. `ledger-agent`
* **Role**: State Management Guardian
* **Implementation**: `orchestrate_all.py::load_ledger()`, `save_ledger()`
* **Task**: Maintains processing state and prevents duplicate work
* **Storage**: JSON format with file hashes and timestamps
* **Fields**:
  - `folders`: Per-folder file hash tracking
  - `output_dir`: User's preferred output location
* **Coordination**: Runs before and after processing cycles

#### 2. `hash-validator`
* **Role**: Integrity Observer
* **Implementation**: `orchestrate_all.py::compute_hash()`
* **Task**: Generates SHA256 hashes for change detection
* **Method**: Streaming hash computation for large files
* **Purpose**: Enables incremental processing and change detection

#### 3. `logger-agent`
* **Role**: Audit Trail Recorder
* **Implementation**: `orchestrate_all.py::log()`
* **Task**: Records processing events with timestamps
* **Output**: Structured logs in `Logs/workflow.log`
* **Format**: ISO timestamp + descriptive message

#### 4. `environment-validator`
* **Role**: Dependency Guardian
* **Implementation**: `configure.sh`
* **Task**: Validates and installs required system dependencies
* **Dependencies**:
  - Python 3 with virtual environment
  - Font packages (DejaVu, Noto, Liberation)
  - Pandoc for format conversion
* **Platform**: Optimized for Debian/Ubuntu systems

## Agentic Workflow Protocols

### Primary Pipeline (PDF-focused)
```
User Input → scanner-agent → converter-agent → merge-agent → chunk-agent → Output
                ↓
           ledger-agent (state tracking)
                ↓
           logger-agent (audit trail)
```

### Legacy Pipeline (Markdown-focused)
```
Input → markdown-merge-agent → text-splitter-agent → shuffle-agent → kindle-converter-agent
```

### Tools and Dependencies
* **PDF Processing**: PyPDF2/pypdf, FPDF
* **Format Conversion**: Pandoc
* **Font Rendering**: DejaVu Sans TrueType
* **Text Processing**: Standard Unix utilities (shuf, grep)
* **Optional E-reader**: kindlegen for MOBI format

### Coordination Models

#### Orchestrated Flow
* **Controller**: `orchestrate_all.py` provides centralized workflow management
* **Interactive**: User prompts for source paths and configuration
* **Stateful**: Ledger-based incremental processing
* **Resilient**: Error handling with graceful degradation

#### Choreographed Flow
* **Controller**: `ingest_and_convert.sh` chains shell scripts
* **Sequential**: Linear pipeline with intermediate file storage
* **Stateless**: Each script operates independently
* **Legacy**: Maintained for backward compatibility

## State Management

### Ledger Format
```json
{
  "folders": {
    "folder_name": {
      "file_path": "sha256_hash"
    }
  },
  "output_dir": "/path/to/chunks",
  "last_run": "2025-01-01T00:00:00"
}
```

### Directory Structure
```
.
├── Converted/          # Temporary PDFs per source folder
├── Merged/            # Final merged PDFs
├── Chunks/            # Chunked outputs (~20k words)
├── Logs/              # Processing logs
├── ledger.json        # State tracking
└── [Legacy dirs: Ingest/, Split/, Kindle/]
```

## Configuration and Environment

### Environment Variables
* `KB_DIR`: Override default knowledge base location
* `BASE_DIR`: Override working directory for scripts

### User Interaction Points
1. Source folder selection
2. Output directory configuration  
3. Base name for merged files
4. Output directory confirmation (subsequent runs)

## Error Handling and Resilience

### File Processing Errors
* **Conversion Failures**: Logged and skipped, processing continues
* **Empty PDFs**: Detected and excluded from merge operations
* **Unicode Issues**: Character filtering for FPDF compatibility

### System Dependencies
* **Missing Pandoc**: Graceful failure with installation instructions
* **Font Availability**: Fallback font handling
* **Permission Issues**: Clear error messages for directory access

## Testing Infrastructure

### Test Coverage
* **Script Executability**: Validates all shell scripts are executable
* **Runtime Validation**: Tests core Python script execution
* **Environment Setup**: Validates virtual environment creation

### Test Files
* `tests/test_scripts.py`: Script permission validation
* `tests/test_ingest_runtime.py`: Runtime behavior testing

## Change History

* **v2.0** - PDF-focused pipeline with FPDF rendering and chunking
* **v1.1** - Interactive user prompts and configurable output directories  
* **v1.0** - Shell-based markdown pipeline with Kindle conversion
