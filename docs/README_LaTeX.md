# LaTeX Version - MicroLLM-PrivateStack Academic Paper

## Files Overview

### Main LaTeX Files

1. **`paper.tex`** - Main LaTeX source file (IEEE conference format)
2. **`references.bib`** - BibTeX bibliography file with 30+ references
3. **`compile_paper.ps1`** - PowerShell compilation script

### Output

- **`paper.pdf`** - Compiled PDF (generated after compilation)

## Prerequisites

### Option 1: Install MiKTeX (Recommended for Windows)

1. Download MiKTeX from: https://miktex.org/download
2. Run installer and select "Install missing packages on-the-fly: Yes"
3. This includes: pdflatex, bibtex, and all required packages

### Option 2: Install TeX Live (Cross-platform)

1. Download TeX Live from: https://www.tug.org/texlive/
2. Full installation (~7GB) includes all packages
3. Works on Windows, Mac, Linux

### Option 3: Use Overleaf (Online, No Installation)

1. Go to: https://www.overleaf.com/
2. Create free account
3. New Project → Upload Project
4. Upload `paper.tex` and `references.bib`
5. Compile online (click Recompile button)

## Compilation Instructions

### Method 1: Using PowerShell Script (Easiest)

```powershell
# Navigate to docs folder
cd "c:\Users\LENOVO\Documents\LLM ringan\docs"

# Run compilation script
.\compile_paper.ps1
```

The script will:
- Check if pdflatex and bibtex are installed
- Run compilation in correct order (4 passes)
- Generate `paper.pdf`
- Optionally clean up auxiliary files

### Method 2: Manual Compilation (Command Line)

```powershell
# Navigate to docs folder
cd "c:\Users\LENOVO\Documents\LLM ringan\docs"

# First pass (generate .aux file)
pdflatex paper.tex

# Process bibliography
bibtex paper

# Second pass (resolve citations)
pdflatex paper.tex

# Third pass (resolve cross-references)
pdflatex paper.tex
```

### Method 3: Using LaTeX Editor

**TeXworks** (included with MiKTeX):
1. Open `paper.tex` in TeXworks
2. Select "pdfLaTeX" from dropdown
3. Click green "Typeset" button
4. Run 3 times total (for bibliography + references)

**TeXstudio** (Advanced):
1. Download from: https://www.texstudio.org/
2. Open `paper.tex`
3. Tools → Build & View (F5)
4. Automatically handles multiple passes

### Method 4: VSCode with LaTeX Workshop

1. Install extension: "LaTeX Workshop"
2. Open `paper.tex` in VSCode
3. Save file (Ctrl+S)
4. Extension auto-compiles on save

## Customization Before Compilation

### 1. Update Author Information (Lines 29-37)

```latex
\author{
\IEEEauthorblockN{Your Full Name}
\IEEEauthorblockA{\textit{Department of Computer Science} \\
\textit{Your University}\\
Jakarta, Indonesia \\
your.email@university.ac.id}
}
```

### 2. Add Co-Authors (Optional)

```latex
\author{
\IEEEauthorblockN{First Author}
\IEEEauthorblockA{\textit{Dept. CS} \\
\textit{University A}\\
City, Country \\
email1@uni.edu}
\and
\IEEEauthorblockN{Second Author}
\IEEEauthorblockA{\textit{Dept. AI} \\
\textit{University B}\\
City, Country \\
email2@uni.edu}
}
```

### 3. Add Acknowledgments (Before Bibliography)

```latex
\section*{Acknowledgment}
This research was supported by [Funding Source]. 
The authors would like to thank [Names] for their valuable feedback.
```

## LaTeX Document Structure

```
paper.tex
├── Preamble (documentclass, packages, settings)
├── Title & Author Information
├── Abstract
├── Keywords
├── Section 1: Introduction
│   ├── 1.1 Latar Belakang
│   ├── 1.2 Problem Statement
│   ├── 1.3 Kontribusi
│   └── 1.4 Batasan
├── Section 2: Related Work (5 subsections)
├── Section 3: Architecture (6 subsections)
├── Section 4: Implementation (4 subsections)
├── Section 5: Evaluation (4 subsections)
├── Section 6: Use Cases (4 subsections)
├── Section 7: Discussion (3 subsections)
├── Section 8: Conclusion
└── Bibliography (auto-generated from references.bib)
```

## Tables Included

The LaTeX version includes properly formatted IEEE-style tables:

1. **Table I**: DeepSeek 1.5B Model Specifications
2. **Table II**: Semantic Caching Performance
3. **Table III**: Time to First Token (TTFT) Measurements
4. **Table IV**: 3-Year TCO Comparison

## Code Listings

Code examples formatted with `listings` package:
- Python code for input sanitization
- Properly syntax-highlighted
- Line numbers included
- Professional formatting

## Equations

Mathematical formulas for:
1. Cosine similarity (semantic caching)
2. Risk scoring formula

