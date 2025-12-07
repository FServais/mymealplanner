import React, { useState, useEffect } from 'react';
import { getIngredients, searchRecipesAI } from '../services/api';
import { Search, X, Loader, ChefHat, Eye, Sparkles } from 'lucide-react';
import RecipePreviewModal from './RecipePreviewModal';
import { Link } from 'react-router-dom';

const RecipeFinder = () => {
    const [allIngredients, setAllIngredients] = useState([]);
    const [selectedIngredients, setSelectedIngredients] = useState([]);
    const [ingredientInput, setIngredientInput] = useState('');
    const [showSuggestions, setShowSuggestions] = useState(false);

    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const [previewRecipe, setPreviewRecipe] = useState(null);

    useEffect(() => {
        fetchIngredients();
    }, []);

    const fetchIngredients = async () => {
        try {
            const response = await getIngredients();
            setAllIngredients(response.data.sort());
        } catch (error) {
            console.error("Error fetching ingredients", error);
        }
    };

    const addIngredient = (ing) => {
        if (!selectedIngredients.includes(ing)) {
            setSelectedIngredients([...selectedIngredients, ing]);
        }
        setIngredientInput('');
        setShowSuggestions(false);
    };

    const removeIngredient = (ing) => {
        setSelectedIngredients(selectedIngredients.filter(i => i !== ing));
    };

    const handleSearch = async () => {
        if (selectedIngredients.length === 0) return;

        setIsLoading(true);
        setHasSearched(true);
        try {
            const response = await searchRecipesAI(selectedIngredients);
            setSearchResults(response.data);
        } catch (error) {
            console.error("Error searching recipes", error);
            // Could add error state here
        } finally {
            setIsLoading(false);
        }
    };

    const filteredSuggestions = allIngredients.filter(ing =>
        ing.toLowerCase().includes(ingredientInput.toLowerCase()) &&
        !selectedIngredients.includes(ing)
    );

    return (
        <div className="container" style={{ maxWidth: '1000px' }}>
            <div className="header" style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                    <Sparkles style={{ color: 'var(--primary)' }} />
                    AI Recipe Finder
                </h1>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Tell us what ingredients you have, and our AI chef will find the best 5 recipes for you.
                </p>
            </div>

            <div className="card" style={{ marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>Your Ingredients</h3>

                <div style={{ position: 'relative', marginBottom: '1rem' }}>
                    <input
                        type="text"
                        placeholder="Type an ingredient (e.g. 'chicken', 'tomato')..."
                        className="input"
                        value={ingredientInput}
                        onChange={(e) => {
                            setIngredientInput(e.target.value);
                            setShowSuggestions(true);
                        }}
                        onFocus={() => setShowSuggestions(true)}
                        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && ingredientInput) {
                                e.preventDefault();
                                // If exact match in suggestions, add it, otherwise just add typed value?
                                // Let's prefer suggestions but fallback to custom
                                addIngredient(ingredientInput);
                            }
                        }}
                        style={{ width: '100%', paddingLeft: '2.5rem' }}
                    />
                    <Search size={18} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />

                    {showSuggestions && ingredientInput && (
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
                            {filteredSuggestions.map(ing => (
                                <div
                                    key={ing}
                                    onClick={() => addIngredient(ing)}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        cursor: 'pointer',
                                        borderBottom: '1px solid var(--border)'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--background)'}
                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                                >
                                    {ing}
                                </div>
                            ))}
                            {filteredSuggestions.length === 0 && (
                                <div style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>
                                    Press Enter to add "{ingredientInput}"
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', minHeight: '40px' }}>
                    {selectedIngredients.map(ing => (
                        <span key={ing} className="tag" style={{
                            fontSize: '1rem',
                            padding: '0.5rem 1rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}>
                            {ing}
                            <button
                                onClick={() => removeIngredient(ing)}
                                style={{ border: 'none', background: 'none', padding: 0, cursor: 'pointer', color: 'inherit', display: 'flex' }}
                            >
                                <X size={16} />
                            </button>
                        </span>
                    ))}
                    {selectedIngredients.length === 0 && (
                        <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic', padding: '0.5rem 0' }}>
                            No ingredients selected yet.
                        </span>
                    )}
                </div>

                <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                    <button
                        className="btn btn-primary"
                        onClick={handleSearch}
                        disabled={selectedIngredients.length === 0 || isLoading}
                        style={{ padding: '0.75rem 2rem', fontSize: '1.1rem' }}
                    >
                        {isLoading ? (
                            <>
                                <Loader className="spin" size={20} /> Searching...
                            </>
                        ) : (
                            <>
                                <Sparkles size={20} /> Find Best Recipes
                            </>
                        )}
                    </button>
                </div>
            </div>

            {hasSearched && (
                <div>
                    <h2 style={{ marginBottom: '1.5rem' }}>
                        {searchResults.length > 0
                            ? `Found ${searchResults.length} Perfect Matches`
                            : 'No matching recipes found.'}
                    </h2>

                    <div className="grid">
                        {searchResults.map(recipe => (
                            <div key={recipe.id} className="card">
                                {/* Simple Logic for matching ingredients count could go here if we had full lists, 
                                    but backend handles selection logic. */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                    <h3 style={{ marginTop: 0, fontSize: '1.25rem' }}>{recipe.name}</h3>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                    {recipe.description || 'No description available.'}
                                </p>

                                {recipe.tags && recipe.tags.length > 0 && (
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                                        {recipe.tags.slice(0, 3).map(tag => (
                                            <span key={tag.name} className="tag" style={{
                                                backgroundColor: (tag.color || '#6366f1') + '1A',
                                                color: tag.color || '#6366f1',
                                                fontSize: '0.8rem'
                                            }}>
                                                {tag.name}
                                            </span>
                                        ))}
                                    </div>
                                )}

                                <div style={{ marginTop: 'auto', display: 'flex', gap: '0.5rem' }}>
                                    <button
                                        onClick={() => setPreviewRecipe(recipe)}
                                        className="btn btn-outline"
                                        style={{ flex: 1, justifyContent: 'center' }}
                                    >
                                        <Eye size={18} /> Quick Look
                                    </button>
                                    <Link to={`/edit/${recipe.id}`} className="btn btn-outline" style={{ justifyContent: 'center' }}>
                                        Edit
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {previewRecipe && (
                <RecipePreviewModal
                    recipe={previewRecipe}
                    onClose={() => setPreviewRecipe(null)}
                />
            )}
        </div>
    );
};

export default RecipeFinder;
