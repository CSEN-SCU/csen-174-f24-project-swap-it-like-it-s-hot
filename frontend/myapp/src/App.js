// App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Marketplace from './pages/Marketplace';
import BookDetail from './pages/BookDetail';
import Login from './pages/Login';
import Navbar from './components/Navbar/Navbar';
import AddBook from './pages/AddBook';
import useAuth from './hooks/useAuth'; // Import the custom hook to get auth status
import './App.css';
import MyListings from './pages/MyListings';

function App() {
  const [searchResults, setSearchResults] = useState([]);  // State for storing search results

  return (
    <Router>
      <AppContent 
        searchResults={searchResults} 
        setSearchResults={setSearchResults} 
      />
    </Router>
  );
}

function AppContent({ searchResults, setSearchResults }) {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const isLoginPage = location.pathname === '/';

  return (
    <div>
      {/* Render Navbar only if not on the login page */}
      {!isLoginPage && (
        <Navbar setSearchResults={setSearchResults} />  // Pass setSearchResults to Navbar
      )}

      <Routes>
        <Route
          path="/"
          element={isAuthenticated ? <Navigate to="/marketplace" /> : <Login />}
        />
        
        <Route
          path="/marketplace"
          element={
            isAuthenticated ? (
              <Marketplace searchResults={searchResults} />  // Pass searchResults to Marketplace
            ) : (
              <Navigate to="/" />
            )
          }
        />

        <Route
          path="/add-book"
          element={isAuthenticated ? <AddBook /> : <Navigate to="/" />}
        />

        <Route
          path="/books/:id"
          element={isAuthenticated ? <BookDetail /> : <Navigate to="/" />}
        />

        <Route
          path="/my-listings"
          element={isAuthenticated ? <MyListings /> : <Navigate to="/" />}
        />
      </Routes>
    </div>
  );
}

export default App;
