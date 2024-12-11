import firebase_admin
from firebase_admin import credentials, firestore, storage
from firebase_admin import auth as firebase_auth
from flask import Flask, jsonify, request, render_template, redirect, url_for, g, flash
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

app = Flask(__name__)

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'swapitlikeithot.appspot.com'})
db = firestore.client()
bucket=storage.bucket()

# For debugging
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
#CORS(app)

load_dotenv()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# home page
@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('auth.login'))
    books_ref = db.collection('books')
    books = [doc.to_dict() for doc in books_ref.stream()]
    return render_template('index_copy.html', books=books)


# Helper function to normalize text (case and whitespace trimming)
def normalize_text(text):
    return text.strip().lower() if text else ''

@app.route('/books', methods=['GET'])
def get_books():
    books_ref = db.collection('books')

    category = request.args.get('category')
    if category:
        books_ref = books_ref.where('course_num', '==', category)

    books = []
    for doc in books_ref.stream():
        book_data = doc.to_dict()
        book_data['id'] = doc.id  # Add the document ID to each book's data
        books.append(book_data)
    
    # Handle sorting by price
    sort_option = request.args.get('sort')
    if sort_option == 'low_to_high':
        books = sorted(books, key=lambda x: float(x.get('price', 0)))
    elif sort_option == 'high_to_low':
        books = sorted(books, key=lambda x: float(x.get('price', 0)), reverse=True)

    return jsonify(books)

@app.route('/course_numbers', methods=['GET'])
def get_course_numbers():
    try: 
        books_ref = db.collection('books')

        # Retrieve all documents in the collection
        books = books_ref.stream()

        # Extract unique course numbers
        course_numbers = ()
        for doc in books:
            book_data = doc.to_dict()
            course_num = book_data.get('course_num')
            if course_num:
                course_numbers.add(course_num)
        # Return the list of unique course numbers
        return jsonify(list(course_numbers))
    except Exception as e: 
        print(f"Error in get_course_numbers: {e}")
        return jsonify({'error': 'Failed to fetch course numbers'}), 500

# view selected book
@app.route('/books/<book_id>', methods=['GET'])
def view_book(book_id):
    book_ref = db.collection('books').document(book_id)
    doc = book_ref.get()

    if doc.exists:
        return jsonify(doc.to_dict())
    else:
        return jsonify({"error": "Book not found"}), 404

# add a new book
@app.route('/add-book')
def book_form():
    return render_template('newpost.html')

# Add to wishlist function
@app.route('/add_to_wishlist', methods=['POST'])
def adding_to_wishlist():
    try:
        # Extract data from the request
        data = request.json
        user_id = data.get('User_ID')
        book_id = data.get('Book_ID')
        
        # Validate the input
        if not user_id or not book_id:
            return jsonify({'error': 'Missing user ID or book ID'}), 400
    
        # Create or update a document in the Wishlist collection
        wishlist_ref = db.collection('wishlist')
        query = wishlist_ref.where('User_ID', '==', user_id).where('Book_ID', '==', book_id).stream()

        if any(query):
            return jsonify({"Message:": "Book is already in your wishlist!"}), 200

        new_wishlist_item = {'User_ID': user_id,'Book_ID': book_id,}
        wishlist_ref.add(new_wishlist_item)

        return jsonify({'message': 'Book added to wishlist successfully!'}), 200

    except Exception as e:
        print(f"Error adding to wishlist: {e}")
        return jsonify({'error': 'Failed to add to wishlist'}), 500
    
