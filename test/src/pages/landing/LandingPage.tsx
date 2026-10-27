import { useState } from 'react'
import { productCollection } from '../../entities/product'
import { ContactCallout } from '../../widgets/contact-callout'
import { ProductShowcase } from '../../widgets/product-showcase'
import './landing.css'

export function LandingPage() {
  const [activeCategory, setActiveCategory] = useState('all')
  return <main className="landing" dir="rtl">
    <nav className="site-nav" aria-label="ناوبری اصلی"><a className="brand" href="#top" aria-label="روستا، صفحه اصلی">روستا<span>Ar</span></a><div className="nav-links"><a href="#collection">مجموعه</a><a href="#story">داستان ما</a><a href="#contact">تماس</a></div><a className="nav-cta" href="#collection">دیدن مجموعه <span aria-hidden="true">←</span></a></nav>
    <section className="hero" id="top" aria-labelledby="hero-title"><div className="hero-copy"><p className="eyebrow">مجموعه تازه / پاییز</p><h1 id="hero-title">لباس‌هایی برای<br /><em>روزهای ماندگار.</em></h1><p className="hero-lede">فرم‌های ساده، پارچه‌های طبیعی و جزئیاتی که هر روز به آن‌ها برمی‌گردید.</p><a className="button button-dark" href="#collection">دیدن مجموعه <span aria-hidden="true">←</span></a></div><div className="hero-visual" role="img" aria-label="مدل با لباس‌های مجموعه پاییز"><div className="hero-label">NEW<br />COLLECTION<br /><span>پاییز - زمستان</span></div><div className="hero-orb" /><img src="https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=1100&q=85" alt="مدل با لباس‌های پاییزی" /></div></section>
    <section className="story" id="story" aria-labelledby="story-title"><p className="eyebrow">نگاه ما / داستان ما</p><h2 id="story-title">کمتر، اما بهتر.</h2><p>ما لباس‌هایی می‌سازیم که با زندگی روزمره همراه شوند؛ با پارچه‌های باکیفیت، برش‌های دقیق و توجه به جزئیاتی که حس خوب می‌سازند.</p></section>
    <ProductShowcase products={productCollection.products} categories={productCollection.categories} activeCategory={activeCategory} onCategoryChange={setActiveCategory} renderEmpty={<p className="empty-state" role="status">محصولی در این دسته پیدا نشد.</p>} />
    <ContactCallout /><footer className="site-footer"><span>روستا استودیو</span><span>برای دیدن جزئیات بیشتر و هماهنگی بازدید، با ما در تماس باشید.</span><a href="mailto:hello@rosta.studio">hello@rosta.studio</a></footer>
  </main>
}
