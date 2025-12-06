import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createRecipe, getRecipe, updateRecipe, getTags } from '../services/api';
import { Save, Plus, X } from 'lucide-react';

const RecipeForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [recipe, setRecipe] = useState({
        name: '',
        description: '',
        ingredients: [],
        instructions: [],
        tags: []
    });

    const [availableTags, setAvailableTags] = useState([]);
    const [showTagSuggestions, setShowTagSuggestions] = useState(false);
    const [tagInput, setTagInput] = useState('');
    const [tagColor, setTagColor] = useState('#6366f1');

    const PRESET_COLORS = [
        '#ef4444', // Red
        '#f97316', // Orange
        '#f59e0b', // Amber
        '#84cc16', // Lime
        '#22c55e', // Green
        '#10b981', // Emerald
        '#06b6d4', // Cyan
        '#3b82f6', // Blue
        '#6366f1', // Indigo (Default)
        '#8b5cf6', // Violet
        '#d946ef', // Fuchsia
        '#ec4899', // Pink
    ];

    useEffect(() => {
        fetchTags();
        if (id) {
            loadRecipe();
        }
    }, [id]);

    const fetchTags = async () => {
        try {
            const response = await getTags();
            setAvailableTags(response.data);
        } catch (error) {
            console.error("Error fetching tags", error);
        }
    };

    const loadRecipe = async () => {
        const response = await getRecipe(id);
        setRecipe(response.data);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (id) {
                await updateRecipe(id, recipe);
            } else {
                await createRecipe(recipe);
            }
            navigate('/');
        } catch (error) {
            console.error("Error saving recipe", error);
        }
    };

    const addIngredient = () => {
        setRecipe({
            ...recipe,
            ingredients: [...recipe.ingredients, { name: '', quantity: '' }]
        });
    };

    const updateIngredient = (index, field, value) => {
        const newIngredients = [...recipe.ingredients];
        newIngredients[index][field] = value;
        setRecipe({ ...recipe, ingredients: newIngredients });
    };

    const removeIngredient = (index) => {
        const newIngredients = recipe.ingredients.filter((_, i) => i !== index);
        setRecipe({ ...recipe, ingredients: newIngredients });
    };

    const addInstruction = () => {
        setRecipe({
            ...recipe,
            instructions: [...recipe.instructions, { step_number: recipe.instructions.length + 1, text: '' }]
        });
    };

    const updateInstruction = (index, value) => {
        const newInstructions = [...recipe.instructions];
        newInstructions[index].text = value;
        setRecipe({ ...recipe, instructions: newInstructions });
    };

    const removeInstruction = (index) => {
        const newInstructions = recipe.instructions.filter((_, i) => i !== index);
        // Re-index steps
        newInstructions.forEach((inst, i) => inst.step_number = i + 1);
        setRecipe({ ...recipe, instructions: newInstructions });
    };

    return (
        <div className="container" style={{ maxWidth: '800px' }}>
            <div className="header">
                <h1>{id ? 'Edit Recipe' : 'New Recipe'}</h1>
            </div>
            <form onSubmit={handleSubmit}>
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Name</label>
                        <input
                            className="input"
                            value={recipe.name}
                            onChange={(e) => setRecipe({ ...recipe, name: e.target.value })}
                            required
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Description</label>
                        <textarea
                            className="input"
                            value={recipe.description}
                            onChange={(e) => setRecipe({ ...recipe, description: e.target.value })}
                            rows={3}
                        />
                    </div>
                </div>

                <div className="card" style={{ marginBottom: '2rem' }}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Tags</label>

                        <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                            {PRESET_COLORS.map(color => (
                                <button
                                    key={color}
                                    type="button"
                                    onClick={() => setTagColor(color)}
                                    style={{
                                        width: '24px',
                                        height: '24px',
                                        borderRadius: '50%',
                                        backgroundColor: color,
                                        border: tagColor === color ? '2px solid white' : '2px solid transparent',
                                        boxShadow: tagColor === color ? `0 0 0 2px ${color}` : 'none',
                                        cursor: 'pointer',
                                        transition: 'all 0.2s'
                                    }}
                                    title={color}
                                />
                            ))}
                        </div>

                        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', position: 'relative' }}>
                            {/* Hidden color input to maintain state compatibility if needed, but primarily using presets now */}
                            <div style={{ flex: 1, position: 'relative' }}>
                                <input
                                    className="input"
                                    placeholder="Add a tag..."
                                    value={tagInput}
                                    onChange={(e) => {
                                        setTagInput(e.target.value);
                                        setShowTagSuggestions(true);
                                    }}
                                    onFocus={() => setShowTagSuggestions(true)}
                                    // Delay hiding to allow click event on suggestion
                                    onBlur={() => setTimeout(() => setShowTagSuggestions(false), 200)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            e.preventDefault();
                                            const val = tagInput.trim();
                                            if (val && !recipe.tags.some(t => (t.name || t) === val)) {
                                                const newTag = { name: val, color: tagColor };
                                                setRecipe({ ...recipe, tags: [...(recipe.tags || []), newTag] });
                                                setTagInput('');
                                                setShowTagSuggestions(false);
                                            }
                                        }
                                    }}
                                    style={{ width: '100%' }}
                                />
                                {showTagSuggestions && tagInput && (
                                    <div style={{
                                        position: 'absolute',
                                        top: '100%',
                                        left: 0,
                                        right: 0,
                                        backgroundColor: 'var(--surface)',
                                        border: '1px solid var(--border)',
                                        borderRadius: '0 0 var(--radius) var(--radius)',
                                        zIndex: 10,
                                        maxHeight: '200px',
                                        overflowY: 'auto',
                                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                    }}>
                                        {availableTags
                                            .filter(t => t.name.toLowerCase().includes(tagInput.toLowerCase()) && !recipe.tags.some(rt => (rt.name || rt) === t.name))
                                            .map(tag => (
                                                <div
                                                    key={tag.id}
                                                    onClick={() => {
                                                        setRecipe({ ...recipe, tags: [...(recipe.tags || []), tag] });
                                                        setTagInput('');
                                                        setShowTagSuggestions(false);
                                                    }}
                                                    style={{
                                                        padding: '0.5rem',
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '0.5rem',
                                                        borderBottom: '1px solid var(--border)'
                                                    }}
                                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--background)'}
                                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                                                >
                                                    <span style={{
                                                        width: '12px',
                                                        height: '12px',
                                                        borderRadius: '50%',
                                                        backgroundColor: tag.color
                                                    }}></span>
                                                    {tag.name}
                                                </div>
                                            ))}
                                    </div>
                                )}
                            </div>
                            <button type="button" className="btn btn-outline"
                                onClick={() => {
                                    const val = tagInput.trim();
                                    if (val && !recipe.tags.some(t => (t.name || t) === val)) {
                                        const newTag = { name: val, color: tagColor };
                                        setRecipe({ ...recipe, tags: [...(recipe.tags || []), newTag] });
                                        setTagInput('');
                                    }
                                }}
                            >
                                <Plus size={16} />
                            </button>
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                            {(recipe.tags || []).map((tag, index) => {
                                const tagName = tag.name || tag;
                                const tagClr = tag.color || '#6366f1';
                                return (
                                    <span key={index} className="tag" style={{
                                        backgroundColor: tagClr + '1A',
                                        color: tagClr,
                                        borderColor: tagClr + '33'
                                    }}>
                                        {tagName}
                                        <button
                                            type="button"
                                            onClick={() => {
                                                const newTags = recipe.tags.filter((_, i) => i !== index);
                                                setRecipe({ ...recipe, tags: newTags });
                                            }}
                                            style={{ border: 'none', background: 'none', padding: 0, cursor: 'pointer', color: 'inherit', marginLeft: '0.5rem', display: 'flex' }}
                                        >
                                            <X size={14} />
                                        </button>
                                    </span>
                                )
                            })}
                        </div>
                    </div>
                </div>

                <div className="card" style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <h3>Ingredients</h3>
                        <button type="button" onClick={addIngredient} className="btn btn-outline">
                            <Plus size={16} /> Add
                        </button>
                    </div>
                    {recipe.ingredients.map((ing, index) => (
                        <div key={index} style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
                            <input
                                className="input"
                                placeholder="Name"
                                value={ing.name}
                                onChange={(e) => updateIngredient(index, 'name', e.target.value)}
                                required
                            />
                            <input
                                className="input"
                                placeholder="Quantity"
                                value={ing.quantity}
                                onChange={(e) => updateIngredient(index, 'quantity', e.target.value)}
                                required
                            />
                            <button type="button" onClick={() => removeIngredient(index)} style={{ color: 'var(--danger)' }}>
                                <X size={20} />
                            </button>
                        </div>
                    ))}
                </div>

                <div className="card" style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <h3>Instructions</h3>
                        <button type="button" onClick={addInstruction} className="btn btn-outline">
                            <Plus size={16} /> Add
                        </button>
                    </div>
                    {recipe.instructions.map((inst, index) => (
                        <div key={index} style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
                            <span style={{ paddingTop: '0.75rem', fontWeight: 'bold', color: 'var(--text-secondary)' }}>
                                {inst.step_number}.
                            </span>
                            <textarea
                                className="input"
                                value={inst.text}
                                onChange={(e) => updateInstruction(index, e.target.value)}
                                required
                                rows={2}
                            />
                            <button type="button" onClick={() => removeInstruction(index)} style={{ color: 'var(--danger)' }}>
                                <X size={20} />
                            </button>
                        </div>
                    ))}
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                    <Save size={20} /> Save Recipe
                </button>
            </form >
        </div >
    );
};

export default RecipeForm;
