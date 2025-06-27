import { useEffect, useState } from "react";
import { auth } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";

export default function Home() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    onAuthStateChanged(auth, (currentUser) => setUser(currentUser));
  }, []);
  return (
    <div style={{ padding: "2rem" }}>
      <h1>USDT Invest</h1>
      <p>{user ? `Привет, ${user.email}` : "Войдите в аккаунт"}</p>
    </div>
  );
}