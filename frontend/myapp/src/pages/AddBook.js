import React, { useState } from 'react';
import './AddBook.css';

function AddBook() {
    const [formData, setFormData] = useState({
        name: '',
        author: '',
        version: '',
        isbn: '',
        course_num: '',
        price: '',
        contact: '',
    });
    const [uploadedImages, setUploadedImages] = useState([]); // Array to hold image files

    const RequiredStar = () => <span className="required-star">*</span>;

    // Handle image upload by either clicking or dragging
    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file && uploadedImages.length < 3) {
            setUploadedImages((prev) => [...prev, { file, preview: URL.createObjectURL(file) }]);
        }
    };

    // Handle image delete
    const handleDeleteImage = (index) => {
        const updatedImages = [...uploadedImages];
        updatedImages.splice(index, 1);
        setUploadedImages(updatedImages);
    };

    // Handle drag-and-drop image upload
    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && uploadedImages.length < 3) {
            setUploadedImages((prev) => [...prev, { file, preview: URL.createObjectURL(file) }]);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = new FormData();
        // Append form fields
        Object.keys(formData).forEach((key) => data.append(key, formData[key]));
        // Append images
        uploadedImages.forEach(({ file }, index) => data.append(`pic${index + 1}`, file));

        try {
            const response = await fetch('http://localhost:5000/added-book', {
                method: 'POST',
                body: data,
            });

            if (response.ok) {
                window.location.href = '/submitted.html';
            } else {
                const result = await response.json();
                alert('Failed to add textbook: ' + result.error);
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Error submitting form');
        }
    };

    return (
        <div className="add-book-container">
            <form onSubmit={handleSubmit} encType="multipart/form-data">
                <h2>Add Your Own Textbook:</h2>
                <div className="upload-area-container">
                    {uploadedImages.map((image, index) => (
                        <div key={index} className="upload-area">
                            <img src={image.preview} alt={`Preview ${index + 1}`} />
                            <div className="trash-can" onClick={() => handleDeleteImage(index)}>
                                🗑️
                            </div>
                        </div>
                    ))}
                    {uploadedImages.length < 3 && (
                        <div
                            className="upload-area"
                            onClick={() => document.getElementById('pic').click()}
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={handleDrop}
                        >
                            <label>Drag & Drop or Click to Upload</label>
                            <input
                                type="file"
                                accept="image/*"
                                id="pic"
                                style={{ display: 'none' }}
                                onChange={handleImageChange}
                            />
                        </div>
                    )}
                </div>

                <div className="fields-container">
                    <div className="fields-names-container">
                        <p>Textbook Name<RequiredStar /></p>
                        <p>Author<RequiredStar /></p>
                        <p>Edition Number</p>
                        <p>ISBN</p>
                        <p>Course Number<RequiredStar /></p>
                        <p>Price<RequiredStar /></p>
                        <p>Preferred Contact Information<RequiredStar /></p>
                    </div>
                    <div className="fields-forms-container">
                        <input type="text" name="name" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
                        <input type="text" name="author" value={formData.author} onChange={(e) => setFormData({...formData, author: e.target.value})} required />
                        <input type="number" name="version" value={formData.version} onChange={(e) => setFormData({...formData, version: e.target.value})} />
                        <input type="number" name="isbn" value={formData.isbn} onChange={(e) => setFormData({...formData, isbn: e.target.value})} />
                        <input type="text" name="course_num" value={formData.course_num} onChange={(e) => setFormData({...formData, course_num: e.target.value})} required />
                        <input type="number" name="price" value={formData.price} onChange={(e) => setFormData({...formData, price: e.target.value})} required />
                        <input type="text" name="contact" value={formData.contact} onChange={(e) => setFormData({...formData, contact: e.target.value})} required />
                    </div>
                </div>

                <div className="form-buttons">
                    <button type="submit" className="form-submit">Submit</button>
                    <button type="button" className="form-cancel" onClick={() => window.location.href = '/marketplace'}>Cancel</button>
                </div>
            </form>
        </div>
    );
}

export default AddBook;