// firebaseConfig.js
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore'; // Import Firestore


const firebaseConfig = {
  apiKey: "AIzaSyCvfjl0ZlHqvpc-7jeocM09WB0WxgASo-Q",
  authDomain: "swapitlikeithot.firebaseapp.com",
  projectId: "swapitlikeithot",
  storageBucket: "swapitlikeithot.appspot.com",
  messagingSenderId: "264073976301",
  appId: "1:264073976301:web:303395d9bb90c011aeafe4"
};

const app = initializeApp(firebaseConfig);

const firestore = getFirestore(app);

// Initialize Firebase Authentication and export necessary items
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { auth, provider, signInWithPopup, firestore };