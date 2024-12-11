import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './BookTile.css';

function BookTile({ book, showMenu = false, onEdit, onDelete }) {
    const [menuOpen, setMenuOpen] = useState(false);
    const placeholderImage = `${process.env.PUBLIC_URL}/images/placeholder.png`;

    const toggleMenu = (e) => {
        e.preventDefault();
        setMenuOpen(!menuOpen);
    };

    const handleEdit = (e) => {
        e.preventDefault();
        onEdit && onEdit(book);
    };

    const handleDelete = (e) => {
        e.preventDefault();
        onDelete && onDelete(book);
    };

    return (
        <div className="book-tile-container">
            {showMenu && (
                <div className="menu-container">
                    <button className="delete-menu" onClick={toggleMenu}>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="16"
                            height="16"
                            fill="white"
                            className="bi bi-three-dots-vertical"
                            viewBox="0 0 16 16"
                        >
                            <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0" />
                        </svg>
                    </button>
                    {menuOpen && (
                        <div className="menu-dropdown">
                            <button onClick={handleEdit}>Edit</button>
                            <button onClick={handleDelete}>Delete</button>
                        </div>
                    )}
                </div>
            )}
            <Link key={book.id} to={`/books/${book.id}`} className="book-tile">
                <img
                    src={book.pic && book.pic.length > 0 ? book.pic[0] : placeholderImage}
                    alt={book.name}
                    className="book-image"
                />
                <div className="book-info">
                    <h2>{book.name}</h2>
                    <h3>{book.author}</h3>
                    <h3>
                        ${new Intl.NumberFormat('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                        }).format(book.price)}
                    </h3>
                </div>
            </Link>
        </div>
    );
}

export default BookTile;
