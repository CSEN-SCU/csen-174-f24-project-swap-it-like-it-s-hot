// src/pages/Marketplace.js
import React, { useState, useEffect } from 'react';
import './Marketplace.css';
import BookTile from '../components/Navbar/BookTile';
import Sidebar from '../components/Navbar/Sidebar';


function Marketplace({ searchResults = [] }) {
    const [books, setBooks] = useState([]);
    const [sortOption, setSortOption] = useState('relevant');
    const [category, setCategory] = useState('');
    const [categories, setCategories] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);


    const clearFilters = () => {
        setCategory('');
        setSortOption('relevant');
        setBooks([]);  // Clear books if searchResults are cleared
    };
    const fetchBooks = async () => {
        try {
            const query = new URLSearchParams();
            if (sortOption) query.append('sort', sortOption);
            if (category) query.append('category', category);
            query.append('page', currentPage);
            query.append('limit', 10);
    
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/books?${query.toString()}`);
            const data = await response.json();
    
            setBooks(data.books || []); // Use an empty array as fallback
            setTotalPages(data.pages || 0); // Use 0 as fallback
        } catch (error) {
            console.error("Error fetching books:", error);
            setBooks([]); // Fallback to an empty array in case of error
            setTotalPages(0); // Fallback to 0 pages in case of error
        }
    };

    useEffect(() => {
        if (!searchResults || searchResults.length === 0) {
            fetchBooks();
        } else {
            setBooks(searchResults);  // Use searchResults directly if available
        }
    }, [sortOption, category, searchResults]);  // Avoid refetching if searchResults are available

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/course_numbers`);
                const data = await response.json();
                setCategories(Array.isArray(data) ? data : []);
            } catch (error) {
                console.error("Error fetching course numbers:", error);
                setCategories([]);
            }
        };

        fetchCategories();
    }, []);

    useEffect(() => {
        console.log("searchResults in Marketplace:", searchResults);
        if (!searchResults || searchResults.length === 0) {
            fetchBooks(); // Fall back to fetching books
        } else {
            setBooks(searchResults);
        }
    }, [sortOption, category, searchResults]);

    if (searchResults && searchResults.length > 0) {
        console.log("First book in searchResults:", searchResults[0]);
    }

    useEffect(() => {
        if (searchResults && searchResults.length > 0) {
            console.log("Setting books from searchResults:", searchResults);
            setBooks(searchResults);
        }
    }, [searchResults]);

    useEffect(() => {
        fetchBooks();
    }, [sortOption, category, currentPage]);

    const handlePageChange = (page) => {
        setCurrentPage(page);
    };


    // useEffect(() => {
    //     const fetchCategories = async () => {
    //         try {
    //             const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/course_numbers`);
    //             const data = await response.json();
    //             setCategories(Array.isArray(data) ? data : []); // Ensure categories is an array
    //         } catch (error) {
    //             console.error("Error fetching categories:", error);
    //             setCategories([]); // Fallback to empty array
    //         }
    //     };

    //     fetchCategories();
    // }, []);

    // useEffect(() => {
    //     if (searchResults && Array.isArray(searchResults) && searchResults.length > 0) {
    //         setBooks(searchResults);
    //     } else {
    //         fetchBooks();
    //     }
    // }, [searchResults, sortOption, category, currentPage]);

    // const handlePageChange = (page) => {
    //     setCurrentPage(page);
    // };

    return (
       
        <div className="marketplace-container">
            <Sidebar
                setCategory={setCategory}
                sortOption={sortOption}
                setSortOption={setSortOption}
                categories={categories}
                clearFilters={clearFilters}
            />
            {/* <div className="marketplace-grid">
                {(searchResults && searchResults.length > 0 ? searchResults : books).map((book, index) => (
                    <BookTile book={book} key={index} />
                ))}
            </div> */}
            <div className ="marketplace-grid-container">

                <div className="marketplace-grid">
                    {(searchResults && Array.isArray(searchResults) && searchResults.length > 0
                        ? searchResults
                        : books
                    ).map((book, index) => (
                        <BookTile book={book} key={index} />
                    ))}
                </div>

                <div className="pagination">
                    {Array.from({ length: totalPages }, (_, index) => (
                        <button
                            key={index + 1}
                            onClick={() => handlePageChange(index + 1)}
                            className={currentPage === index + 1 ? 'active' : ''}
                        >
                            {index + 1}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Marketplace;