## Troubleshooting

### Error: "pdflatex not found"

**Solution**: Install MiKTeX or TeX Live (see Prerequisites above)

### Error: "Missing package XYZ"

**Solution**: 
- MiKTeX: Will auto-install on first compile
- TeX Live: Run `tlmgr install <package-name>`

### Error: "Bibliography not appearing"

**Solution**: Make sure you run compilation in correct order:
1. pdflatex
2. bibtex
3. pdflatex
4. pdflatex

### Warning: "Citation undefined"

**Solution**: Normal on first pass, run pdflatex again after bibtex

### PDF looks wrong / formatting issues

**Solution**: 
- Ensure using IEEE document class: `\documentclass[conference]{IEEEtran}`
- Clear auxiliary files and recompile
- Check for missing `\end{...}` tags

## Converting to Other Formats

### To ACM Format

Replace first line:
```latex
\documentclass[sigconf]{acmart}
```

### To Two-Column Article

```latex
\documentclass[twocolumn]{article}
```

### To Single-Column (for review)

Remove `conference` option:
```latex
\documentclass{IEEEtran}
```

## File Size Optimization

Current compiled PDF: ~300-400 KB (text only)

If adding images:
```latex
\usepackage{graphicx}
\includegraphics[width=\columnwidth]{figure.png}
```

Optimize images before including:
- Use PNG for diagrams (not JPG)
- Maximum 300 DPI for print
- Compress with tools like TinyPNG

## Submission Checklist

Before submitting to conference/journal:

- [ ] Update author information
- [ ] Remove `[Author Name]` placeholders
- [ ] Verify all citations compile correctly
- [ ] Check page limit (IEEE conferences typically 6-10 pages)
- [ ] Run spell check (F7 in TeXstudio)
- [ ] Verify all tables/figures are referenced in text
- [ ] Add acknowledgments if required
- [ ] Generate final PDF with high quality settings
- [ ] Check PDF file size (most venues: <10 MB)

## Advanced: Camera-Ready Version

If paper is accepted, for final camera-ready:

1. **Add IEEE copyright notice** (bottom of first page):
```latex
\IEEEoverridecommandlockouts
\IEEEpubid{\makebox[\columnwidth]{978-1-xxxx-xxxx-x/26/\$31.00~\copyright~2026 IEEE \hfill} \hspace{\columnsep}\makebox[\columnwidth]{ }}
```

2. **Embed all fonts**:
```powershell
pdflatex -output-format=pdf paper.tex
```

3. **Verify PDF/A compliance** (if required):
Use Adobe Acrobat Pro or online tools

## Quick Reference: Common LaTeX Commands

### Text Formatting
- Bold: `\textbf{text}`
- Italic: `\textit{text}`
- Typewriter: `\texttt{code}`

### Lists
```latex
\begin{itemize}
  \item Bullet point
\end{itemize}

\begin{enumerate}
  \item Numbered item
\end{enumerate}
```

### Citations
- In text: `\cite{authorYYYY}`
- Multiple: `\cite{author1YYYY, author2YYYY}`

### Cross-References
```latex
\section{Introduction}
\label{sec:intro}

As discussed in Section~\ref{sec:intro}...
See Table~\ref{tab:results}...
```

## Getting Help

**LaTeX Documentation**:
- TeX StackExchange: https://tex.stackexchange.com/
- Overleaf Tutorials: https://www.overleaf.com/learn
- IEEE Author Tools: https://journals.ieeeauthorcenter.ieee.org/

**MiKTeX Issues**:
- Official docs: https://miktex.org/kb
- Package manager: MiKTeX Console

**BibTeX Issues**:
- Format guide: http://www.bibtex.org/Format/
- Entry types: @article, @inproceedings, @misc, etc.

## Files Generated During Compilation

After compilation, you'll see these files:

- **paper.pdf** ✅ (FINAL OUTPUT - This is what you submit!)
- paper.aux (auxiliary file with references)
- paper.log (compilation log, useful for debugging)
- paper.bbl (processed bibliography)
- paper.blg (bibliography log)
- paper.out (hyperref outline)

**Which files to keep?**
- Keep: `paper.tex`, `references.bib`, `paper.pdf`
- Delete/ignore: `.aux`, `.log`, `.bbl`, `.blg`, `.out`

## Success Indicators

After successful compilation:

✅ **paper.pdf exists** in docs folder
✅ **No errors** in compilation log (warnings OK)
✅ **Bibliography appears** at end of document
✅ **Citations show** as [1], [2], etc. (not [?])
✅ **Tables formatted** correctly in two-column layout
✅ **Page count**: ~8-12 pages (IEEE format)

---

**LaTeX Version Status:** ✅ Ready to Compile
**Estimated Compilation Time:** 20-30 seconds (first time, longer with package installation)
**Output Format:** IEEE Conference Two-Column
**Page Count:** ~10-12 pages
