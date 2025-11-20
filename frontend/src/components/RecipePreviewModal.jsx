import React from 'react';
import { X, Clock, Users, ChefHat } from 'lucide-react';

const RecipePreviewModal = ({ recipe, onClose }) => {
    if (!recipe) return null;

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
            padding: '2rem'
        }} onClick={onClose}>
            <div style={{
                backgroundColor: 'var(--surface)',
                borderRadius: '1rem',
                width: '100%',
                maxWidth: '800px',
                maxHeight: '90vh',
                overflowY: 'auto',
                position: 'relative',
                boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
            }} onClick={e => e.stopPropagation()}>

                <div style={{
                    padding: '2rem',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'start',
                    position: 'sticky',
                    top: 0,
                    backgroundColor: 'var(--surface)',
                    zIndex: 10
                }}>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.75rem', color: 'var(--primary)' }}>{recipe.name}</h2>
                        {recipe.description && (
                            <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>{recipe.description}</p>
                        )}
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'var(--text-secondary)',
                            padding: '0.5rem',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                        className="hover-bg"
                    >
                        <X size={24} />
                    </button>
                </div>

                <div style={{ padding: '2rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                        <div>
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)' }}>
                                <ChefHat size={20} /> Ingredients
                            </h3>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {recipe.ingredients.map((ing, idx) => (
                                    <li key={idx} style={{
                                        padding: '0.75rem 0',
                                        borderBottom: '1px solid var(--border)',
                                        display: 'flex',
                                        justifyContent: 'space-between'
                                    }}>
                                        <span>{ing.name}</span>
                                        <span style={{ color: 'var(--text-secondary)', fontWeight: '500' }}>{ing.quantity}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div>
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)' }}>
                                <Clock size={20} /> Instructions
                            </h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                {recipe.instructions.map((inst, idx) => (
                                    <div key={idx} style={{ display: 'flex', gap: '1rem' }}>
                                        <div style={{
                                            background: 'var(--primary)',
                                            color: 'white',
                                            width: '24px',
                                            height: '24px',
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: '0.8rem',
                                            flexShrink: 0,
                                            marginTop: '0.2rem'
                                        }}>
                                            {inst.step_number}
                                        </div>
                                        <p style={{ margin: 0, lineHeight: '1.6' }}>{inst.text}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RecipePreviewModal;
