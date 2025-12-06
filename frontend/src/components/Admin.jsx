import React, { useState } from 'react';
import { suggestDuplicates, mergeIngredients, getIngredients, getTags, createTag, updateTag, deleteTag } from '../services/api';
import { Wand2, ArrowRight, Check, Loader2, Tag, Plus, Pencil, Trash2, X } from 'lucide-react';

const Admin = () => {
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    const handleFindDuplicates = async () => {
        setLoading(true);
        setMessage(null);
        try {
            const response = await suggestDuplicates();
            // Add a unique ID to each group to use as a key
            const suggestionsWithIds = response.data.suggestions.map((s, i) => ({
                ...s,
                id: `group-${i}-${Date.now()}`
            }));
            setSuggestions(suggestionsWithIds);
            if (response.data.suggestions.length === 0) {
                setMessage({ type: 'info', text: 'No duplicates found by AI.' });
            }
        } catch (error) {
            console.error("Error finding duplicates", error);
            setMessage({ type: 'error', text: 'Failed to fetch suggestions.' });
        } finally {
            setLoading(false);
        }
    };

    const handleMerge = async (group) => {
        try {
            // Filter out sources that are not selected (if we implemented selection, but for now assume all sources in the group)
            // The UI allows editing the target name, so we should take the current value from the state/input.
            // Since we are iterating, we might need to track state for each group if we want them editable.
            // For simplicity v1: We trust the AI's grouping or allow simple edits.

            // Let's assume the user accepts the group as is for now, or we can make it editable.
            // To make it editable, we'd need to map suggestions to a local state.

            await mergeIngredients({
                target_name: group.target,
                source_names: group.sources
            });

            setMessage({ type: 'success', text: `Merged ${group.sources.length} ingredients into "${group.target}"` });

            // Remove the merged group from the list by ID
            setSuggestions(prev => prev.filter(g => g.id !== group.id));

        } catch (error) {
            console.error("Error merging ingredients", error);
            setMessage({ type: 'error', text: 'Failed to merge ingredients.' });
        }
    };

    const [allIngredients, setAllIngredients] = useState([]);
    const [selectedIngredients, setSelectedIngredients] = useState([]);
    const [manualTargetName, setManualTargetName] = useState('');
    const [loadingIngredients, setLoadingIngredients] = useState(false);
    const [ingredientSearch, setIngredientSearch] = useState('');

    // Tag Management State
    const [tags, setTags] = useState([]);
    const [loadingTags, setLoadingTags] = useState(false);
    const [editingTag, setEditingTag] = useState(null); // null = create mode, object = edit mode
    const [tagForm, setTagForm] = useState({ name: '', color: '#6366f1' });
    const [showTagModal, setShowTagModal] = useState(false);

    const PRESET_COLORS = [
        '#ef4444', '#f97316', '#f59e0b', '#84cc16',
        '#22c55e', '#10b981', '#06b6d4', '#3b82f6',
        '#6366f1', '#8b5cf6', '#d946ef', '#ec4899'
    ];

    React.useEffect(() => {
        fetchIngredients();
        fetchTags();
    }, []);

    const fetchTags = async () => {
        setLoadingTags(true);
        try {
            const response = await getTags();
            setTags(response.data.sort((a, b) => a.name.localeCompare(b.name)));
        } catch (error) {
            console.error("Error fetching tags", error);
        } finally {
            setLoadingTags(false);
        }
    };

    const handleSaveTag = async () => {
        try {
            if (editingTag) {
                await updateTag(editingTag.id, tagForm);
                setMessage({ type: 'success', text: 'Tag updated successfully.' });
            } else {
                await createTag(tagForm);
                setMessage({ type: 'success', text: 'Tag created successfully.' });
            }
            setShowTagModal(false);
            setTagForm({ name: '', color: '#6366f1' });
            setEditingTag(null);
            fetchTags();
        } catch (error) {
            console.error("Error saving tag", error);
            setMessage({ type: 'error', text: 'Failed to save tag.' });
        }
    };

    const handleDeleteTag = async (id) => {
        if (!window.confirm("Are you sure? This will remove the tag from all recipes that use it.")) return;
        try {
            await deleteTag(id);
            setMessage({ type: 'success', text: 'Tag deleted successfully.' });
            fetchTags();
        } catch (error) {
            console.error("Error deleting tag", error);
            setMessage({ type: 'error', text: 'Failed to delete tag.' });
        }
    };

    const openCreateTag = () => {
        setTagForm({ name: '', color: '#6366f1' });
        setEditingTag(null);
        setShowTagModal(true);
    };

    const openEditTag = (tag) => {
        setTagForm({ name: tag.name, color: tag.color || '#6366f1' });
        setEditingTag(tag);
        setShowTagModal(true);
    };

    const fetchIngredients = async () => {
        setLoadingIngredients(true);
        try {
            const response = await getIngredients();
            setAllIngredients(response.data.sort());
        } catch (error) {
            console.error("Error fetching ingredients", error);
        } finally {
            setLoadingIngredients(false);
        }
    };

    const handleManualMerge = async () => {
        if (!manualTargetName || selectedIngredients.length === 0) {
            setMessage({ type: 'error', text: 'Please select ingredients and specify a target name.' });
            return;
        }

        try {
            await mergeIngredients({
                target_name: manualTargetName,
                source_names: selectedIngredients
            });

            setMessage({ type: 'success', text: `Merged ${selectedIngredients.length} ingredients into "${manualTargetName}"` });

            // Reset manual merge state
            setSelectedIngredients([]);
            setManualTargetName('');
            // Refresh ingredient list
            fetchIngredients();

        } catch (error) {
            console.error("Error merging ingredients", error);
            setMessage({ type: 'error', text: 'Failed to merge ingredients.' });
        }
    };

    const toggleIngredientSelection = (ing) => {
        if (selectedIngredients.includes(ing)) {
            setSelectedIngredients(prev => prev.filter(i => i !== ing));
        } else {
            setSelectedIngredients(prev => [...prev, ing]);
            // Auto-fill target name with first selection if empty
            if (!manualTargetName) {
                setManualTargetName(ing);
            }
        }
    };

    return (
        <div className="container">
            <div className="header">
                <h1>Admin Tools</h1>
            </div>

            {/* Tag Management Section */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <div>
                        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Tag size={24} color="var(--primary)" />
                            Tag Management
                        </h2>
                        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                            Create, update, or delete tags. Changes reflect on all recipes.
                        </p>
                    </div>
                    <button className="btn btn-primary" onClick={openCreateTag}>
                        <Plus size={18} /> New Tag
                    </button>
                </div>

                {loadingTags ? (
                    <div>Loading tags...</div>
                ) : (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                        {tags.map(tag => (
                            <div key={tag.id} className="tag"
                                style={{
                                    paddingRight: '0.5rem',
                                    backgroundColor: (tag.color || '#6366f1') + '1A',
                                    color: tag.color || '#6366f1',
                                    borderColor: (tag.color || '#6366f1') + '33',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem'
                                }}>
                                <span>{tag.name}</span>
                                <div style={{ display: 'flex', gap: '0.25rem' }}>
                                    <button onClick={() => openEditTag(tag)} style={{ padding: '0.25rem', color: 'inherit', cursor: 'pointer' }}>
                                        <Pencil size={14} />
                                    </button>
                                    <button onClick={() => handleDeleteTag(tag.id)} style={{ padding: '0.25rem', color: 'inherit', cursor: 'pointer' }}>
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            </div>
                        ))}
                        {tags.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No tags found.</p>}
                    </div>
                )}
            </div>

            {/* Tag Modal */}
            {showTagModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
                }}>
                    <div className="card" style={{ width: '400px', maxWidth: '90%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3>{editingTag ? 'Edit Tag' : 'New Tag'}</h3>
                            <button onClick={() => setShowTagModal(false)}><X size={20} /></button>
                        </div>
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Name</label>
                            <input
                                className="input"
                                value={tagForm.name}
                                onChange={e => setTagForm({ ...tagForm, name: e.target.value })}
                                autoFocus
                            />
                        </div>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Color</label>
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                {PRESET_COLORS.map(c => (
                                    <button
                                        key={c}
                                        type="button"
                                        onClick={() => setTagForm({ ...tagForm, color: c })}
                                        style={{
                                            width: '24px', height: '24px', borderRadius: '50%', backgroundColor: c,
                                            border: tagForm.color === c ? '2px solid white' : '2px solid transparent',
                                            boxShadow: tagForm.color === c ? `0 0 0 2px ${c}` : 'none',
                                            cursor: 'pointer'
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                            <button className="btn btn-outline" onClick={() => setShowTagModal(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSaveTag} disabled={!tagForm.name}>Save</button>
                        </div>
                    </div>
                </div>
            )}

            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <div>
                        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Wand2 size={24} color="var(--primary)" />
                            AI Duplicate Finder
                        </h2>
                        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                            Use AI to find and merge duplicate ingredients (e.g., "Tomato" vs "Tomates").
                        </p>
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={handleFindDuplicates}
                        disabled={loading}
                    >
                        {loading ? <><Loader2 className="spin" size={20} /> Analyzing...</> : 'Find Duplicates (AI)'}
                    </button>
                </div>

                {message && (
                    <div style={{
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        marginBottom: '1rem',
                        backgroundColor: message.type === 'error' ? '#fee2e2' : message.type === 'success' ? '#dcfce7' : '#e0f2fe',
                        color: message.type === 'error' ? '#991b1b' : message.type === 'success' ? '#166534' : '#075985'
                    }}>
                        {message.text}
                    </div>
                )}

                {suggestions.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {suggestions.map((group) => (
                            <div key={group.id} style={{
                                border: '1px solid var(--border)',
                                borderRadius: '0.5rem',
                                padding: '1rem',
                                backgroundColor: 'var(--background)'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                                    <div style={{ flex: 1 }}>
                                        <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>
                                            Merge these variations:
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                            {group.sources.map((source, idx) => (
                                                <span key={idx} className="badge" style={{ backgroundColor: 'var(--surface)', border: '1px solid var(--border)' }}>
                                                    {source}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    <ArrowRight size={20} style={{ color: 'var(--text-secondary)' }} />

                                    <div style={{ flex: 1 }}>
                                        <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>
                                            Into this canonical name:
                                        </label>
                                        <input
                                            className="input"
                                            defaultValue={group.target}
                                            onChange={(e) => {
                                                group.target = e.target.value;
                                            }}
                                            style={{ width: '100%' }}
                                        />
                                    </div>

                                    <button
                                        className="btn btn-primary"
                                        onClick={() => handleMerge(group)}
                                    >
                                        <Check size={18} /> Merge
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="card">
                <h2 style={{ margin: '0 0 1rem 0' }}>Manual Merge</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    Select ingredients from the list below to merge them manually.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                            1. Select Ingredients to Merge ({selectedIngredients.length})
                        </label>
                        <div style={{
                            height: '300px',
                            overflowY: 'auto',
                            border: '1px solid var(--border)',
                            borderRadius: '0.5rem',
                            padding: '0.5rem'
                        }}>
                            <input
                                type="text"
                                className="input"
                                placeholder="Search ingredients..."
                                value={ingredientSearch}
                                onChange={(e) => setIngredientSearch(e.target.value)}
                                style={{ marginBottom: '0.5rem', width: '100%' }}
                            />
                            {loadingIngredients ? (
                                <div style={{ padding: '1rem', textAlign: 'center' }}>Loading ingredients...</div>
                            ) : (
                                allIngredients
                                    .filter(ing => ing.toLowerCase().includes(ingredientSearch.toLowerCase()))
                                    .map((ing, idx) => (
                                        <div
                                            key={idx}
                                            onClick={() => toggleIngredientSelection(ing)}
                                            style={{
                                                padding: '0.5rem',
                                                cursor: 'pointer',
                                                backgroundColor: selectedIngredients.includes(ing) ? 'var(--primary-light)' : 'transparent',
                                                borderRadius: '0.25rem',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '0.5rem'
                                            }}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedIngredients.includes(ing)}
                                                readOnly
                                                style={{ pointerEvents: 'none' }}
                                            />
                                            {ing}
                                        </div>
                                    ))
                            )}
                        </div>
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                            2. Target Name
                        </label>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                            <div style={{ flex: 1 }}>
                                <input
                                    className="input"
                                    value={manualTargetName}
                                    onChange={(e) => setManualTargetName(e.target.value)}
                                    placeholder="e.g. Tomato"
                                    style={{ width: '100%' }}
                                />
                                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                                    All selected ingredients will be renamed to this.
                                </p>
                            </div>
                            <button
                                className="btn btn-primary"
                                onClick={handleManualMerge}
                                disabled={selectedIngredients.length === 0 || !manualTargetName}
                            >
                                Merge Selected
                            </button>
                        </div>

                        {selectedIngredients.length > 0 && (
                            <div style={{ marginTop: '1rem' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>
                                    Selected:
                                </label>
                                <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                                    {selectedIngredients.map((ing, idx) => (
                                        <span key={idx} className="badge" style={{ fontSize: '0.8rem' }}>
                                            {ing}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Admin;
