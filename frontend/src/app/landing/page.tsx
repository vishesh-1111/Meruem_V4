import BrandSlide from "@/components/Landing/BrandSlide";
import CTA from "@/components/Landing/CTA";
import Footer from "@/components/Landing/Footer";
import Header from "@/components/Landing/Header";
import Hero from "@/components/Landing/Hero";
import Pricing from "@/components/Landing/Pricing";
import ProductCard from "@/components/Landing/ProductCard";
import ProductShowcase from "@/components/Landing/ProductShowcase";
import Testimonials from "@/components/Landing/Testimonials";

export default function LandingPage() {
  return (
    <div>
      <Header />
      <Hero/>
      <BrandSlide/>
      <ProductShowcase/>
      <ProductCard/>
      <Pricing/>
      <Testimonials/>
      <CTA/>
      <Footer/>
    </div>
  );
}
