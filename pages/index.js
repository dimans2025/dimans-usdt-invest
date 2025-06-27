import Link from 'next/link';
export default function Home() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Добро пожаловать в USDT Invest</h1>
      <p>Инвестируйте в USDT под 1% в день. Минимум: 1 USDT.</p>
      <p>TRC20-кошелёк: <strong>TD19DdRMpApXtcGf197fet6qjKmmBtRGWy</strong></p>
      <p><Link href="/login">Войти</Link> или <Link href="/register">Зарегистрироваться</Link></p>
    </div>
  );
}