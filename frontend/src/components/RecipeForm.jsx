import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createRecipe, getRecipe, updateRecipe } from '../services/api';
import { Save, Plus, X } from 'lucide-react';

const RecipeForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [recipe, setRecipe] = useState({
        name: '',
        description: '',
        ingredients: [],
        instructions: []
    });

    useEffect(() => {
        if (id) {
            loadRecipe();
        }
    }, [id]);

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
            </form>
        </div>
    );
};

export default RecipeForm;
