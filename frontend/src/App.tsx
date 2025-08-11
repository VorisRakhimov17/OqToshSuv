import React, { useEffect, useState } from "react";
import {
  ShoppingCart, Plus, Minus, Droplets, Phone, Mail, MapPin, Star, Check,
} from "lucide-react";
import api from "./lib/api"; // <= src/lib/api.ts

// ---- Types ----
interface Product {
  id: number;
  name: string;
  size: string;
  price: number | string;     // DRF Decimal string bo‘lishi mumkin
  image?: string | null;
  description?: string | null;
}
interface CartItem extends Product {
  quantity: number;
}

// ---- Utils ----
const priceToNumber = (p: number | string) =>
  typeof p === "number" ? p : parseFloat(p || "0");

const formatSum = (n: number | string) =>
  priceToNumber(n).toLocaleString("uz-UZ");

// ---- Component ----
export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [cart, setCart] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Nav scroll effekti
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Mahsulotlarni yuklash
  useEffect(() => {
    setLoading(true);
    api
      .get<Product[]>("/products/")
      .then((res) => setProducts(res.data))
      .catch(() => setError("Mahsulotlarni yuklashda xatolik"))
      .finally(() => setLoading(false));
  }, []);

  // Savat logikasi
  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existed = prev.find((i) => i.id === product.id);
      if (existed) {
        return prev.map((i) =>
          i.id === product.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const updateQuantity = (id: number, delta: number) => {
    setCart((prev) =>
      prev
        .map((i) =>
          i.id === id
            ? { ...i, quantity: Math.max(0, i.quantity + delta) }
            : i
        )
        .filter((i) => i.quantity > 0)
    );
  };

  const getTotalPrice = () =>
    cart.reduce((t, i) => t + priceToNumber(i.price) * i.quantity, 0);
  const getTotalItems = () => cart.reduce((t, i) => t + i.quantity, 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav
        className={`fixed top-0 w-full z-50 transition-all duration-300 ${
          scrolled ? "bg-white/90 backdrop-blur-md shadow-lg" : "bg-transparent"
        }`}
      >
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Droplets
                className={`h-8 w-8 transition-colors duration-300 ${
                  scrolled ? "text-blue-600" : "text-white"
                }`}
              />
              <h1
                className={`text-2xl font-bold transition-colors duration-300 ${
                  scrolled ? "text-gray-800" : "text-white"
                }`}
              >
                OQ TOSH
              </h1>
            </div>
            <button
              onClick={() => setIsCartOpen((s) => !s)}
              className={`relative p-2 rounded-full transition-all duration-300 ${
                scrolled
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-white/20 text-white hover:bg-white/30"
              }`}
            >
              <ShoppingCart className="h-6 w-6" />
              {getTotalItems() > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold animate-bounce">
                  {getTotalItems()}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section
        className="relative h-screen flex items-center justify-center overflow-hidden"
        style={{
          backgroundImage:
            "url(https://images.pexels.com/photos/1000084/pexels-photo-1000084.jpeg?auto=compress&cs=tinysrgb&w=1920)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundAttachment: "fixed",
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/70 via-blue-800/50 to-transparent" />
        <div className="relative z-10 text-center text-white px-6 animate-fade-in">
          <h2 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
            OQ TOSH SUV <br />
            <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              Sof Hayot
            </span>
          </h2>
          <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto opacity-90 leading-relaxed">
            Har qanday ehtiyoj uchun yuqori sifatli suv mahsulotlari. Shaxsiy
            hidratsiyadan tijorat ta&apos;minotigacha.
          </p>
          <button
            onClick={() =>
              document.getElementById("products")?.scrollIntoView({
                behavior: "smooth",
              })
            }
            className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-8 py-4 rounded-full text-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
          >
            Hozir sotib ol
          </button>
        </div>
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-white rounded-full mt-2 animate-pulse" />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-800 mb-4">
              Nima uchun OQ TOSH ni tanlaysiz
            </h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Biz tengsiz tozalik bilan eng yuqori sifatli suv mahsulotlarini
              yetkazib beramiz
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              {
                icon: <Droplets className="h-12 w-12 text-blue-500" />,
                title: "100% Sof",
                description:
                  "Kengaytirilgan filtrlash har bir tomchi mukammal toza bo‘lishini ta’minlaydi",
              },
              {
                icon: <Star className="h-12 w-12 text-blue-500" />,
                title: "Premium Sifat",
                description:
                  "Qattiq sifat nazorati eng yuqori standartlarga javob beradi",
              },
              {
                icon: <Check className="h-12 w-12 text-blue-500" />,
                title: "Ishonchli brend",
                description:
                  "Mamlakat bo‘ylab minglab mamnun mijozlar",
              },
            ].map((f, i) => (
              <div
                key={i}
                className="text-center group hover:transform hover:scale-105 transition-all duration-300"
              >
                <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full mb-6 group-hover:bg-blue-200 transition-colors duration-300">
                  {f.icon}
                </div>
                <h4 className="text-2xl font-bold text-gray-800 mb-4">
                  {f.title}
                </h4>
                <p className="text-gray-600 leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Products */}
      <section id="products" className="py-20 bg-gradient-to-b from-blue-50 to-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-800 mb-4">
              Bizning suv mahsulotlari
            </h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Assortimentdan har qanday vaziyatga mos keladigan mahsulotni tanlang
            </p>
          </div>

          {loading && (
            <div className="text-center text-gray-500">Yuklanmoqda...</div>
          )}
          {error && <div className="text-center text-red-600">{error}</div>}

          {!loading && !error && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {products.map((product, index) => (
                <div
                  key={product.id}
                  className="bg-white rounded-2xl shadow-lg overflow-hidden group hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="relative overflow-hidden">
                    <img
                      src={
                        product.image ||
                        "https://placehold.co/800x500?text=No+Image"
                      }
                      alt={product.name}
                      className="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute top-4 right-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      {product.size}
                    </div>
                  </div>

                  <div className="p-6">
                    <h4 className="text-2xl font-bold text-gray-800 mb-2">
                      {product.name}
                    </h4>
                    {product.description && (
                      <p className="text-gray-600 mb-4 leading-relaxed">
                        {product.description}
                      </p>
                    )}
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-3xl font-bold text-blue-600">
                        {formatSum(product.price)} so&apos;m
                      </span>
                      <span className="text-gray-500 text-lg">
                        shisha boshiga
                      </span>
                    </div>
                    <button
                      onClick={() => addToCart(product)}
                      className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
                    >
                      Savatga qo&apos;shish
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Contact */}
      <section className="py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold mb-4">Aloqa qiling</h3>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Savollaringiz bormi? Biz yordam beramiz.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Phone className="h-8 w-8" />,
                title: "Qo‘ng‘iroq qiling",
                info: "+998 (77) 160 90 00",
                sub: "9:00–21:00",
              },
              {
                icon: <Mail className="h-8 w-8" />,
                title: "Email",
                info: "oqtoshsuv@gmail.com",
                sub: "24 soat ichida javob",
              },
              {
                icon: <MapPin className="h-8 w-8" />,
                title: "Manzil",
                info: "Alisher Navoiy 123-uy",
                sub: "Qibray tumani",
              },
            ].map((c, i) => (
              <div key={i} className="text-center group">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-6 group-hover:bg-blue-500 transition-colors duration-300">
                  {c.icon}
                </div>
                <h4 className="text-xl font-bold mb-2">{c.title}</h4>
                <p className="text-blue-400 font-semibold mb-1">{c.info}</p>
                <p className="text-gray-400">{c.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Droplets className="h-6 w-6 text-blue-400" />
            <span className="text-xl font-bold">OQ TOSH</span>
          </div>
          <p className="text-gray-400">
            © 2025 OQ TOSH. Barcha huquqlar himoyalangan.
          </p>
        </div>
      </footer>

      {/* Cart sidebar */}
      <div
        className={`fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform transition-transform duration-300 z-50 ${
          isCartOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-800">Savat</h3>
            <button
              onClick={() => setIsCartOpen(false)}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              ×
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {cart.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <ShoppingCart className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">Savat bo‘sh</p>
              <p className="text-sm">Mahsulot qo‘shishni boshlang!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cart.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg"
                >
                  <img
                    src={item.image || "https://placehold.co/100x100"}
                    alt={item.name}
                    className="w-16 h-16 object-cover rounded"
                  />
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">
                      {item.name}
                    </h4>
                    <p className="text-sm text-gray-600">{item.size}</p>
                    <p className="text-blue-600 font-bold">
                      {formatSum(item.price)} so&apos;m
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => updateQuantity(item.id, -1)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Minus className="h-4 w-4" />
                    </button>
                    <span className="w-8 text-center font-semibold">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, 1)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {cart.length > 0 && (
          <div className="border-t p-6">
            <div className="flex items-center justify-between text-xl font-bold text-gray-800 mb-4">
              <span>Jami:</span>
              <span>{formatSum(getTotalPrice())} so&apos;m</span>
            </div>
            <button className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white py-3 rounded-xl font-semibold transition-all duration-300">
              To‘lovga o‘tish
            </button>
          </div>
        )}
      </div>

      {/* Overlay */}
      {isCartOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsCartOpen(false)}
        />
      )}

      {/* Custom animation */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fade-in 1s ease-out both; }
      `}</style>
    </div>
  );
}
