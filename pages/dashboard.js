
import { useEffect, useState } from 'react';
import { auth, db } from '../firebase/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import {
  doc,
  getDoc,
  updateDoc,
  serverTimestamp,
  setDoc,
  collection,
  addDoc,
  query,
  orderBy,
  getDocs
} from 'firebase/firestore';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState('');
  const [history, setHistory] = useState([]);

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
            const gain = updatedBalance * 0.01 * diffDays;
            updatedBalance += gain;
            await updateDoc(ref, {
              balance: updatedBalance,
              lastUpdate: serverTimestamp()
            });
            await addDoc(collection(db, "users", user.uid, "history"), {
              type: "Начисление",
              amount: gain,
              timestamp: serverTimestamp()
            });
          }
        } else {
          await updateDoc(ref, { lastUpdate: serverTimestamp() });
        }

        setBalance(updatedBalance.toFixed(2));

        const q = query(collection(db, "users", user.uid, "history"), orderBy("timestamp", "desc"));
        const snapshot = await getDocs(q);
        const hist = snapshot.docs.map(doc => doc.data());
        setHistory(hist);
      }
    });
    return () => unsub();
  }, []);

  const invest = async () => {
    const investAmount = parseFloat(amount);
    if (isNaN(investAmount) || investAmount < 1) {
      alert("Минимум 1 USDT");
      return;
    }

    const ref = doc(db, "users", user.uid);
    const snap = await getDoc(ref);
    const oldBalance = snap.data().balance;

    const newBalance = oldBalance + investAmount;
    await updateDoc(ref, {
      balance: newBalance
    });

    await addDoc(collection(db, "users", user.uid, "history"), {
      type: "Инвестиция",
      amount: investAmount,
      timestamp: serverTimestamp()
    });

    setBalance(newBalance.toFixed(2));
    setAmount('');
    alert(`Инвестировано ${investAmount} USDT`);
  };

  if (!user) return <p style={{ padding: 20 }}>Загрузка...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h1>Личный кабинет</h1>
      <p>Email: {user.email}</p>
      <p>Баланс: {balance} USDT</p>

      <input
        placeholder="Сумма (мин. 1 USDT)"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        type="number"
        min="1"
      />
      <button onClick={invest}>Инвестировать</button>

      <h2 style={{ marginTop: 30 }}>История операций</h2>
      <ul>
        {history.map((item, index) => (
          <li key={index}>
            {item.type}: +{item.amount.toFixed(2)} USDT
          </li>
        ))}
      </ul>
    </div>
  );
}
