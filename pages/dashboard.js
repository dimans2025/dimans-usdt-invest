import { useEffect, useState } from 'react';
import { auth, db } from '../firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { doc, getDoc, updateDoc, serverTimestamp } from 'firebase/firestore';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [balance, setBalance] = useState(0);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user);
        const ref = doc(db, "users", user.uid);
        const snap = await getDoc(ref);
        const data = snap.data();
        let updatedBalance = data.balance;

        if (data.lastUpdate) {
          const last = data.lastUpdate.toDate();
          const now = new Date();
          const diffDays = Math.floor((now - last) / (1000 * 60 * 60 * 24));
          if (diffDays > 0) {
            updatedBalance += updatedBalance * 0.01 * diffDays;
            await updateDoc(ref, {
              balance: updatedBalance,
              lastUpdate: serverTimestamp()
            });
          }
        } else {
          await updateDoc(ref, { lastUpdate: serverTimestamp() });
        }

        setBalance(updatedBalance.toFixed(2));
      }
    });
    return () => unsub();
  }, []);

  if (!user) return <p style={{ padding: 20 }}>Загрузка...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h1>Личный кабинет</h1>
      <p>Email: {user.email}</p>
      <p>Баланс: {balance} USDT</p>
    </div>
  );
}