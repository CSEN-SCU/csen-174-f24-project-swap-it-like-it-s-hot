import { useEffect, useState } from 'react';
import { auth } from '../firebaseConfig';  // Ensure your Firebase config exports `auth`
import { onAuthStateChanged } from 'firebase/auth';

function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [idToken, setIdToken] = useState(null);  // Renamed to match your MyListings.js

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setIsAuthenticated(true);
        const token = await user.getIdToken(true);  // Fetch the ID token asynchronously
        setIdToken(token);  // Set the token in the state
      } else {
        setIsAuthenticated(false);
        setIdToken(null);  // Reset the token if no user is authenticated
      }
    });

    return () => unsubscribe();  // Cleanup listener on unmount
  }, []);

  return { isAuthenticated, idToken };  // Return idToken here
}

export default useAuth;