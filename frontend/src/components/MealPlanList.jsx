import React, { useState, useEffect } from 'react';
import { getMealPlans, getMealPlan, deleteMealPlan } from '../services/api';
import { Calendar, ChevronRight, Loader, Trash2 } from 'lucide-react';

const MealPlanList = ({ onLoadPlan }) => {
    const [plans, setPlans] = useState([]);
    const [loading, setLoading] = useState(true);

    const [expandedPlanId, setExpandedPlanId] = useState(null);

    useEffect(() => {
        fetchPlans();
    }, []);

    const fetchPlans = async () => {
        try {
            const response = await getMealPlans();
            setPlans(response.data);
        } catch (error) {
            console.error("Error fetching meal plans", error);
        } finally {
            setLoading(false);
        }
    };

    const handleLoad = async (id) => {
        try {
            const response = await getMealPlan(id);
            const recipeIds = response.data.recipes.map(r => r.id);
            onLoadPlan(recipeIds);
        } catch (error) {
            console.error("Error loading meal plan", error);
        }
    };

    const handleDelete = async (e, id) => {
        e.stopPropagation(); // Prevent triggering handleLoad
        if (window.confirm("Are you sure you want to delete this meal plan?")) {
            try {
                await deleteMealPlan(id);
                fetchPlans(); // Refresh list
            } catch (error) {
                console.error("Error deleting meal plan", error);
                alert("Failed to delete meal plan");
            }
        }
    };

    const toggleExpand = (e, id) => {
        e.stopPropagation();
        setExpandedPlanId(expandedPlanId === id ? null : id);
    };

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}><Loader className="spin" /></div>;

    return (
        <div>
            <div className="header">
                <h1>Saved Meal Plans</h1>
            </div>

            <div className="grid">
                {plans.map((plan) => (
                    <div key={plan.id} className="card" style={{ cursor: 'pointer' }} onClick={() => handleLoad(plan.id)}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Calendar size={18} />
                                    {plan.name}
                                </h3>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                                    {new Date(plan.created_at).toLocaleDateString()} • {plan.recipes.length} recipes
                                </p>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <button
                                    onClick={(e) => handleDelete(e, plan.id)}
                                    className="btn-icon"
                                    style={{ color: 'var(--error)', padding: '0.5rem' }}
                                    title="Delete meal plan"
                                >
                                    <Trash2 size={18} />
                                </button>
                                <button
                                    onClick={(e) => toggleExpand(e, plan.id)}
                                    className="btn-icon"
                                    style={{ padding: '0.5rem', transform: expandedPlanId === plan.id ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
                                    title="View recipes"
                                >
                                    <ChevronRight size={20} color="var(--text-secondary)" />
                                </button>
                            </div>
                        </div>

                        {expandedPlanId === plan.id && (
                            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)', cursor: 'default' }} onClick={(e) => e.stopPropagation()}>
                                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Recipes in this plan:</h4>
                                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                                    {plan.recipes.map(recipe => (
                                        <li key={recipe.id} style={{ marginBottom: '0.25rem' }}>{recipe.name}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {plans.length === 0 && (
                <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                    <Calendar size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                    <p>No saved meal plans yet.</p>
                </div>
            )}
        </div>
    );
};

export default MealPlanList;
