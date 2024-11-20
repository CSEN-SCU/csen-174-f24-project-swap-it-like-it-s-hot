import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import { auth, provider, signInWithPopup } from '../firebaseConfig';
import useAuth from '../hooks/useAuth'; // Import the useAuth hook

function Login() {
  const navigate = useNavigate();
  const { isAuthenticated, idToken } = useAuth(); // Get the authentication state and ID token

  const handleLogin = () => {
    signInWithPopup(auth, provider)
      .then((result) => {
        const email = result.user.email;
        if (email.endsWith('@scu.edu')) {
          navigate('/marketplace');
        } else {
          alert('Please sign in with a school email.');
          auth.signOut();
        }
      })
      .catch((error) => {
        console.error("Login Error: ", error);
      });
  };

  // Handle sending the Firebase ID token with requests to your Flask backend
  const fetchData = async () => {
    if (isAuthenticated && idToken) {
      try {
        const response = await fetch('http://localhost:5000/my-listings', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${idToken}`, // Include Firebase ID token in Authorization header
            'Content-Type': 'application/json',
          },
        });
        const data = await response.json();
        console.log('My Listings:', data);
      } catch (error) {
        console.error('Error fetching listings:', error);
      }
    }
  };

  return (
    <div className="login-container">
      <div className="logo-section">
        <img src="images/silihLogoClear.png" alt="Logo" />
      </div>
      <div className="form-section">
        <h1 className="projectName">Swap It Like It's HOT!</h1>
        <h1 className="motto">For SCU by SCU</h1>
        <section>
          <h2>Sign In / Sign Up</h2>
          <button onClick={handleLogin}>Sign in with Google</button>
        </section>
      </div>
    </div>
  );
}

export default Login;