@app.route('/delete_listing/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    print(f"Attempting to delete listing with ID: {listing_id}")  # Debugging line

    try:
        # Verify the user's Firebase ID token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        token = auth_header.split(" ")[1]
        decoded_token = firebase_auth.verify_id_token(token)
        user_id = decoded_token['uid']

        # Fetch the listing from Firestore
        doc_ref = db.collection('listings').document(listing_id)
        doc = doc_ref.get()

        if not doc.exists:
            print("Listing not found in Firestore.")  # Debugging line
            return jsonify({'error': 'Listing not found'}), 404

        listing_data = doc.to_dict()
        book_id = listing_data.get('Book_ID')
        user_id = listing_data.get('User_ID')

        # Check if the listing belongs to the current user
        if user_id != request.auth.uid:
            return jsonify({'error': 'Unauthorized'}), 403

        # Delete the listing from Firestore
        doc_ref.delete()
        print(f"Successfully deleted listing with ID: {listing_id}")
        
        book_ref = db.collection('books').document(book_id)
        book_ref.delete()
        print(f"Successfully deleted book with ID: {book_id}")
        
        return jsonify({'message': 'Listing deleted successfully'}), 200
    

    except Exception as e:
        print("Error during delete operation:", str(e))
        return jsonify({'error': 'Internal server error'}), 500
    

# Remove from wishlist function
@app.route('/remove_from_wishlist', methods=['POST'])
def removing_from_wishlist():
    try:
        # Extract data from the request
        data = request.json
        user_id = data.get('User_ID')
        book_id = data.get('Book_ID')
        
        # Validate the input
        if not user_id or not book_id:
            return jsonify({'error': 'Missing user ID or book ID'}), 400
    
        # Create or update a document in the Wishlist collection
        wishlist_ref = db.collection('wishlist')
        query = wishlist_ref.where('User_ID', '==', user_id).where('Book_ID', '==', book_id).stream()

        # Check if the document exists
        doc = next(query, None)  # Get the first document if it exists

        if doc:
            # If found, delete the document
            wishlist_ref.document(doc.id).delete()
            return jsonify({"message": "Book removed from wishlist successfully!"}), 200
        else:
            return jsonify({"error": "Item not found in wishlist"}), 404

    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500

# Add to wishlist function
@app.route('/is_in_wishlist', methods=['POST'])
def is_in_wishlist():
    try:
        # Extract data from the request
        data = request.json
        user_id = data.get('User_ID')
        book_id = data.get('Book_ID')
        
        # Validate the input
        if not user_id or not book_id:
            return jsonify({'error': 'Missing user ID or book ID'}), 400
    
        # Create or update a document in the Wishlist collection
        wishlist_ref = db.collection('wishlist')
        query = wishlist_ref.where('User_ID', '==', user_id).where('Book_ID', '==', book_id).stream()

        if any(query):
            return jsonify({"isInWishlist": True}), 200
        else:
            return jsonify({"isInWishlist": False}), 200

    except Exception as e:
        print("Error in is_in_wishlist:", str(e))
        return jsonify({"error": "An error occurred while checking the wishlist status"}), 500
    
#get wishlist function
@app.route('/get_wishlist', methods=['GET'])
def get_wishlist():
    try:
        # Extract the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token missing or invalid'}), 401
        
        # Get the token
        id_token = auth_header.split('Bearer ')[1]

        # Verify the token and decode the user's UID
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']

        # Query the wishlist for the user
        wishlist_ref = db.collection('wishlist').where('User_ID', '==', user_id)
        wishlist_items = wishlist_ref.stream()

        # Collect book details
        book_ids = [item.to_dict().get('Book_ID') for item in wishlist_items]
        books = []
        for book_id in book_ids:
            book_ref = db.collection('books').document(book_id)
            book_doc = book_ref.get()
            if book_doc.exists:
                book_data = book_doc.to_dict()
                book_data['id'] = book_id
                books.append(book_data)

        return jsonify(books), 200

    except Exception as e:
        print(f"Error fetching wishlist: {e}")
        return jsonify({'error': 'Failed to fetch wishlist'}), 500

@app.route('/report_seller', methods=['POST'])
def report_seller():
    print(request.json)  # Debug
    
    data = request.json
    seller_email = data.get('seller_email')
    buyer_email = data.get('buyer_email')
    book_name = data.get('book_name')

    if not all([seller_email, buyer_email, book_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        msg = Message(
            subject=f'Interest in your listing: {book_name}', 
            sender='swapitlikeitshot.silih@gmail.com',
            recipients=[seller_email]
        )
        msg.body = (
            f"Hello,\n\n"
            f"It was reported that your book listing '{book_name}', is a bit too high in price.\n\n"
            f"Consider reducing the price on your listing!\n\n"
            "Thank you!"
        )
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to send email'}), 500

@app.route('/show_interest', methods=['POST'])
def show_interest():
    print(request.json)  # Debug
    
    data = request.json
    seller_email = data.get('seller_email')
    buyer_email = data.get('buyer_email')
    book_name = data.get('book_name')

    if not all([seller_email, buyer_email, book_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        msg = Message(
            subject=f'Interest in your listing: {book_name}', 
            sender='swapitlikeitshot.silih@gmail.com',
            recipients=[seller_email]
        )
        msg.body = (
            f"Hello,\n\n"
            f"A buyer is interested in your book listing '{book_name}'.\n\n"
            f"Buyer's email: {buyer_email}\n\n"
            f"Please reach out to the buyer if the book is still available, or take down the listing if it is not.\n\n"
            "Thank you!"
        )
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to send email'}), 500

@app.route('/search', methods=['GET'])
def search_books():
    try:
        books_ref = db.collection('books')
        name = normalize_text(request.args.get('name', ''))
        author = normalize_text(request.args.get('author', ''))
        isbn = request.args.get('isbn', '').strip()

        results = []

        # Search by name (case-insensitive prefix search)
        if name:
            name_books = books_ref.where('name', '>=', name).where('name', '<=', name + '\uf8ff').stream()
            for doc in name_books:
                book_data = doc.to_dict()
                book_data['id'] = doc.id
                results.append(book_data)

        # Search by author (case-insensitive prefix search)
        if author:
            author_books = books_ref.where('author', '>=', author).where('author', '<=', author + '\uf8ff').stream()
            for doc in author_books:
                book_data = doc.to_dict()
                book_data['id'] = doc.id
                results.append(book_data)

        # Search by ISBN (exact match)
        if isbn:
            try:
                isbn_int = int(isbn)  # Ensure ISBN is treated as an integer
                isbn_books = books_ref.where('isbn', '==', isbn_int).stream()
                for doc in isbn_books:
                    book_data = doc.to_dict()
                    book_data['id'] = doc.id
                    results.append(book_data)
            except ValueError:
                print(f"Invalid ISBN: {isbn}")

        # Combine results and remove duplicates based on book ID
        unique_results = {book['id']: book for book in results}.values()

        return jsonify(list(unique_results))

    except Exception as e:
        print(f"Error in search_books: {e}")
        return jsonify({'error': 'An error occurred while searching for books'}), 500

@app.route('/search', methods=['GET'])
def search():
    return search_books()


#adding user after they sign in
@app.route('/add_user', methods=['POST'])
def adding_user():
    try:
        user_data = request.json
        
        # Check if all necessary data is provided
        if not user_data.get('uid') or not user_data.get('displayName') or not user_data.get('email'):
            return jsonify({"error": "Missing required user data"}), 400
        
        # Add the user to Firestore
        user_ref = db.collection('users').document(user_data['uid'])
        user_ref.set({
            'uid': user_data['uid'],
            'displayName': user_data['displayName'],
            'email': user_data['email'],
        })
        

        return jsonify({"message": "User added successfully"}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error adding user: {e}")
        return jsonify({"error": "Failed to add user"}), 500

# form submitted
@app.route('/added-book', methods=['POST'])
def add_book():
    try:
        name = request.form.get('name')
        author = request.form.get('author')
        version = request.form.get('version')
        isbn = request.form.get('isbn')
        course_num = request.form.get('course_num')
        price = request.form.get('price')
        condition = request.form.get('condition')
        contact = request.form.get('contact')
        description = request.form.get('description')
        user_id = request.form.get('user_id')

        image_urls = []
        for i in range(1, 4):  # Expecting up to 3 images
            pic = request.files.get(f'pic{i}')
            if pic:
                pic_url = upload_image(pic)
                image_urls.append(pic_url)

        if not image_urls:
            image_urls = None

        # Create a dictionary to store the form data
        form_data = {
            'name': name,
            'author': author,
            'version': version,
            'isbn': int(isbn),
            'course_num': course_num,
            'price': float(price),
            'condition': condition,
            'contact': contact,
            'pic': image_urls,
            'description': description
        }
        book_ref = db.collection('books').add(form_data)   # add entry to books collection
        
        
        # Also adds to listings
        listing_data = {
            'Book_ID': book_ref[1].id,
            'User_ID': user_id
        }

        db.collection('listings').add(listing_data)
        return render_template('submitted.html')
    except Exception as e:
        print("Error in add_textbook:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

# Path for showing the listings
@app.route('/my_listings', methods=['GET'])
def view_listings():
    try:
        # Extract the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token missing or invalid'}), 401
        
        # Get the token
        id_token = auth_header.split('Bearer ')[1]

        # Verify the token and decode the user's UID
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']

        # Query the wishlist for the user
        listings_ref = db.collection('listings').where('User_ID', '==', user_id)
        listings_items = listings_ref.stream()

        # Collect book details
        book_ids = [item.to_dict().get('Book_ID') for item in listings_items]
        books = []
        for book_id in book_ids:
            book_ref = db.collection('books').document(book_id)
            book_doc = book_ref.get()
            if book_doc.exists:
                book_data = book_doc.to_dict()
                book_data['id'] = book_id
                books.append(book_data)

        return jsonify(books), 200

    except Exception as e:
        print(f"Error fetching my listings: {e}")
        return jsonify({'error': 'Failed to fetch your listings'}), 500

def upload_image(pic):
    blob = bucket.blob(pic.filename)
    blob.upload_from_file(pic, content_type=pic.content_type)
    blob.make_public()
    url = blob.public_url
    return url

if __name__ == '__main__':
    app.run(debug=True)