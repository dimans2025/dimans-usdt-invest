import { useState } from 'react';
import { auth, db } from '../firebase';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';
import { useRouter } from 'next/router';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleRegister = async (e) => {
    e.preventDefault();
    const { user } = await createUserWithEmailAndPassword(auth, email, password);
    await setDoc(doc(db, "users", user.uid), {
      email,
      balance: 0,
      lastUpdate: serverTimestamp(),
      createdAt: serverTimestamp()
    });
    router.push("/dashboard");
  };

  return (
    <form onSubmit={handleRegister} style={{ padding: 20 }}>
      <h2>Регистрация</h2>
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
      <input value={password} onChange={e => setPassword(e.target.value)} placeholder="Пароль" type="password" />
      <button type="submit">Зарегистрироваться</button>
    </form>
  );
}