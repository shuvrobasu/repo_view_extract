# JSON Code Repository Viewer

A professional desktop application for browsing, analyzing, and extracting code from large JSON repositories and Python codebases.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

<img width="1920" height="1040" alt="image" src="https://github.com/user-attachments/assets/c4f04b38-1a86-4e8e-8251-02f5c7953a38" />

## Features

### Core Functionality

- **Large File Support**: Handle JSON files up to 2GB with efficient streaming
- **Folder Scanning**: Recursively scan directories for Python files
- **Smart Pagination**: Browse thousands of records with 50 records per page
- **Syntax Highlighting**: Python code highlighting with keyword, string, and comment detection
- **Synchronized Line Numbers**: Professional code viewing experience

### Advanced Filtering

- **Multi-Type Filter**: Filter by 10+ code categories (GUI, AI/ML, Web/API, etc.)
- **Size Range Filter**: Filter files by size (1KB - 100MB)
- **Quality Filter**: Filter by code quality score (★☆☆ to ★★★)
- **Text Search**: Search by repo name, path, or content with case-sensitive option
- **Live Preview**: See filter results before applying

### Code Quality Analysis

- **Automated Scoring**: 12-point quality metric system
- **Quality Breakdown**: View specific quality indicators
  - Docstrings presence
  - Type hints usage
  - Comment ratio
  - Line length compliance
  - Import quality
  - Exception handling
  - Code complexity
  - And more...

### Export & Extraction

- **Single File Export**: Extract individual code files
- **Bulk Export**: Export all or filtered records
- **Smart Filename Handling**: Automatic sanitization and collision avoidance
- **Long Path Support**: Auto-generated names for Windows filename limits

### Performance Optimization

- **3-Tier Lazy Loading**:
  - T1: Instant name/size display
  - T2: Background LOC/type/quality calculation
  - T3: On-demand full quality metrics
- **Smart Caching**: Metrics cached to avoid recalculation
- **Background Processing**: Non-blocking UI during heavy operations

## Installation

### Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)

### Dependencies

No external dependencies required! Uses only Python standard library.

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/json-code-viewer.git

# Navigate to directory
cd json-code-viewer

# Run the application
python Repo_view_extract.py
```

## Usage

### Opening Files

**JSON File (NDJSON/JSON Lines)**
```
File > Open JSON File (Ctrl+O)
```

Supports both array-based JSON `[{...}, {...}]` and newline-delimited JSON.

**Folder Scanning**
```
File > Open Folder (Ctrl+Shift+O)
```

Recursively scans for `.py` files, excluding `__pycache__`, `venv`, `.git`, etc.

### Searching & Filtering

**Text Search (Ctrl+F)**

- Search by: Repo Name, Path, or Content
- Case-sensitive option
- Live result preview
- Persists across sessions until cleared

**Type & Size Filter (Ctrl+T)**

- Select from 10 code types:
  - GUI (tkinter, PyQt, etc.)
  - AI/ML (tensorflow, torch, etc.)
  - Data Processing (pandas, numpy, etc.)
  - Image Processing (PIL, opencv, etc.)
  - Web/API (flask, django, etc.)
  - Database (sqlite, sqlalchemy, etc.)
  - Algorithm & more...
- Size range: 1KB to 100MB
- Quality threshold: Any, 20%+, 40%+, 70%+
- Preview matching records before applying

**Clear Filters (Ctrl+R or ESC)**

### Exporting Code

**Extract Current Record**
```
Tools > Extract Code
```

Save currently selected code to file with smart filename handling.

**Export All/Filtered**
```
Tools > Export All Codes
```

- Exports all records or currently filtered subset
- Automatic filename sanitization
- Collision avoidance with counter suffixes
- Progress tracking for large exports

### Viewing Statistics

**Repository Statistics**
```
Tools > Statistics
```

Displays:

- Total records and size
- License distribution (top 10)
- File extension breakdown (top 10)
- Visual bar charts

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open JSON file |
| `Ctrl+Shift+O` | Open folder |
| `Ctrl+F` | Search records |
| `Ctrl+T` | Type/Size filter |
| `Ctrl+R` | Clear filter |
| `Ctrl+Shift+C` | Copy code |
| `Ctrl+Q` | Quit application |
| `ESC` | Clear filter |

## Code Type Detection

The application automatically detects code types based on:

1. **Import Analysis**: Identifies libraries used
2. **Path Keywords**: Examines file paths for hints
3. **Content Patterns**: Analyzes code structure

### Supported Categories

- **GUI**: tkinter, PyQt, PySide, wx, kivy, pygame
- **AI/ML**: tensorflow, keras, torch, sklearn, transformers
- **Data Processing**: pandas, numpy, scipy, dask
- **Image Processing**: PIL, opencv, scikit-image
- **Web/API**: flask, django, fastapi, requests
- **Database**: sqlite3, sqlalchemy, pymongo, redis
- **Algorithm**: collections, heapq, bisect, itertools
- **Testing**: pytest, unittest, nose, mock
- **Networking**: socket, asyncio, twisted, paramiko
- **Automation**: subprocess, shutil, selenium, schedule

## Quality Metrics

### Scoring System (62 points max)

| Metric | Weight | Description |
|--------|--------|-------------|
| Has Docstrings | 10 | Module/function documentation |
| Type Hints | 8 | Function annotations |
| Good Comment Ratio | 7 | 5-40% comments |
| Line Length | 5 | <120 chars per line |
| No Wildcard Imports | 5 | Avoids `import *` |
| Functions/Classes | 5 | Structured code |
| Good Naming | 5 | Meaningful identifiers |
| No Bare Except | 4 | Specific exceptions |
| No eval/exec | 4 | Safe code practices |
| Reasonable Complexity | 4 | Max 5 nesting levels |
| Exception Handling | 3 | try/except blocks |
| No Magic Numbers | 2 | Few hardcoded values |

### Quality Tiers

- **★★★** (70%+): High quality, well-documented code
- **★★☆** (40-69%): Moderate quality, some best practices
- **★☆☆** (<40%): Basic code, needs improvement

## File Handling

### Safe Filename Generation

- Removes invalid characters: `< > : " / \ | ? *`
- Strips control characters
- Handles long paths (255 char Windows limit)
- Auto-generates random names when needed
- Prevents collisions with counter suffixes

