// src/pages/Listings.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useAuth from '../hooks/useAuth'; // Ensure you're importing your useAuth hook
import './MyListings.css';
import BookTile from '../components/Navbar/BookTile'; // Assuming you use BookTile to display each listing

function MyListings() {
    const { isAuthenticated, idToken } = useAuth(); // Get the token and authentication state
    const [listings, setListings] = useState([]);  // Ensure listings is initialized as an empty array
    const [loading, setLoading] = useState(true);  // Loading state to handle async fetching

    useEffect(() => {
        const fetchListings = async () => {
            console.log("ID Token: ", idToken); // Log the token to verify it's not null and correct

            // if (!idToken) {
            //     console.log("No token found");
            //     setLoading(false);
            //     return;
            // }

            try {
                const response = await axios.get('http://localhost:5000/my-listings', {
                    headers: {
                        Authorization: `Bearer ${idToken}`, // Send the token as a Bearer token
                    },
                });

                // Ensure that the response is in the expected format
                setListings(response.data.listings || []); // Default to an empty array if no listings
            } catch (error) {
                console.error('Error fetching listings:', error.response ? error.response.data : error.message);
                setLoading(false); // Ensure loading stops even on error
            }
        };

        // Only fetch if authenticated and token is available
        if (isAuthenticated && idToken) {
            fetchListings();
        } else {
            setLoading(false); // Stop loading if user is not authenticated
        }
    }, [idToken, isAuthenticated]); // Re-run the effect when token or auth state changes

    // Loading spinner or message while the token is being fetched
    if (loading) {
        return <p>Loading...</p>;
    }

    return (
        <div className="listings-container">
            <h1>My Listings</h1>
            {listings.length > 0 ? (
                <div className="listings-grid">
                    {listings.map((listing, index) => (
                        <BookTile book={listing} key={index} />
                    ))}
                </div>
            ) : (
                <p>No listings available</p>
            )}
        </div>
    );
}

export default MyListings;
