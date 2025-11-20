import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RecipeList from './components/RecipeList';
import RecipeForm from './components/RecipeForm';
import PDFImport from './components/PDFImport';
import ShoppingList from './components/ShoppingList';
import Admin from './components/Admin';
import { UtensilsCrossed, ShoppingCart, ChefHat, Settings } from 'lucide-react';

import { useLocation } from 'react-router-dom';

import MealPlanList from './components/MealPlanList';

function Content() {
  const [planRecipes, setPlanRecipes] = useState([]);
  const location = useLocation();
  const showSidebar = location.pathname !== '/import' && location.pathname !== '/shopping-list' && location.pathname !== '/admin';

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <nav style={{ backgroundColor: 'var(--surface)', borderBottom: '1px solid var(--border)', padding: '1rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 2rem' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--primary)' }}>
            <UtensilsCrossed />
            <span>VibedMeal</span>
          </Link>
          <div className="nav-links">
            <Link to="/" className="nav-link">Recipes</Link>
            <Link to="/meal-plans" className="nav-link">Meal Plans</Link>
            <Link to="/import" className="nav-link">Import PDF</Link>
            <Link to="/shopping-list" className="nav-link">
              <ShoppingCart size={20} /> Shopping List
            </Link>
            <Link to="/admin" className="nav-link">
              <Settings size={20} /> Admin
            </Link>
          </div>
        </div>
      </nav>

      <main className="container" style={{ flex: 1, display: 'grid', gridTemplateColumns: showSidebar ? '1fr 350px' : '1fr', gap: '2rem', marginTop: '2rem' }}>
        <div style={{ minWidth: 0 }}>
          <Routes>
            <Route path="/" element={<RecipeList onAddToPlan={setPlanRecipes} />} />
            <Route path="/meal-plans" element={<MealPlanList onLoadPlan={setPlanRecipes} />} />
            <Route path="/create" element={<RecipeForm />} />
            <Route path="/edit/:id" element={<RecipeForm />} />
            <Route path="/import" element={<PDFImport />} />
            <Route path="/shopping-list" element={<ShoppingList recipeIds={planRecipes} />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </div>

        {showSidebar && (
          <aside>
            <div style={{ position: 'sticky', top: '2rem' }}>
              <ShoppingList recipeIds={planRecipes} />
            </div>
          </aside>
        )}
      </main>

      <footer style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border)', marginTop: 'auto' }}>
        <p>© 2024 VibedMeal Planner. Built with FastAPI & React.</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Content />
    </Router>
  );
}

export default App;
