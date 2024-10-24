// Step 1: Load the .env file at the top of your app
require('dotenv').config();  // Load environment variables from .env file

// Step 2: Import the Firebase SDK
const firebase = require('firebase/app');
require('firebase/auth');       // Import Firebase Authentication if needed
require('firebase/firestore');   // Import Firebase Firestore if needed

// Step 3: Create the Firebase configuration object using environment variables
const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

// Step 4: Initialize Firebase with the configuration
firebase.initializeApp(firebaseConfig);

// Now you can use Firebase services (e.g., Firestore, Authentication)
const db = firebase.firestore();

// Example: Add a document to the Firestore 'users' collection
db.collection('users').add({
  name: 'John Doe',
  email: 'john.doe@example.com'
}).then((docRef) => {
  console.log('Document written with ID: ', docRef.id);
}).catch((error) => {
  console.error('Error adding document: ', error);
});
