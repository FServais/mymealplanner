import React, { useState, useEffect } from 'react';
import {
    getSourceFiles,
    getRecipes,
    patchRecipeIngredients,
    extractPdfText
} from '../services/api';
import {
    ChevronLeft,
    ChevronRight,
    Upload,
    FileText,
    ExternalLink,
    Plus,
    X,
    Save,
    Sparkles,
    Check,
    AlertCircle
} from 'lucide-react';

// efarmz CDN URL for recipe PDFs
const EFARMZ_CDN_BASE = 'https://cdn.efarmz.be/recipes/FR';

function getCdnPdfUrl(filename) {
    if (!filename) return null;
    return `${EFARMZ_CDN_BASE}/${encodeURIComponent(filename)}`;
}

function BulkReview() {
    // Filter state
    const [sourceFiles, setSourceFiles] = useState([]);
    const [selectedSourceFile, setSelectedSourceFile] = useState('');

    // Recipe list state
    const [recipes, setRecipes] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);

    // Current recipe editing state
    const [ingredients, setIngredients] = useState([]);
    const [hasChanges, setHasChanges] = useState(false);
    const [saving, setSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState(null);

    // PDF state
    const [pdfUrl, setPdfUrl] = useState(null);
    const [pdfFile, setPdfFile] = useState(null);
    const [showRawText, setShowRawText] = useState(false);
    const [rawText, setRawText] = useState('');
    const [rawLines, setRawLines] = useState([]);
    const [extracting, setExtracting] = useState(false);

    const currentRecipe = recipes[currentIndex];

    // Load source files on mount
    useEffect(() => {
        loadSourceFiles();
    }, []);

    // Load recipes when source file changes
    useEffect(() => {
        async function fetchRecipes() {
            if (!selectedSourceFile) return;
            setLoading(true);
            try {
                const response = await getRecipes({ source_file: selectedSourceFile, limit: 500 });
                setRecipes(response.data);
                setCurrentIndex(0);
            } catch (error) {
                console.error('Failed to load recipes:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchRecipes();
    }, [selectedSourceFile]);

    // Update ingredients when recipe changes
    useEffect(() => {
        if (currentRecipe) {
            setIngredients(currentRecipe.ingredients.map(i => ({ ...i })));
            setHasChanges(false);
            setSaveMessage(null);
            setRawText('');
            setRawLines([]);
            setPdfFile(null);

            // Set PDF URL from efarmz CDN based on source_file
            if (currentRecipe.source_file) {
                setPdfUrl(getCdnPdfUrl(currentRecipe.source_file));
            } else {
                setPdfUrl(null);
            }
        }
    }, [currentRecipe]);

    async function loadSourceFiles() {
        try {
            const response = await getSourceFiles();
            setSourceFiles(response.data);
        } catch (error) {
            console.error('Failed to load source files:', error);
        }
    }

    function updateIngredient(index, field, value) {
        const updated = [...ingredients];
        updated[index] = { ...updated[index], [field]: value };
        setIngredients(updated);
        setHasChanges(true);
    }

    function addIngredient() {
        setIngredients([...ingredients, { name: '', quantity: '' }]);
        setHasChanges(true);
    }

    function removeIngredient(index) {
        setIngredients(ingredients.filter((_, i) => i !== index));
        setHasChanges(true);
    }

    function addSuggestedIngredient(line) {
        // Parse the raw line to extract name and quantity
        const text = line.raw_text;
        // Simple heuristic: first number-like part is quantity, rest is name
        const match = text.match(/^([\d/.,]+\s*[a-zA-Z]*)\s+(.+)$/);
        if (match) {
            setIngredients([...ingredients, { name: match[2].trim(), quantity: match[1].trim() }]);
        } else {
            setIngredients([...ingredients, { name: text, quantity: '' }]);
        }
        setHasChanges(true);
    }

    async function handleSave() {
        if (!currentRecipe) return;

        setSaving(true);
        setSaveMessage(null);
        try {
            await patchRecipeIngredients(currentRecipe.id, ingredients);
            setHasChanges(false);
            setSaveMessage({ type: 'success', text: 'Saved!' });

            // Update the recipe in the local list
            const updated = [...recipes];
            updated[currentIndex] = { ...updated[currentIndex], ingredients: [...ingredients] };
            setRecipes(updated);
        } catch (error) {
            console.error('Failed to save:', error);
            setSaveMessage({ type: 'error', text: 'Failed to save' });
        } finally {
            setSaving(false);
        }
    }

    async function handleSaveAndNext() {
        await handleSave();
        if (currentIndex < recipes.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    }

    function handlePdfUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        setPdfFile(file);
        // Create a local URL for the uploaded file
        setPdfUrl(URL.createObjectURL(file));
    }

    async function handleExtractText() {
        if (!pdfFile && !currentRecipe?.source_file) return;

        setExtracting(true);
        try {
            const formData = new FormData();

            // If we have an uploaded file, use that; otherwise fetch from CDN
            if (pdfFile) {
                formData.append('file', pdfFile);
            } else if (currentRecipe?.source_file) {
                // Fetch the PDF from efarmz CDN and send for extraction
                const cdnUrl = getCdnPdfUrl(currentRecipe.source_file);
                const response = await fetch(cdnUrl);
                if (!response.ok) {
                    throw new Error(`Failed to fetch PDF from CDN: ${response.status}`);
                }
                const blob = await response.blob();
                formData.append('file', new File([blob], currentRecipe.source_file, { type: 'application/pdf' }));
            } else {
                alert('Please upload a PDF first');
                setExtracting(false);
                return;
            }

            const response = await extractPdfText(formData);
            setRawText(response.data.raw_text);
            setRawLines(response.data.raw_lines);
            setShowRawText(true);
        } catch (error) {
            console.error('Failed to extract text:', error);
            alert('Failed to extract text from PDF');
        } finally {
            setExtracting(false);
        }
    }

    function goToPrevious() {
        if (currentIndex > 0) {
            if (hasChanges && !confirm('You have unsaved changes. Discard?')) return;
            setCurrentIndex(currentIndex - 1);
        }
    }

    function goToNext() {
        if (currentIndex < recipes.length - 1) {
            if (hasChanges && !confirm('You have unsaved changes. Discard?')) return;
            setCurrentIndex(currentIndex + 1);
        }
    }

    return (
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <div className="card" style={{ marginBottom: '1rem' }}>
                <h2 style={{ marginBottom: '1rem' }}>Bulk Recipe Review</h2>

                {/* Filter */}
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span>Source File:</span>
                        <select
                            value={selectedSourceFile}
                            onChange={(e) => setSelectedSourceFile(e.target.value)}
                            style={{ padding: '0.5rem', minWidth: '200px' }}
                        >
                            <option value="">-- Select a PDF --</option>
                            {sourceFiles.map(f => (
                                <option key={f} value={f}>{f}</option>
                            ))}
                        </select>
                    </label>

                    {recipes.length > 0 && (
                        <span style={{ color: 'var(--text-secondary)' }}>
                            {recipes.length} recipe{recipes.length !== 1 ? 's' : ''} found
                        </span>
                    )}
                </div>
            </div>

            {loading && <p>Loading recipes...</p>}

            {!loading && recipes.length === 0 && selectedSourceFile && (
                <div className="card">
                    <p>No recipes found for this source file.</p>
                </div>
            )}

            {!loading && currentRecipe && (
                <>
                    {/* Navigation */}
                    <div className="card" style={{ marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <button
                                    onClick={goToPrevious}
                                    disabled={currentIndex === 0}
                                    className="btn-secondary"
                                >
                                    <ChevronLeft size={20} />
                                </button>
                                <span>
                                    Recipe <strong>{currentIndex + 1}</strong> of <strong>{recipes.length}</strong>
                                </span>
                                <button
                                    onClick={goToNext}
                                    disabled={currentIndex === recipes.length - 1}
                                    className="btn-secondary"
                                >
                                    <ChevronRight size={20} />
                                </button>
                            </div>

                            <h3 style={{ margin: 0, flex: 1, textAlign: 'center' }}>
                                {currentRecipe.name}
                            </h3>

                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                {saveMessage && (
                                    <span style={{
                                        color: saveMessage.type === 'success' ? 'var(--success)' : 'var(--error)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.25rem'
                                    }}>
                                        {saveMessage.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                                        {saveMessage.text}
                                    </span>
                                )}
                                <button
                                    onClick={handleSave}
                                    disabled={!hasChanges || saving}
                                    className="btn-secondary"
                                >
                                    <Save size={16} /> Save
                                </button>
                                <button
                                    onClick={handleSaveAndNext}
                                    disabled={saving}
                                    className="btn-primary"
                                >
                                    Save & Next
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Main content - side by side */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        {/* Left: PDF Source */}
                        <div className="card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <h4 style={{ margin: 0 }}>PDF Source</h4>
                                <label className="btn-secondary" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Upload size={16} />
                                    Upload PDF
                                    <input
                                        type="file"
                                        accept=".pdf"
                                        onChange={handlePdfUpload}
                                        style={{ display: 'none' }}
                                    />
                                </label>
                            </div>

                            <div style={{
                                padding: '1.5rem',
                                border: '1px solid var(--border)',
                                borderRadius: '8px',
                                background: 'var(--background)'
                            }}>
                                {pdfUrl ? (
                                    <div style={{ textAlign: 'center' }}>
                                        <FileText size={48} style={{ marginBottom: '1rem', opacity: 0.6 }} />
                                        <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                                            {currentRecipe?.source_file || 'Uploaded PDF'}
                                        </p>
                                        <a
                                            href={pdfUrl}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="btn-primary"
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '0.5rem',
                                                textDecoration: 'none'
                                            }}
                                        >
                                            <ExternalLink size={16} />
                                            Open PDF in New Tab
                                        </a>
                                    </div>
                                ) : (
                                    <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                                        <FileText size={48} style={{ marginBottom: '0.5rem', opacity: 0.5 }} />
                                        <p>No PDF available</p>
                                        <p style={{ fontSize: '0.875rem' }}>Upload a PDF to extract ingredients</p>
                                    </div>
                                )}
                            </div>

                            {/* Extract button */}
                            <div style={{ marginTop: '1rem' }}>
                                <button
                                    onClick={handleExtractText}
                                    disabled={extracting || (!pdfFile && !currentRecipe?.source_file)}
                                    className="btn-secondary"
                                    style={{ width: '100%' }}
                                >
                                    <Sparkles size={16} />
                                    {extracting ? 'Extracting...' : 'Re-extract Ingredients with AI'}
                                </button>
                            </div>

                            {/* Raw text panel */}
                            {rawLines.length > 0 && (
                                <div style={{ marginTop: '1rem' }}>
                                    <button
                                        onClick={() => setShowRawText(!showRawText)}
                                        className="btn-secondary"
                                        style={{ marginBottom: '0.5rem' }}
                                    >
                                        {showRawText ? 'Hide' : 'Show'} Raw Text ({rawLines.length} lines)
                                    </button>

                                    {showRawText && (
                                        <div style={{
                                            maxHeight: '200px',
                                            overflow: 'auto',
                                            background: 'var(--background)',
                                            padding: '0.5rem',
                                            borderRadius: '4px',
                                            fontSize: '0.75rem',
                                            fontFamily: 'monospace'
                                        }}>
                                            {rawText.split('\n').slice(0, 100).map((line, i) => (
                                                <div key={i} style={{ marginBottom: '0.25rem' }}>{line || '\u00A0'}</div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Right: Ingredients Editor */}
                        <div className="card">
                            <h4 style={{ marginBottom: '1rem' }}>
                                Ingredients ({ingredients.length})
                                {hasChanges && <span style={{ color: 'var(--warning)', marginLeft: '0.5rem' }}>*</span>}
                            </h4>

                            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                                {ingredients.map((ing, index) => (
                                    <div key={index} style={{
                                        display: 'flex',
                                        gap: '0.5rem',
                                        marginBottom: '0.5rem',
                                        alignItems: 'center'
                                    }}>
                                        <input
                                            type="text"
                                            value={ing.name}
                                            onChange={(e) => updateIngredient(index, 'name', e.target.value)}
                                            placeholder="Ingredient name"
                                            style={{ flex: 2 }}
                                        />
                                        <input
                                            type="text"
                                            value={ing.quantity}
                                            onChange={(e) => updateIngredient(index, 'quantity', e.target.value)}
                                            placeholder="Quantity"
                                            style={{ flex: 1 }}
                                        />
                                        <button
                                            onClick={() => removeIngredient(index)}
                                            className="btn-icon"
                                            style={{ color: 'var(--error)' }}
                                        >
                                            <X size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>

                            <button
                                onClick={addIngredient}
                                className="btn-secondary"
                                style={{ marginTop: '0.5rem', width: '100%' }}
                            >
                                <Plus size={16} /> Add Ingredient
                            </button>

                            {/* AI Suggestions */}
                            {rawLines.length > 0 && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <h4 style={{ marginBottom: '0.5rem' }}>
                                        AI Detected Lines ({rawLines.length})
                                    </h4>
                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                        Click + to add missing ingredients
                                    </p>
                                    <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                                        {rawLines.map((line, index) => (
                                            <div key={index} style={{
                                                display: 'flex',
                                                gap: '0.5rem',
                                                marginBottom: '0.25rem',
                                                alignItems: 'center',
                                                padding: '0.25rem',
                                                background: 'var(--background)',
                                                borderRadius: '4px',
                                                fontSize: '0.875rem'
                                            }}>
                                                <button
                                                    onClick={() => addSuggestedIngredient(line)}
                                                    className="btn-icon"
                                                    style={{ color: 'var(--success)' }}
                                                >
                                                    <Plus size={14} />
                                                </button>
                                                <span style={{ flex: 1 }}>{line.raw_text}</span>
                                                {line.serving_hint && (
                                                    <span style={{
                                                        fontSize: '0.75rem',
                                                        color: 'var(--text-secondary)',
                                                        background: 'var(--surface)',
                                                        padding: '0.125rem 0.375rem',
                                                        borderRadius: '4px'
                                                    }}>
                                                        {line.serving_hint}
                                                    </span>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export default BulkReview;
