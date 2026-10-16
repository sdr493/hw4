import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import ChatBubble from './components/ChatBubble'
import ChatResultsSection from './components/ChatResultsSection'
import CoatOfArms from './components/CoatOfArms'
import NavBar from './components/NavBar'
import PromoBanner from './components/PromoBanner'
import PromoPopup from './components/PromoPopup'
import Skyline from './components/Skyline'
import About from './pages/About'
import AuthForm from './pages/AuthForm'
import Coupon from './pages/Coupon'
import Home from './pages/Home'
import ProductDetail from './pages/ProductDetail'
import Products from './pages/Products'

export default function App() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return (
    <>
      <NavBar />
      <PromoBanner />
      <main>
        <ChatResultsSection />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/coupon" element={<Coupon />} />
          <Route path="/login" element={<AuthForm mode="login" />} />
          <Route path="/create-account" element={<AuthForm mode="signup" />} />
          <Route path="*" element={<section className="section"><h1>Page not found</h1></section>} />
        </Routes>
      </main>
      <Skyline />
      <footer className="footer">
        <div className="footer__crest"><CoatOfArms size={44} /></div>
        © Campus Customs · Built by a Yale MBA student
      </footer>
      <ChatBubble />
      <PromoPopup />
    </>
  )
}
