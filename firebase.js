import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyD00vVS6J4QFpyl1IFrQsZOt_9u65VPoEc",
  authDomain: "dimans-usdt-invest.firebaseapp.com",
  projectId: "dimans-usdt-invest",
  storageBucket: "dimans-usdt-invest.firebasestorage.app",
  messagingSenderId: "744128222079",
  appId: "1:744128222079:web:57e5c70eff9339fbf3c04a",
  measurementId: "G-RCB51FKQ3T"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);