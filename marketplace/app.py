import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from flask import Flask, jsonify, request, render_template, redirect, url_for, g, flash, session
from flask_cors import CORS
from mailjet_rest import Client
import json
from marketplace.auth import bp as auth_bp
from functools import wraps

app = Flask(__name__)
app.register_blueprint(auth_bp)

with open('mailConfig.json') as config_file:
    mailjet_config = json.load(config_file)

MAILJET_API_KEY = mailjet_config['MAILJET_API_KEY']
MAILJET_API_SECRET = mailjet_config['MAILJET_API_SECRET']

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'swapitlikeithot.appspot.com'})
db = firestore.client()
bucket=storage.bucket()

CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

@app.before_request
def load_user():
    # Example logic for setting g.user, modify according to your authentication method
    # If using session-based auth:
    if "user_email" in session:  # Replace with your actual session key for user email
        g.user = {"email": session["user_email"], "name": session.get("user_name", "Anonymous")}
    else:
        g.user = None

@app.before_request
def authenticate_user():
    id_token = request.headers.get("Authorization")  # Expecting Firebase ID token in headers
    if id_token:
        try:
            decoded_token = auth.verify_id_token(id_token)
            g.user = {
                "email": decoded_token.get("email"),
                "uid": decoded_token.get("uid"),
                "name": decoded_token.get("name", "Firebase User")
            }
        except Exception as e:
            print(f"Error verifying Firebase token: {e}")
            g.user = None
    else:
        g.user = None


# home page
@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('auth.login'))
    books_ref = db.collection('books')
    books = [doc.to_dict() for doc in books_ref.stream()]
    return render_template('index_copy.html', books=books)

# view all books
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
    books_ref = db.collection('books')

    # Retrieve all documents in the collection
    books = books_ref.stream()

    # Extract unique course numbers
    course_numbers = set()
    for doc in books:
        book_data = doc.to_dict()
        course_num = book_data.get('course_num')
        if course_num:
            course_numbers.add(course_num)

    # Return the list of unique course numbers
    return jsonify(list(course_numbers))

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
@app.route('/add_wishlist/<book_id>', methods=['POST'])
def add_to_wishlist(book_id):
    # Checking the user to make sure they are signed in
    user_id = g.user["id"] 
    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    wishlist_ref = db.collection("users").document(user_id).collection("wishlist")

    # checking if the book is already in the wishlist for the user
    books_doc = wishlist_ref.document(book_id).get()
    if books_doc.exists:
        return jsonify({"message": "Book already in wishlist:"}), 200

    # actually adding the book to wishlist
    wishlist_ref.document(book_id).set({
        "book_ref": f"/books/{book_id}"
    })

    return jsonify({"message": "Book added to wishlist"}), 200

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    seller_email = data.get('seller_email')
    book_name = data.get('book_name')

    # Ensure the user is authenticated
    if not g.user:
        return jsonify({'error': 'User not authenticated'}), 401

    # Use the authenticated user's email
    buyer_email = g.user.get('email')

    if not seller_email or not book_name:
        return jsonify({'error': 'Missing required fields'}), 400

    # Autogenerate message
    message = f"Hi, I'm interested in your book '{book_name}'. Please let me know if it is available. You can reach me at {buyer_email}. Thanks!"

    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    email_data = {
        'Messages': [
            {
                "From": {
                    "Email": buyer_email,
                    "Name": g.user.get('name', 'Interested Buyer')  # Default to 'Interested Buyer' if name isn't available
                },
                "To": [
                    {
                        "Email": seller_email,
                        "Name": "Seller"
                    }
                ],
                "Subject": f"Interest in Your Book: {book_name}",
                "TextPart": message,
                "HTMLPart": f"<p>{message}</p>"
            }
        ]
    }

    result = mailjet.send.create(data=email_data)
    if result.status_code == 200:
        return jsonify({'success': 'Email sent successfully'}), 200
    else:
        return jsonify({'error': 'Failed to send email'}), 500


def search_books():
    books_ref = db.collection('books')
    
    # Get query parameters from the request
    name = request.args.get('name', '').lower()  # Convert name to lowercase for case-insensitive matching
    course_num = request.args.get('course_num', '')  # Using course_num instead of author or isbn directly

    # Apply filters based on available parameters
    if name:
        books_ref = books_ref.where('name', '>=', name).where('name', '<=', name + '\uf8ff')  # Firestore range query

    if course_num:
        books_ref = books_ref.where('course_num', '==', course_num)

    # Retrieve and format results
    results = []
    try:
        for doc in books_ref.stream():
            book_data = doc.to_dict()
            book_data['id'] = doc.id
            results.append(book_data)

        return jsonify(results)
    
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': 'An error occurred while searching for books'}), 500
    
@app.route('/search', methods=['GET'])
def search():
    return search_books()

    
def validate_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise ValueError("Invalid token")
    
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            token = token.split(" ")[1]  # Remove "Bearer " from the token
            decoded_token = auth.verify_id_token(token)
            g.user = decoded_token  # Set the user object to the decoded token
        except Exception as e:
            print(f"Token verification failed: {e}")
            return jsonify({"error": "Token is invalid or expired"}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/my-listings', methods=['GET'])
@token_required
def get_my_listings():
    token = request.headers.get('Authorization')
    print(f"Authorization Header: {token}")

    if not token:
        return jsonify({"error": "Token missing"}), 401

    token = token.split('Bearer ')[1] if 'Bearer ' in token else token
    print(f"Extracted Token: {token}")  # Print out the token to inspect

    if g.user is None:
        return jsonify({"error": "User not authenticated"}), 401
    
    user_email = g.user.get('email')  # Now it's safe to access the email
    if not user_email:
        return jsonify({"error": "User email not found"}), 400
    

    try:
        books_ref = db.collection('books')
        books = []
        for doc in books_ref.stream():
            book_data = doc.to_dict()
            book_data['id'] = doc.id  # Add the document ID to each book's data
            books.append(book_data)
        
        return jsonify(books)
    except Exception as e:
        print(f"Error retrieving listings for {user_email}: {e}")
        return jsonify({"error": "Failed to retrieve listings"}), 500


# @app.route('/my-listings', methods=['GET'])
# @token_required
# def get_my_listings():
#     if g.user is None:
#         return jsonify({"error": "User not authenticated"}), 401

#     # user_email = g.user.get('email')  # Now it's safe to access the email
#     # print(f"User email: {user_email}")

#     # Fetch user-specific listings (dummy response for now)
#     return jsonify({"listings": ["Listing 1", "Listing 2"]})

#     user_email = g.user.get('email')
#     if not user_email:
#         return jsonify({"error": "User email not found"}), 400

#     try:
#         books_ref = db.collection('books').where('contact', '==', user_email)
#         listings = [doc.to_dict() for doc in books_ref.stream()]
#         return jsonify(listings), 200
#     except Exception as e:
#         print(f"Error retrieving listings for {user_email}: {e}")
#         return jsonify({"error": "Failed to retrieve listings"}), 500


# form submitted
@app.route('/added-book', methods=['POST'])
#@login_required
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
        db.collection('books').add(form_data)   # add entry to books collection
        return render_template('submitted.html')
    except Exception as e:
        print("Error in add_textbook:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

def upload_image(pic):
    blob = bucket.blob(pic.filename)
    blob.upload_from_file(pic, content_type=pic.content_type)
    blob.make_public()
    url = blob.public_url
    return url

if __name__ == '__main__':
    app.run(debug=True)
    print(app.url_map)