import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8082';

const api = axios.create({
    baseURL: API_URL,
    paramsSerializer: params => {
        const searchParams = new URLSearchParams();
        for (const key in params) {
            const val = params[key];
            if (Array.isArray(val)) {
                val.forEach(v => searchParams.append(key, v));
            } else if (val !== undefined && val !== null) {
                searchParams.append(key, val);
            }
        }
        return searchParams.toString();
    }
});

export const getRecipes = (params) => api.get('/recipes/', { params });
export const getRecipeCount = (params) => api.get('/recipes/count', { params });

// Tools
export const suggestDuplicates = () => api.post('/tools/ingredients/suggest-duplicates?provider=gemini');
export const mergeIngredients = (data) => api.post('/tools/ingredients/merge', data);
export const getIngredients = () => api.get('/recipes/ingredients');
export const getRecipe = (id) => api.get(`/recipes/${id}`);
export const createRecipe = (recipe) => api.post('/recipes/', recipe);
export const updateRecipe = (id, recipe) => api.put(`/recipes/${id}`, recipe);
export const deleteRecipe = (id) => api.delete(`/recipes/${id}`);
export const importRecipePDF = (formData, provider = 'openai') => api.post(`/recipes/import/pdf?provider=${provider}`, formData, {
    headers: {
        'Content-Type': 'multipart/form-data',
    },
});
export const getImportStatus = (taskId) => api.get(`/recipes/import/status/${taskId}`);
export const generateShoppingList = (recipeIds) => api.post('/meal-planner/generate-shopping-list', recipeIds);

export const createMealPlan = (mealPlan) => api.post('/meal-plans/', mealPlan);
export const getMealPlans = () => api.get('/meal-plans/');
export const getMealPlan = (id) => api.get(`/meal-plans/${id}`);
export const deleteMealPlan = (id) => api.delete(`/meal-plans/${id}`);

export default api;
