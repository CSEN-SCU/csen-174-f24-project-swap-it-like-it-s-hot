import React, { useEffect, useState } from 'react';
import { auth } from '../firebaseConfig';
import './Listings.css';
import BookTile from '../components/Navbar/BookTile';

function Listings() {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchListings = async () => {
            try {
                const currentUser = auth.currentUser;

                if (!currentUser) {
                    console.error("User not logged in");
                    return;
                }

                const token = await currentUser.getIdToken();

                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/my_listings`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setListings(data);
                } else {
                    console.error("Failed to fetch listings:", await response.text());
                }
            } catch (error) {
                console.error("Error fetching listings:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchListings();
    }, []);

    if (loading) return <p>Loading listings...</p>;

    return (
        <div className="listings-container">
            <div className="listings-header">
                <h1>Your Listings</h1>
                <p>Browse the books you’ve added as listings.</p>
            </div>
            <div className="listings-grid">
                {listings.length > 0 ? (
                    listings.map((book, index) => (
                        <BookTile book={book} key={index} />
                    ))
                ) : (
                    <p>No items added yet. Start adding books!</p>
                )}
            </div>
        </div>
    );
}

export default Listings;
