"""Product enrichment service - Trendyol'dan ürün bilgilerini çeker"""
from __future__ import annotations

import re
from typing import Optional
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


@dataclass
class ProductInfo:
    """Ürün bilgileri"""
    url: str
    title: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    currency: str = "TL"


class ProductEnrichmentService:
    """Trendyol'dan ürün bilgilerini çeken servis"""
    
    def __init__(self):
        self.timeout = 10.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    
    async def fetch_product_info(self, url: str) -> ProductInfo:
        """URL'den ürün bilgilerini çek"""
        
        # Kısa linkler için gerçek URL'yi al (ty.gl gibi)
        if "ty.gl" in url or "trendyol.com" not in url:
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.head(url, headers=self.headers)
                    url = str(response.url)
            except Exception as e:
                print(f"URL redirect error: {e}")
        
        # Trendyol kontrolü
        if "trendyol.com" in url:
            return await self._fetch_trendyol(url)
        else:
            return ProductInfo(url=url)
    
    async def _fetch_trendyol(self, url: str) -> ProductInfo:
        """Trendyol'dan ürün bilgilerini çek"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")
                
                # Başlık - Yeni selector (iki farklı format)
                title = None
                # Format 1: data-testid="product-title"
                title_elem = soup.find("h1", attrs={"data-testid": "product-title"})
                if not title_elem:
                    # Format 2: class="product-title variant-pdp"
                    title_elem = soup.find("h1", class_="product-title variant-pdp")
                if not title_elem:
                    # Format 3: Sadece "product-title" class'ı
                    title_elem = soup.find("h1", class_="product-title")
                if not title_elem:
                    # Fallback: pr-new-br
                    title_elem = soup.find("h1", class_="pr-new-br")
                if not title_elem:
                    # Son fallback: herhangi bir h1
                    title_elem = soup.find("h1")
                if title_elem:
                    # Sadece metin al, <a> ve <strong> içindeki metinler dahil
                    title = title_elem.get_text(strip=True)
                
                # Fiyat - Yeni selector (en ucuz fiyatı bul)
                price = None
                prices = []
                
                # 1. ty-plus-price yapısındaki fiyatlar (sepette/kampanya fiyatları)
                plus_price_elem = soup.find("div", class_="ty-plus-price-content")
                if plus_price_elem:
                    # Sepette indirimli fiyat
                    discounted_elem = plus_price_elem.find("span", class_="ty-plus-price-discounted-price")
                    if discounted_elem:
                        price_val = self._extract_price(discounted_elem.get_text(strip=True))
                        if price_val:
                            prices.append(price_val)
                    
                    # Normal fiyat
                    original_elem = plus_price_elem.find("div", class_="ty-plus-price-original-price")
                    if original_elem:
                        price_val = self._extract_price(original_elem.get_text(strip=True))
                        if price_val:
                            prices.append(price_val)
                
                # 2. campaign-price-content yapısı
                campaign_price_elem = soup.find("div", class_="campaign-price-content")
                if campaign_price_elem:
                    # Sepette indirimli fiyat
                    new_price = campaign_price_elem.find("p", class_="new-price")
                    if new_price:
                        price_val = self._extract_price(new_price.get_text(strip=True))
                        if price_val:
                            prices.append(price_val)
                    
                    # Eski fiyat
                    old_price = campaign_price_elem.find("p", class_="old-price")
                    if old_price:
                        price_val = self._extract_price(old_price.get_text(strip=True))
                        if price_val:
                            prices.append(price_val)
                
                # 3. data-testid="lowest-price" yapısı (14 günün en düşük fiyatı)
                lowest_price_btn = soup.find("button", attrs={"data-testid": "lowest-price"})
                if lowest_price_btn:
                    price_view = lowest_price_btn.find("div", class_="price-view")
                    if price_view:
                        # Sadece indirimli fiyatı al (en ucuz olan)
                        discounted = price_view.find("span", class_="discounted")
                        if discounted:
                            price_val = self._extract_price(discounted.get_text(strip=True))
                            if price_val:
                                prices.append(price_val)
                
                # 4. data-testid="normal-price" yapısı (iki farklı format)
                price_wrapper = soup.find("div", attrs={"data-testid": "normal-price"})
                if price_wrapper:
                    # Format 1: price-container içinde discounted span
                    price_container = price_wrapper.find("div", class_="price-container")
                    if price_container:
                        price_elem = price_container.find("span", class_="discounted")
                        if price_elem:
                            price_val = self._extract_price(price_elem.get_text(strip=True))
                            if price_val:
                                prices.append(price_val)
                    else:
                        # Format 2: Doğrudan discounted span
                        price_elem = price_wrapper.find("span", class_="discounted")
                        if price_elem:
                            price_val = self._extract_price(price_elem.get_text(strip=True))
                            if price_val:
                                prices.append(price_val)
                
                # 5. Fallback fiyat selector'ları
                if not prices:
                    price_elem = soup.find("span", class_="prc-dsc")
                    if not price_elem:
                        price_elem = soup.find("span", class_="prc-slg")
                    if price_elem:
                        price_val = self._extract_price(price_elem.get_text(strip=True))
                        if price_val:
                            prices.append(price_val)
                
                # En ucuz fiyatı al
                if prices:
                    price = min(prices)
                
                # Resim - Yeni selector
                image_url = None
                # Önce data-testid="image" içinde ara
                img_elem = soup.find("img", attrs={"data-testid": "image"})
                if not img_elem:
                    img_elem = soup.find("img", class_="ph-gallery-img")
                if not img_elem:
                    img_elem = soup.find("img", attrs={"data-src": True})
                if img_elem:
                    image_url = img_elem.get("src") or img_elem.get("data-src")
                    if image_url and not image_url.startswith("http"):
                        image_url = "https:" + image_url
                
                return ProductInfo(
                    url=url,
                    title=title,
                    price=price,
                    image_url=image_url,
                    currency="TL"
                )
        except Exception as e:
            print(f"Trendyol fetch error: {e}")
            return ProductInfo(url=url)
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Metin içinden fiyat çıkar"""
        if not price_text:
            return None
        
        # Sadece sayıları ve nokta/virgül al
        cleaned = re.sub(r"[^\d,.]", "", price_text)
        
        # Virgülü noktaya çevir
        cleaned = cleaned.replace(",", ".")
        
        # Birden fazla nokta varsa son noktadan sonrasını al (kuruş)
        if cleaned.count(".") > 1:
            parts = cleaned.split(".")
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        
        try:
            return float(cleaned)
        except (ValueError, AttributeError):
            return None


# Global instance
product_service = ProductEnrichmentService()
