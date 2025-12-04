import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { importRecipePDF, createRecipe, getImportStatus } from '../services/api';
import { Upload, Loader, FileText } from 'lucide-react';

const PDFImport = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [provider, setProvider] = useState('openai');

    const pollForStatus = async (taskId) => {
        const maxAttempts = 180; // 6 minutes max (180 * 2s)
        let attempts = 0;

        while (attempts < maxAttempts) {
            try {
                const statusResponse = await getImportStatus(taskId);
                const task = statusResponse.data;

                if (task.status === 'completed') {
                    // Success - save the recipe
                    await createRecipe(task.result);
                    navigate('/');
                    return;
                } else if (task.status === 'failed') {
                    // Failed - show error
                    const errorMessage = task.error || 'Unknown error occurred';
                    setError(`Error: ${errorMessage}`);
                    setLoading(false);
                    return;
                }

                // Still processing - wait and try again
                await new Promise(resolve => setTimeout(resolve, 2000));
                attempts++;
            } catch (err) {
                console.error('Error polling status:', err);
                setError('Failed to check processing status. Please try again.');
                setLoading(false);
                return;
            }
        }

        // Timeout
        setError('Processing timeout. The PDF import took too long. Please try again.');
        setLoading(false);
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Submit the file and get task ID
            const response = await importRecipePDF(formData, provider);
            const { task_id } = response.data;

            // Start polling for status
            await pollForStatus(task_id);
        } catch (err) {
            console.error("Import failed", err);

            // Extract detailed error message from response
            let errorMessage = "Failed to import PDF. Please try again.";

            if (err.response) {
                if (err.response.status === 400) {
                    errorMessage = "Could not extract text from PDF. Please ensure the file is a valid PDF.";
                } else if (err.response.status === 500) {
                    const detail = err.response.data?.detail || "Server error during processing";
                    errorMessage = `Error: ${detail}`;
                } else if (err.response.status === 413) {
                    errorMessage = "File is too large. Maximum size is 10MB.";
                } else {
                    errorMessage = err.response.data?.detail || err.message || errorMessage;
                }
            } else if (err.code === 'ECONNABORTED') {
                errorMessage = "Request timeout. Please try again.";
            } else if (err.request) {
                errorMessage = "Network error. Please check your connection and try again.";
            }

            setError(errorMessage);
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

            {/* Provider selector */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                    AI Model Provider
                </label>
                <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    disabled={loading}
                    style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '8px',
                        border: '1px solid var(--border)',
                        backgroundColor: 'var(--bg-secondary)',
                        color: 'var(--text-primary)',
                        fontSize: '1rem',
                        cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                >
                    <option value="openai">OpenAI (GPT-4)</option>
                    <option value="gemini">Google Gemini</option>
                </select>
            </div>

            {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                    <Loader className="spin" size={24} />
                    <span>Analyzing recipe with {provider === 'openai' ? 'OpenAI' : 'Gemini'}...</span>
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
