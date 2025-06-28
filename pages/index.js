
import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ padding: 20 }}>
      <h1>USDT Invest</h1>
      <Link href="/register">Зарегистрироваться</Link><br />
      <Link href="/login">Войти</Link>
    </div>
  );
}
