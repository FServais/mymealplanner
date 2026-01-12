import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RecipeList from './components/RecipeList';
import RecipeForm from './components/RecipeForm';
import PDFImport from './components/PDFImport';
import ShoppingList from './components/ShoppingList';
import Admin from './components/Admin';
import RecipeFinder from './components/RecipeFinder';
import BulkReview from './components/BulkReview';
import { UtensilsCrossed, ShoppingCart, ChefHat, Settings, Sparkles, ClipboardCheck } from 'lucide-react';

import { useLocation } from 'react-router-dom';

import MealPlanList from './components/MealPlanList';

function Content() {
  const [planRecipes, setPlanRecipes] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const showSidebar = location.pathname !== '/import' && location.pathname !== '/shopping-list' && location.pathname !== '/admin' && location.pathname !== '/finder' && location.pathname !== '/review';

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <nav style={{ backgroundColor: 'var(--surface)', borderBottom: '1px solid var(--border)', padding: '1rem 0', position: 'relative' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 2rem' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--primary)' }}>
            <UtensilsCrossed />
            <span>VibedMeal</span>
          </Link>

          {/* Hamburger Menu Button */}
          <button
            className="mobile-only"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            style={{ color: 'var(--text)', padding: '0.5rem' }}
          >
            <div style={{ width: '24px', height: '2px', backgroundColor: 'currentColor', marginBottom: '6px' }}></div>
            <div style={{ width: '24px', height: '2px', backgroundColor: 'currentColor', marginBottom: '6px' }}></div>
            <div style={{ width: '24px', height: '2px', backgroundColor: 'currentColor' }}></div>
          </button>

          <div className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
            <Link to="/" className="nav-link" onClick={() => setIsMenuOpen(false)}>Recipes</Link>
            <Link to="/finder" className="nav-link" onClick={() => setIsMenuOpen(false)} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Sparkles size={16} /> AI Finder
            </Link>
            <Link to="/meal-plans" className="nav-link" onClick={() => setIsMenuOpen(false)}>Meal Plans</Link>
            <Link to="/import" className="nav-link" onClick={() => setIsMenuOpen(false)}>Import PDF</Link>
            <Link to="/shopping-list" className="nav-link" onClick={() => setIsMenuOpen(false)}>
              <ShoppingCart size={20} /> Shopping List
            </Link>
            <Link to="/review" className="nav-link" onClick={() => setIsMenuOpen(false)}>
              <ClipboardCheck size={20} /> Review
            </Link>
            <Link to="/admin" className="nav-link" onClick={() => setIsMenuOpen(false)}>
              <Settings size={20} /> Admin
            </Link>
          </div>
        </div>
      </nav>

      <main className="container" style={{ flex: 1, display: 'grid', gridTemplateColumns: showSidebar ? 'repeat(auto-fit, minmax(300px, 1fr))' : '1fr', gap: '2rem', marginTop: '2rem' }}>
        <div style={{ minWidth: 0, gridColumn: showSidebar ? '1 / -2' : '1 / -1' }}>
          <Routes>
            <Route path="/" element={<RecipeList selectedRecipes={planRecipes} setSelectedRecipes={setPlanRecipes} />} />
            <Route path="/finder" element={<RecipeFinder />} />
            <Route path="/meal-plans" element={<MealPlanList onLoadPlan={setPlanRecipes} />} />
            <Route path="/create" element={<RecipeForm />} />
            <Route path="/edit/:id" element={<RecipeForm />} />
            <Route path="/import" element={<PDFImport />} />
            <Route path="/shopping-list" element={<ShoppingList recipes={planRecipes} />} />
            <Route path="/review" element={<BulkReview />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </div>

        {showSidebar && (
          <aside className="desktop-only" style={{ gridColumn: '-2 / -1', minWidth: '300px' }}>
            <div style={{ position: 'sticky', top: '2rem' }}>
              <ShoppingList recipes={planRecipes} />
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
