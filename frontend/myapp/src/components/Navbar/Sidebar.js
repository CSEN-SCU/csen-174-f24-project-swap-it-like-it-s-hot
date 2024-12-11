import React, { useState } from 'react';
import './Sidebar.css';

function Dropdown({ sortOption, setSortOption }) {
    const handleChange = (event) => {
        setSortOption(event.target.value);
    };

    return (
        <div>
            <label htmlFor="dropdown">Sort by: </label>
            <select id="dropdown" value={sortOption} onChange={handleChange}>
                <option value="relevant">Most Relevant</option>
                <option value="low_to_high">Price Low to High</option>
                <option value="high_to_low">Price High to Low</option>
            </select>
        </div>
    );
}

function Sidebar({ setCategory, sortOption, setSortOption, categories, clearFilters }) {
    const [selectedCategory, setSelectedCategory] = useState('');
    const [isCoursesVisible, setIsCoursesVisible] = useState(false); // State for toggling courses section

    const handleCategoryChange = (category) => {
        setSelectedCategory(category);
        setCategory(category);
    };

    const handleClearFilters = () => {
        setSelectedCategory('');
        clearFilters();
    };

    const toggleCoursesVisibility = () => {
        setIsCoursesVisible((prev) => !prev); // Toggle the visibility state
    };

    return (
        <div className="sidebar">
            <h2>Filters</h2>
            <Dropdown sortOption={sortOption} setSortOption={setSortOption} />
            <h3>Categories</h3>
            <button type="button" className="collapsible" onClick={toggleCoursesVisibility}>
                Courses
            </button>
            {isCoursesVisible && ( // Conditionally render the courses section
                <div className="collapsed-courses">
                    <div className="category-list">
                        { Array.isArray(categories) && categories.map((category) => (
                            <label key={category} className={`category-item ${selectedCategory === category ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="category"
                                    value={category}
                                    checked={selectedCategory === category}
                                    onChange={() => handleCategoryChange(category)}
                                />
                                {category}
                            </label>
                        ))}
                    </div>
                </div>
            )}
            <button onClick={handleClearFilters} className="clear-filters-btn">
                Clear Filters
            </button>
        </div>
    );
}

export default Sidebar;