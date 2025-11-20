import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRecipes, deleteRecipe, getIngredients, getRecipeCount } from '../services/api';
import { Plus, Trash2, ChefHat, Filter, X, Search, ChevronDown, Eye } from 'lucide-react';
import RecipePreviewModal from './RecipePreviewModal';

const RecipeList = ({ onAddToPlan }) => {
    const [recipes, setRecipes] = useState([]);
    const [selectedRecipes, setSelectedRecipes] = useState(new Set());
    const [allIngredients, setAllIngredients] = useState([]);
    const [selectedIngredients, setSelectedIngredients] = useState([]);
    const [showFilter, setShowFilter] = useState(false);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [previewRecipe, setPreviewRecipe] = useState(null);
    const LIMIT = 12;

    useEffect(() => {
        fetchIngredients();
    }, []);

    useEffect(() => {
        // Reset list when filters change
        setPage(0);
        setRecipes([]);
        setHasMore(true);
        fetchRecipes(0, true);
        fetchCount();
    }, [selectedIngredients, search]);

    const fetchIngredients = async () => {
        try {
            const response = await getIngredients();
            setAllIngredients(response.data.sort());
        } catch (error) {
            console.error("Error fetching ingredients", error);
        }
    };

    const fetchCount = async () => {
        try {
            const params = {};
            if (selectedIngredients.length > 0) {
                params.ingredients = selectedIngredients;
            }
            if (search) {
                params.search = search;
            }
            const response = await getRecipeCount(params);
            setTotalCount(response.data.count);
        } catch (error) {
            console.error("Error fetching recipe count", error);
        }
    };

    const fetchRecipes = async (pageNum = page, isNewFilter = false) => {
        try {
            const params = {
                skip: pageNum * LIMIT,
                limit: LIMIT
            };
            if (selectedIngredients.length > 0) {
                params.ingredients = selectedIngredients;
            }
            if (search) {
                params.search = search;
            }

            const response = await getRecipes(params);
            const newRecipes = response.data;

            if (newRecipes.length < LIMIT) {
                setHasMore(false);
            }

            if (isNewFilter) {
                setRecipes(newRecipes);
            } else {
                setRecipes(prev => [...prev, ...newRecipes]);
            }
        } catch (error) {
            console.error("Error fetching recipes", error);
        }
    };

    const loadMore = () => {
        const nextPage = page + 1;
        setPage(nextPage);
        fetchRecipes(nextPage, false);
    };

    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to delete this recipe?")) {
            await deleteRecipe(id);
            // Refresh current view
            setPage(0);
            setHasMore(true);
            fetchRecipes(0, true);
        }
    };

    const toggleSelection = (id) => {
        const newSelection = new Set(selectedRecipes);
        if (newSelection.has(id)) {
            newSelection.delete(id);
        } else {
            newSelection.add(id);
        }
        setSelectedRecipes(newSelection);
        onAddToPlan(Array.from(newSelection));
    };

    const toggleIngredientFilter = (ingredient) => {
        if (selectedIngredients.includes(ingredient)) {
            setSelectedIngredients(selectedIngredients.filter(i => i !== ingredient));
        } else {
            setSelectedIngredients([...selectedIngredients, ingredient]);
        }
    };

    return (
        <div>
            <div className="header">
                <div>
                    <h1 style={{ marginBottom: '0.25rem' }}>My Recipes</h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                        {totalCount} {totalCount === 1 ? 'recipe' : 'recipes'} total
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div style={{ position: 'relative' }}>
                        <input
                            type="text"
                            placeholder="Search recipes..."
                            className="input"
                            style={{ paddingLeft: '2.5rem', width: '200px' }}
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                        <Search size={18} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                    </div>
                    <button
                        className={`btn ${showFilter ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setShowFilter(!showFilter)}
                    >
                        <Filter size={20} /> Filter
                    </button>
                    <Link to="/create" className="btn btn-primary">
                        <Plus size={20} /> New Recipe
                    </Link>
                </div>
            </div>

            {showFilter && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h3 style={{ margin: 0 }}>Filter by Ingredients</h3>
                        {selectedIngredients.length > 0 && (
                            <button
                                onClick={() => setSelectedIngredients([])}
                                style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textDecoration: 'underline' }}
                            >
                                Clear all
                            </button>
                        )}
                    </div>

                    <div style={{ marginBottom: '1rem', position: 'relative' }}>
                        <input
                            type="text"
                            placeholder="Search ingredients..."
                            className="input"
                            style={{ width: '100%', paddingLeft: '2.2rem' }}
                            onChange={(e) => {
                                const term = e.target.value.toLowerCase();
                                const allBadges = document.querySelectorAll('.ingredient-badge');
                                allBadges.forEach(badge => {
                                    const name = badge.getAttribute('data-name').toLowerCase();
                                    if (name.includes(term)) {
                                        badge.style.display = 'inline-flex';
                                    } else {
                                        badge.style.display = 'none';
                                    }
                                });
                            }}
                        />
                        <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                        {allIngredients.map((ing) => (
                            <button
                                key={ing}
                                data-name={ing}
                                className="badge ingredient-badge"
                                onClick={() => toggleIngredientFilter(ing)}
                                style={{
                                    cursor: 'pointer',
                                    border: '1px solid var(--primary)',
                                    backgroundColor: selectedIngredients.includes(ing) ? 'var(--primary)' : 'transparent',
                                    color: selectedIngredients.includes(ing) ? 'white' : 'var(--primary)',
                                    fontSize: '0.9rem',
                                    padding: '0.4rem 0.8rem',
                                    display: 'inline-flex'
                                }}
                            >
                                {ing}
                            </button>
                        ))}
                        {allIngredients.length === 0 && (
                            <span style={{ color: 'var(--text-secondary)' }}>No ingredients found to filter by.</span>
                        )}
                    </div>
                </div>
            )}

            <div className="grid">
                {recipes.map((recipe) => {
                    // Generate thumbnail URL from source_file
                    const getThumbnailUrl = (sourceFile) => {
                        if (!sourceFile) return null;
                        // Remove .pdf extension
                        const fileNameWithoutExt = sourceFile.replace('.pdf', '');
                        // Use local backend endpoint
                        return `http://localhost:8000/images/thumbnails/${fileNameWithoutExt}.jpg`;
                    };

                    const thumbnailUrl = getThumbnailUrl(recipe.source_file);

                    return (
                        <div key={recipe.id} className="card">
                            {thumbnailUrl && (
                                <div style={{
                                    width: '100%',
                                    height: '200px',
                                    overflow: 'hidden',
                                    borderRadius: '0.5rem',
                                    marginBottom: '1rem',
                                    backgroundColor: 'var(--surface)'
                                }}>
                                    <img
                                        src={thumbnailUrl}
                                        alt={recipe.name}
                                        style={{
                                            width: '100%',
                                            height: '100%',
                                            objectFit: 'cover'
                                        }}
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                        }}
                                    />
                                </div>
                            )}
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                <h3 style={{ marginTop: 0, fontSize: '1.25rem' }}>{recipe.name}</h3>
                                <button onClick={() => handleDelete(recipe.id)} style={{ color: 'var(--danger)' }}>
                                    <Trash2 size={18} />
                                </button>
                            </div>

                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: 'auto', paddingTop: '1rem' }}>
                                <input
                                    type="checkbox"
                                    checked={selectedRecipes.has(recipe.id)}
                                    onChange={() => toggleSelection(recipe.id)}
                                    style={{ width: '1.2rem', height: '1.2rem' }}
                                />
                                <span style={{ fontSize: '0.9rem' }}>Add to Meal Plan</span>
                            </div>
                            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                                <button
                                    onClick={() => setPreviewRecipe(recipe)}
                                    className="btn btn-outline"
                                    style={{ flex: 1, justifyContent: 'center' }}
                                    title="Quick Look"
                                >
                                    <Eye size={18} />
                                </button>
                                <Link to={`/edit/${recipe.id}`} className="btn btn-outline" style={{ flex: 3, justifyContent: 'center' }}>
                                    Edit Recipe
                                </Link>
                            </div>
                        </div>
                    );
                })}
            </div>

            {previewRecipe && (
                <RecipePreviewModal
                    recipe={previewRecipe}
                    onClose={() => setPreviewRecipe(null)}
                />
            )}

            {recipes.length > 0 && hasMore && (
                <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                    <button onClick={loadMore} className="btn btn-outline">
                        <ChevronDown size={20} /> Load More
                    </button>
                </div>
            )}

            {recipes.length === 0 && (
                <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                    <ChefHat size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                    <p>No recipes found. Create one or adjust filters!</p>
                </div>
            )}
        </div>
    );
};

export default RecipeList;
