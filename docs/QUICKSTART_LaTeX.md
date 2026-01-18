# LaTeX Paper Quick Start Guide

## 🚀 Fastest Way to Get PDF

### Option 1: Overleaf (NO Installation Required!) ⭐ RECOMMENDED

1. **Go to Overleaf**: https://www.overleaf.com/
2. **Create Free Account** (or login)
3. **New Project** → **Upload Project**
4. **Upload these 2 files**:
   - `paper.tex`
   - `references.bib`
5. **Click "Recompile"** button
6. **Download PDF** (top right)

✅ **Done in 5 minutes!**

---

### Option 2: Windows - Install MiKTeX

1. **Download MiKTeX**: https://miktex.org/download
2. **Install** (30 minutes for full installation)
3. **Run PowerShell** as Administrator:
```powershell
cd "c:\Users\LENOVO\Documents\LLM ringan\docs"
.\compile_paper.ps1
```
4. **Wait** for compilation (~1 minute)
5. **Open** `paper.pdf`

---

## 📝 Before Compiling - MUST DO!

Edit `paper.tex` (line 29-37):

```latex
\author{
\IEEEauthorblockN{Your Name Here}  ← CHANGE THIS
\IEEEauthorblockA{\textit{Your Department} \\  ← CHANGE THIS
\textit{Your University}\\  ← CHANGE THIS
Jakarta, Indonesia \\  ← CHANGE THIS
your.email@uni.ac.id}  ← CHANGE THIS
}
```

---

## 📊 What You Get

- **Format**: IEEE Conference (two-column)
- **Pages**: ~10-12 pages
- **File Size**: ~300-400 KB
- **Quality**: Publication-ready PDF

**Includes:**
✅ 8 main sections
✅ 4 formatted tables
✅ Code listings with syntax highlighting
✅ Mathematical equations
✅ 30+ references (auto-formatted)
✅ Professional IEEE styling

---

## ❓ Troubleshooting

### "pdflatex not found"
→ Install MiKTeX or use Overleaf (no installation)

### "Bibliography not showing"
→ Run compilation 3 times (script does this automatically)

### "Missing packages"
→ MiKTeX will auto-download (internet required on first compile)

### "File too large to submit"
→ Current PDF is ~300 KB (well under 10 MB limits)

---

## 📤 Submitting to Conference/Journal

1. ✅ Update author info (see above)
2. ✅ Compile to PDF
3. ✅ Check page count matches venue limit
4. ✅ Verify all citations appear (not [?])
5. ✅ Submit `paper.pdf`

**Common page limits:**
- IEEE conferences: 6-10 pages
- ACM conferences: 10-12 pages
- Journals: 12-25 pages

Current paper: ~10-12 pages ✅ (fits most conferences)

---

## 🔧 Files You Need

**Essential:**
- `paper.tex` (main document)
- `references.bib` (bibliography)

**Generated (automatic):**
- `paper.pdf` (your final output!)

**Optional:**
- `compile_paper.ps1` (compilation script for Windows)
- `README_LaTeX.md` (detailed guide)

---

## 💡 Pro Tips

**Overleaf Advantages:**
- ✅ No installation
- ✅ Works on any OS (Windows/Mac/Linux)
- ✅ Auto-saves
- ✅ Real-time collaboration
- ✅ Built-in spell check
- ✅ One-click compile

**Local Installation Advantages:**
- ✅ Works offline
- ✅ Faster compilation
- ✅ Version control (Git)
- ✅ Custom templates

**Recommendation**: Start with Overleaf for quick PDF, then install locally if doing multiple revisions.

---

## 🎯 Success Checklist

After compilation, verify:

- [ ] **paper.pdf exists**
- [ ] **Author name updated** (not [Author Name])
- [ ] **All citations numbered** (not [?])
- [ ] **Bibliography appears** at end
- [ ] **Tables render correctly**
- [ ] **No compilation errors** in log
- [ ] **Page count**: 10-12 pages
- [ ] **File size**: <1 MB

If all checked → **READY TO SUBMIT!** ✅

---

**Need help?** See full guide in: `README_LaTeX.md`
