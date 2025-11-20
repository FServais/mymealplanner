import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { importRecipePDF, createRecipe } from '../services/api';
import { Upload, Loader, FileText } from 'lucide-react';

const PDFImport = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await importRecipePDF(formData);
            const extractedRecipe = response.data;

            // Automatically save the imported recipe
            await createRecipe(extractedRecipe);
            navigate('/');
        } catch (err) {
            console.error("Import failed", err);
            setError("Failed to import PDF. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <div style={{ marginBottom: '1.5rem', color: 'var(--primary)' }}>
                <FileText size={48} />
            </div>
            <h2 style={{ marginTop: 0 }}>Import from PDF</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                Upload a PDF recipe and we'll extract the details for you using AI.
            </p>

            {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                    <Loader className="spin" size={24} />
                    <span>Analyzing recipe...</span>
                </div>
            ) : (
                <label className="btn btn-primary" style={{ cursor: 'pointer', display: 'inline-flex' }}>
                    <Upload size={20} />
                    <span>Upload PDF</span>
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                    />
                </label>
            )}

            {error && (
                <div style={{ marginTop: '1rem', color: 'var(--danger)' }}>
                    {error}
                </div>
            )}
        </div>
    );
};

export default PDFImport;
