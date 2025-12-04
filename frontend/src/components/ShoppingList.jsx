import React, { useState, useEffect } from 'react';
import { generateShoppingList, createMealPlan } from '../services/api';
import { ShoppingCart, Save, ChefHat } from 'lucide-react';

const ShoppingList = ({ recipes = [] }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    // Derive recipeIds from recipes
    const recipeIds = recipes.map(r => r.id);

    useEffect(() => {
        if (recipeIds.length > 0) {
            fetchShoppingList();
        } else {
            setItems([]);
        }
    }, [recipeIds.join(',')]);

    const fetchShoppingList = async () => {
        setLoading(true);
        try {
            const response = await generateShoppingList(recipeIds);
            setItems(response.data);
        } catch (error) {
            console.error("Error generating shopping list", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSavePlan = async () => {
        const name = prompt("Enter a name for this meal plan:");
        if (!name) return;

        try {
            await createMealPlan({ name, recipe_ids: recipeIds });
            alert("Meal plan saved successfully!");
        } catch (error) {
            console.error("Error saving meal plan", error);
            alert("Failed to save meal plan.");
        }
    };

    if (recipes.length === 0) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                <ShoppingCart size={32} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <p>Select recipes to generate a shopping list.</p>
            </div>
        );
    }

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.5rem' }}>Shopping List</h2>
                <span className="badge" style={{ backgroundColor: 'var(--primary)', color: 'white' }}>
                    {items.length} items
                </span>
            </div>

            {/* Selected Recipes Section */}
            <div style={{ marginBottom: '1.5rem', padding: '0.75rem', backgroundColor: 'var(--background)', borderRadius: 'var(--radius)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <ChefHat size={16} />
                    <span>{recipes.length} {recipes.length === 1 ? 'recipe' : 'recipes'} selected</span>
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {recipes.map((recipe) => (
                        <li key={recipe.id} style={{ fontSize: '0.9rem', padding: '0.25rem 0', color: 'var(--text)' }}>
                            • {recipe.name}
                        </li>
                    ))}
                </ul>
            </div>

            {loading ? (
                <p>Loading...</p>
            ) : (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {items.map((item, index) => (
                        <li key={index} style={{
                            padding: '0.75rem 0',
                            borderBottom: '1px solid var(--border)',
                            display: 'flex',
                            justifyContent: 'space-between'
                        }}>
                            <span>{item.name}</span>
                            <strong style={{ color: 'var(--primary)' }}>{item.quantity}</strong>
                        </li>
                    ))}
                </ul>
            )}

            <div style={{ marginTop: '2rem' }}>
                <button onClick={handleSavePlan} className="btn btn-outline" style={{ width: '100%', justifyContent: 'center' }}>
                    <Save size={18} /> Save Meal Plan
                </button>
            </div>
        </div>
    );
};

export default ShoppingList;