### Supported Formats

- **Input**: `.json`, `.jsonl`, `.ndjson`, Python directories
- **Output**: `.py` files with original or sanitized names

## Performance

### Optimizations

- **Streaming JSON**: Processes large files line-by-line
- **Lazy Metrics**: Calculates quality scores on-demand
- **Background Scanning**: Non-blocking T2 metric calculation
- **Smart Caching**: Stores computed metrics in memory
- **Pagination**: Renders only visible records

### Tested Limits

- ✅ 2GB JSON files
- ✅ 100,000+ code records
- ✅ 10MB+ individual files
- ✅ 10,000+ file folder scans

## Troubleshooting

### Large File Loading

**Issue**: File takes long to load  
**Solution**: Use progress bar to monitor. Cancel with window close if needed.

### No Results in Filter

**Issue**: Filter returns 0 results  
**Solution**: Application prompts to clear filter automatically.

### Long Filenames on Windows

**Issue**: Export fails with long paths  
**Solution**: Auto-generates random 12-char names when limit exceeded.

### Slow Quality Calculation

**Issue**: Quality scores show "..."  
**Solution**: Background scan runs automatically. Wait for completion or view current record to force calculation.

## Technical Details

### Architecture
```
JSONCodeViewer (Main Class)
|
+-- Data Storage
|   |
|   +-- records: List[Dict]
|   +-- filtered_indices: List[int]
|   +-- record_cache: Dict[int, Dict]
|
+-- UI Components
|   |
|   +-- Treeview (record list)
|   +-- Code viewer with line numbers
|   +-- Metadata display
|
+-- Metrics System
|   |
|   +-- T1: Name/Size (instant)
|   +-- T2: LOC/Type/Quality (background)
|   +-- T3: Full quality breakdown (on-demand)
|
+-- Export System
    |
    +-- Safe filename generation
    +-- Bulk export with progress
```

### Code Structure

- **GUI Framework**: tkinter with ttk styling
- **Threading**: Background loading and metric calculation
- **Data Model**: In-memory record list with filtered indices
- **Caching**: Dictionary-based metric storage

## Contributing

Contributions welcome! Areas for enhancement:

- Additional code type detectors
- More quality metrics
- Export format options (CSV, HTML)
- Diff/comparison features
- Git integration

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built for analyzing large code repositories from datasets like:

- GitHub Code Archive
- The Stack (Hugging Face)
- CodeSearchNet
- Custom code collections

## Screenshots

<img width="1920" height="1040" alt="image" src="https://github.com/user-attachments/assets/580033ea-6e10-46c3-9159-6ca219e5d3c7" />


## Contact

Issues and feature requests: [GitHub Issues](https://github.com/shuvrobasu/repo_view_extract/issues)

---

**Made with ❤️ for developers who wrangle big code datasets**
