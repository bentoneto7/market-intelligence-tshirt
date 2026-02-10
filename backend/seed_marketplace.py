"""Seed marketplace_products with realistic Shopee t-shirt data."""

from datetime import datetime

from app.database import SessionLocal, init_db
from app.models.marketplace_product import MarketplaceProduct

PRODUCTS = [
    # AC/DC - URLs reais da Shopee
    {"title": "Camiseta ACDC AC DC Guitarra Preta De Banda Rock Unissex", "price": 39.90, "original_price": 59.90, "sold_count": 4521, "rating": 4.7, "review_count": 587, "seller_name": "Aluvino Shop", "seller_location": "São Paulo/SP", "related_artist": "AC/DC", "category": "camiseta_banda", "search_term": "camiseta acdc",
     "product_url": "https://shopee.com.br/Camiseta-ACDC-AC-DC-Guitarra-Preta-De-Banda-Rock-Masculina-E-Feminina-(Unissex)-100-Algod%C3%A3o-Infantil-Adulto-Plus-Size-i.522425551.21145745304"},
    {"title": "Camiseta de Rock / Camisa de Banda / Camiseta AC/DC", "price": 44.90, "original_price": 64.90, "sold_count": 3200, "rating": 4.6, "review_count": 420, "seller_name": "Rock Store BR", "seller_location": "São Paulo/SP", "related_artist": "AC/DC", "category": "camiseta_banda", "search_term": "camiseta ac/dc",
     "product_url": "https://shopee.com.br/Camiseta-de-Rock-Camisa-de-Banda-Camiseta-AC-DC-i.324993638.5259270912"},
    {"title": "Camiseta ACDC Highway to Hell", "price": 49.90, "original_price": 69.90, "sold_count": 2847, "rating": 4.8, "review_count": 312, "seller_name": "Metal Merch", "seller_location": "São Paulo/SP", "related_artist": "AC/DC", "category": "camiseta_banda", "search_term": "camiseta acdc",
     "product_url": "https://shopee.com.br/Camiseta-ACDC-(Camiseta-AC-DC-Highway-to-Hell)-i.481971262.11516282535"},
    {"title": "Camiseta Algodão ACDC Banda de Rock Angus Young Hard Metal", "price": 42.90, "original_price": None, "sold_count": 1890, "rating": 4.9, "review_count": 198, "seller_name": "Streetwear SP", "seller_location": "São Paulo/SP", "related_artist": "AC/DC", "category": "camiseta_banda", "search_term": "camiseta acdc",
     "product_url": "https://shopee.com.br/Camiseta-Algodao-ACDC-Ac-Dc-Banda-de-Rock-Bandas-Classicas-Angus-Young-Hard-Metal-Camisa-Unissex-i.897640504.20970360090"},
    {"title": "Camiseta AC/DC Black Ice Preta Banda De Rock Plus Size", "price": 54.90, "original_price": 69.90, "sold_count": 1560, "rating": 4.5, "review_count": 234, "seller_name": "Aluvino Shop", "seller_location": "São Paulo/SP", "related_artist": "AC/DC", "category": "camiseta_banda", "search_term": "camiseta acdc",
     "product_url": "https://shopee.com.br/Camiseta-AC-DC-AC-DC-ACDC-Black-Ice-Preta-Banda-De-Rock-Masculina-E-Feminina-(Unissex)-100-Algod%C3%A3o-Tamanho-Plus-G1-G2-G3-Camisa-Blusa-Infantil-Adulto-Aluvino-Shop-i.522425551.21996957470"},

    # Guns N' Roses - URLs reais da Shopee
    {"title": "Camiseta Banda Guns N' Roses Oversized Streetwear Premium", "price": 47.90, "original_price": 64.90, "sold_count": 5120, "rating": 4.7, "review_count": 678, "seller_name": "Premium Rock", "seller_location": "São Paulo/SP", "related_artist": "Guns N' Roses", "category": "camiseta_banda", "search_term": "camiseta guns n roses",
     "product_url": "https://shopee.com.br/Camiseta-Banda-Guns-N'-Roses-Oversized-Streetwear-Masculina-30.1-Premium-Rock-i.724130088.22493204560"},
    {"title": "Camiseta Skull Caveira Banda Rock Guns N Roses", "price": 39.90, "original_price": 54.90, "sold_count": 3890, "rating": 4.8, "review_count": 456, "seller_name": "Rock Music Store", "seller_location": "São Paulo/SP", "related_artist": "Guns N' Roses", "category": "camiseta_banda", "search_term": "camiseta guns n roses",
     "product_url": "https://shopee.com.br/Camiseta-Skull-Caveira-Banda-Rock-Guns-N-Roses-Musica-i.394163276.9237826885"},
    {"title": "Camiseta Guns N' Roses Banda Rock", "price": 42.90, "original_price": 59.90, "sold_count": 2340, "rating": 4.6, "review_count": 289, "seller_name": "Metal Merch", "seller_location": "São Paulo/SP", "related_artist": "Guns N' Roses", "category": "camiseta_banda", "search_term": "camiseta guns n roses",
     "product_url": "https://shopee.com.br/Camiseta-Guns-N'-Roses-Banda-Rock-i.420215377.11506561161"},
    {"title": "Camiseta Guns N Roses Banda Show Blusa Rock", "price": 34.90, "original_price": 49.90, "sold_count": 4560, "rating": 4.7, "review_count": 534, "seller_name": "Rock Store BR", "seller_location": "São Paulo/SP", "related_artist": "Guns N' Roses", "category": "camiseta_banda", "search_term": "camiseta guns n roses",
     "product_url": "https://shopee.com.br/Camiseta-Guns-N-Roses-Banda-Show-Blusa-Rock-Camisa-ou-Baby-Look-i.389303940.15591718234"},

    # My Chemical Romance - URLs reais da Shopee
    {"title": "Camiseta My Chemical Romance The Black Parade", "price": 44.90, "original_price": 64.90, "sold_count": 6780, "rating": 4.9, "review_count": 890, "seller_name": "Emo Store", "seller_location": "São Paulo/SP", "related_artist": "My Chemical Romance", "category": "camiseta_banda", "search_term": "camiseta my chemical romance",
     "product_url": "https://shopee.com.br/Camiseta-My-Chemical-Romance-The-Black-Parade-i.299191059.6654084892"},
    {"title": "CAMISETA MY CHEMICAL ROMANCE MCR BLACK PARADE", "price": 49.90, "original_price": None, "sold_count": 4230, "rating": 4.8, "review_count": 534, "seller_name": "Rock Store BR", "seller_location": "São Paulo/SP", "related_artist": "My Chemical Romance", "category": "camiseta_banda", "search_term": "camiseta mcr",
     "product_url": "https://shopee.com.br/CAMISETA-MY-CHEMICAL-ROMANCE-MCR-BLACK-PARADE-i.503080430.22693563692"},
    {"title": "Camiseta My Chemical Romance Mcr The Black Parade", "price": 42.90, "original_price": 59.90, "sold_count": 2100, "rating": 4.7, "review_count": 245, "seller_name": "Loja Underground", "seller_location": "Curitiba/PR", "related_artist": "My Chemical Romance", "category": "camiseta_banda", "search_term": "camiseta mcr",
     "product_url": "https://shopee.com.br/Camiseta-My-Chemical-Romance-Mcr-The-Black-Parade-i.447843269.13006373145"},
    {"title": "Camiseta Banda Emo My Chemical Romance Pop Punk", "price": 34.90, "original_price": 49.90, "sold_count": 8920, "rating": 4.6, "review_count": 1023, "seller_name": "Alt Fashion", "seller_location": "Belo Horizonte/MG", "related_artist": "My Chemical Romance", "category": "camiseta_banda", "search_term": "camiseta mcr",
     "product_url": "https://shopee.com.br/Camiseta-Banda-Emo-My-Chemical-Romance-Pop-Punk-i.452746376.11732358926"},

    # Lollapalooza / Sabrina Carpenter - URLs reais da Shopee
    {"title": "Camiseta Unissex Lollapalooza 2025 Festival Estampa Criativa", "price": 54.90, "original_price": 79.90, "sold_count": 2340, "rating": 4.7, "review_count": 267, "seller_name": "Festival Merch", "seller_location": "São Paulo/SP", "related_artist": None, "related_event": "Lollapalooza Brasil 2026", "category": "camiseta_festival", "search_term": "camiseta lollapalooza",
     "product_url": "https://shopee.com.br/Camiseta-Unissex-Lollapalooza-2025-Exclusivo-para-Festival-com-Estampa-Criativa-i.397588367.22798131806"},
    {"title": "Camisa Unissex Sabrina Carpenter Lollapalooza 2026", "price": 47.90, "original_price": None, "sold_count": 3450, "rating": 4.8, "review_count": 389, "seller_name": "Pop Culture", "seller_location": "São Paulo/SP", "related_artist": "Sabrina Carpenter", "category": "camiseta_artista", "search_term": "camiseta sabrina carpenter",
     "product_url": "https://shopee.com.br/Camisa-Unissex-Off-Cantora-Pop-Sabrina-Carpenter-100-Algod%C3%A3o-Lollapalooza-2026-Please-Please-i.1031072947.42717843331"},
    {"title": "CAMISETA SABRINA CARPENTER SHORT N SWEET 100% ALGODÃO", "price": 44.90, "original_price": 59.90, "sold_count": 2890, "rating": 4.7, "review_count": 312, "seller_name": "Alt Fashion", "seller_location": "Belo Horizonte/MG", "related_artist": "Sabrina Carpenter", "category": "camiseta_artista", "search_term": "camiseta sabrina carpenter",
     "product_url": "https://shopee.com.br/CAMISETA-SABRINA-CARPENTER-SHORT-N-SWEET-100-ALGOD%C3%83O--i.285656470.19499333370"},

    # The Weeknd - URLs reais da Shopee
    {"title": "Camiseta The Weeknd After Hours Starboy Kiss Land", "price": 49.90, "original_price": 69.90, "sold_count": 4560, "rating": 4.8, "review_count": 534, "seller_name": "Streetwear SP", "seller_location": "São Paulo/SP", "related_artist": "The Weeknd", "category": "camiseta_artista", "search_term": "camiseta the weeknd",
     "product_url": "https://shopee.com.br/Camiseta-The-Weeknd-Blusa-After-Hours-Starboy-Kiss-Land-i.348129150.10700042593"},
    {"title": "Camiseta The Weeknd Starboy", "price": 44.90, "original_price": 59.90, "sold_count": 3890, "rating": 4.7, "review_count": 456, "seller_name": "Urban Fashion BR", "seller_location": "Rio de Janeiro/RJ", "related_artist": "The Weeknd", "category": "camiseta_artista", "search_term": "camiseta the weeknd",
     "product_url": "https://shopee.com.br/Camiseta-The-Weeknd-Starboy-i.425364604.20099356765"},
    {"title": "Camiseta The Weeknd After Hours Unissex Algodão", "price": 39.90, "original_price": None, "sold_count": 5670, "rating": 4.6, "review_count": 623, "seller_name": "Hype Store", "seller_location": "São Paulo/SP", "related_artist": "The Weeknd", "category": "camiseta_artista", "search_term": "camiseta the weeknd",
     "product_url": "https://shopee.com.br/Camiseta-The-Weeknd-After-Hours-Unissex-Camisa-Blusa-Algod%C3%A3o-i.1040361865.23792367386"},

    # Bad Bunny - URLs reais da Shopee
    {"title": "Camiseta Bad Bunny Debí Tirar Más Fotos World Tour 2026 Brasil", "price": 47.90, "original_price": 64.90, "sold_count": 7890, "rating": 4.8, "review_count": 945, "seller_name": "Latin Vibes", "seller_location": "São Paulo/SP", "related_artist": "Bad Bunny", "category": "camiseta_artista", "search_term": "camiseta bad bunny",
     "product_url": "https://shopee.com.br/Camiseta-Bad-Bunny-Deb%C3%AD-Tirar-M%C3%A1s-Fotos-World-Tour-2026-Brasil-i.401790412.58251391742"},
    {"title": "Camiseta Premium Algodão T-Shirt Bad Bunny", "price": 39.90, "original_price": 54.90, "sold_count": 6230, "rating": 4.7, "review_count": 712, "seller_name": "Urban Fashion BR", "seller_location": "Rio de Janeiro/RJ", "related_artist": "Bad Bunny", "category": "camiseta_artista", "search_term": "camiseta bad bunny",
     "product_url": "https://shopee.com.br/Camiseta-Premium-Algod%C3%A3o-T-Shirt-Bad-Bunny-i.312808202.22396913142"},
    {"title": "Camiseta Bad Bunny Un Verano Sin Ti Oversize Hip Hop", "price": 54.90, "original_price": None, "sold_count": 4520, "rating": 4.9, "review_count": 567, "seller_name": "Hype Store", "seller_location": "São Paulo/SP", "related_artist": "Bad Bunny", "category": "camiseta_artista", "search_term": "camiseta bad bunny",
     "product_url": "https://shopee.com.br/2025-Ver%C3%A3o-Na-Moda-Bad-Bunny-UN-VERANO-SIN-TI-Camiseta-De-Algod%C3%A3o-Puro-Masculino-E-Feminino-Grande-Unissex-Hip-Hop-Venda-i.1576673125.42008440434"},
    {"title": "Camiseta Bad Bunny Playboy Vintage Moda Rapper Rock", "price": 42.90, "original_price": 54.90, "sold_count": 3210, "rating": 4.6, "review_count": 389, "seller_name": "Style Store", "seller_location": "São Paulo/SP", "related_artist": "Bad Bunny", "category": "camiseta_artista", "search_term": "camiseta bad bunny",
     "product_url": "https://shopee.com.br/Camiseta-Bad-Bunny-Playboy-Vintage-Moda-Rapper-Rock-i.373229837.22938119680"},

    # Doja Cat - URLs reais da Shopee
    {"title": "Camiseta Doja Cat Álbum Scarlet 100% Poliéster", "price": 44.90, "original_price": 59.90, "sold_count": 3210, "rating": 4.7, "review_count": 378, "seller_name": "Pop Culture", "seller_location": "São Paulo/SP", "related_artist": "Doja Cat", "category": "camiseta_artista", "search_term": "camiseta doja cat",
     "product_url": "https://shopee.com.br/Camiseta-Doja-Cat-%C3%81lbum-Scarlet-100-poli%C3%A9ster-i.743437716.23197347454"},
    {"title": "Camiseta Doja Cat Black Photo Tee", "price": 49.90, "original_price": None, "sold_count": 1890, "rating": 4.6, "review_count": 201, "seller_name": "Alt Fashion", "seller_location": "Belo Horizonte/MG", "related_artist": "Doja Cat", "category": "camiseta_artista", "search_term": "camiseta doja cat",
     "product_url": "https://shopee.com.br/Camiseta-Doja-Cat-Black-Photo-Tee-i.1356917260.23293474141"},

    # Black Label Society - URLs reais da Shopee
    {"title": "Camiseta Black Label Society 001 Logo Zakk Wylde Heavy Metal", "price": 44.90, "original_price": 59.90, "sold_count": 1560, "rating": 4.8, "review_count": 187, "seller_name": "Metal Merch", "seller_location": "São Paulo/SP", "related_artist": "Black Label Society", "category": "camiseta_banda", "search_term": "camiseta black label society",
     "product_url": "https://shopee.com.br/Camiseta-Black-Label-Society-001-Logo.zakk-Wylde-Heavy-Metal-i.290232265.8410681835"},
    {"title": "Camiseta Black Label Society", "price": 42.90, "original_price": None, "sold_count": 980, "rating": 4.5, "review_count": 112, "seller_name": "Rock Store BR", "seller_location": "São Paulo/SP", "related_artist": "Black Label Society", "category": "camiseta_banda", "search_term": "camiseta black label society",
     "product_url": "https://shopee.com.br/Camiseta-Black-Label-Society-i.299191059.7148454600"},

    # Tyler The Creator - URLs reais da Shopee
    {"title": "Camiseta Tyler the Creator Igor", "price": 49.90, "original_price": 69.90, "sold_count": 5340, "rating": 4.9, "review_count": 623, "seller_name": "Hype Store", "seller_location": "São Paulo/SP", "related_artist": "Tyler The Creator", "category": "camiseta_artista", "search_term": "camiseta tyler the creator",
     "product_url": "https://shopee.com.br/Camiseta-Tyler-the-Creator-Igor-i.341654163.22692784105"},
    {"title": "Camiseta 100% Algodão Golf Wang Tyler The Creator", "price": 54.90, "original_price": None, "sold_count": 3780, "rating": 4.8, "review_count": 445, "seller_name": "Streetwear SP", "seller_location": "São Paulo/SP", "related_artist": "Tyler The Creator", "category": "camiseta_artista", "search_term": "camiseta tyler creator",
     "product_url": "https://shopee.com.br/Camiseta-100-algod%C3%A3o-Golf-Wang-odd-future-tyler-the-creator-i.392918071.9131031239"},
    {"title": "Camiseta Algodão Tyler The Creator Igor Album Trap Hip Hop", "price": 44.90, "original_price": 59.90, "sold_count": 2890, "rating": 4.7, "review_count": 312, "seller_name": "Urban Fashion BR", "seller_location": "Rio de Janeiro/RJ", "related_artist": "Tyler The Creator", "category": "camiseta_artista", "search_term": "camiseta tyler creator",
     "product_url": "https://shopee.com.br/Camiseta-Algodao-Tyler-The-Creator-Igor-Album-Trap-Hip-Hop-Swag-Unissex-i.897640504.21697616659"},

    # Chappell Roan - URLs reais da Shopee
    {"title": "Camiseta Midwest Princess Chappell Roan", "price": 44.90, "original_price": 59.90, "sold_count": 4120, "rating": 4.8, "review_count": 478, "seller_name": "Pop Culture", "seller_location": "São Paulo/SP", "related_artist": "Chappell Roan", "category": "camiseta_artista", "search_term": "camiseta chappell roan",
     "product_url": "https://shopee.com.br/Camiseta-Midwest-Princess-(Chappell-Roan)-i.914351904.23797686252"},
    {"title": "CAMISETA CHAPPELL ROAN GOOD LUCK BABE MIDWEST PRINCESS", "price": 39.90, "original_price": None, "sold_count": 3560, "rating": 4.7, "review_count": 389, "seller_name": "Alt Fashion", "seller_location": "Belo Horizonte/MG", "related_artist": "Chappell Roan", "category": "camiseta_artista", "search_term": "camiseta chappell roan",
     "product_url": "https://shopee.com.br/CAMISETA-CHAPPELL-ROAN-GOOD-LUCK-BABE-MIDWEST-PRINCESS-COLLECTION-100-algod%C3%A3o--i.285656470.23797634047"},
    {"title": "CAMISETA CHAPPELL ROAN THE RISE AND FALL OF A MIDWEST PRINCESS", "price": 47.90, "original_price": 64.90, "sold_count": 2780, "rating": 4.8, "review_count": 312, "seller_name": "Rock Store BR", "seller_location": "São Paulo/SP", "related_artist": "Chappell Roan", "category": "camiseta_artista", "search_term": "camiseta chappell roan",
     "product_url": "https://shopee.com.br/CAMISETA-CHAPPELL-ROAN-THE-RISE-AND-FALL-OF-A-MIDWEST-PRINCESS-100-ALGOD%C3%83O--i.285656470.18197765160"},

    # Interpol - URLs reais da Shopee
    {"title": "Camiseta Banda Interpol", "price": 47.90, "original_price": None, "sold_count": 890, "rating": 4.7, "review_count": 102, "seller_name": "Loja Underground", "seller_location": "Curitiba/PR", "related_artist": "Interpol", "category": "camiseta_banda", "search_term": "camiseta interpol",
     "product_url": "https://shopee.com.br/Camiseta-Banda-Interpol-i.330587701.16973365359"},
    {"title": "Camiseta Feminina Interpol Turn on the Bright Lights", "price": 44.90, "original_price": 59.90, "sold_count": 560, "rating": 4.6, "review_count": 78, "seller_name": "Indie Store", "seller_location": "São Paulo/SP", "related_artist": "Interpol", "category": "camiseta_banda", "search_term": "camiseta interpol",
     "product_url": "https://shopee.com.br/Camiseta-Camisa-Feminina-Interpol-Indie-Rock-Turn-on-the-Bright-Lights-i.283482613.7542062650"},

    # Cypress Hill - URLs reais da Shopee
    {"title": "Camiseta Cypress Hill 002 Rap Hiphop", "price": 42.90, "original_price": 54.90, "sold_count": 2340, "rating": 4.6, "review_count": 278, "seller_name": "Urban Fashion BR", "seller_location": "Rio de Janeiro/RJ", "related_artist": "Cypress Hill", "category": "camiseta_banda", "search_term": "camiseta cypress hill",
     "product_url": "https://shopee.com.br/Camiseta-Cypress-Hill-002-Rap-Hiphop-i.290232265.5448134150"},
    {"title": "Camiseta Algodão Cypress Hill Hip Hop Rap Banda", "price": 39.90, "original_price": None, "sold_count": 1780, "rating": 4.5, "review_count": 189, "seller_name": "Hip Hop Store", "seller_location": "São Paulo/SP", "related_artist": "Cypress Hill", "category": "camiseta_banda", "search_term": "camiseta cypress hill",
     "product_url": "https://shopee.com.br/Camiseta-Algodao-Cypress-Hill-Hip-Hop-Rap-Banda-Cute-Engra%C3%A7ada-i.897640504.22029967758"},

    # Banda de Rock genérico - URLs reais da Shopee
    {"title": "Camiseta Banda de Rock Rolling Stones Ramones Metallica ACDC", "price": 29.90, "original_price": 44.90, "sold_count": 15670, "rating": 4.6, "review_count": 2034, "seller_name": "Rock Store BR", "seller_location": "São Paulo/SP", "related_artist": None, "category": "camiseta_generica", "search_term": "camiseta banda rock",
     "product_url": "https://shopee.com.br/Camiseta-Banda-de-Rock-Rolling-Stones-Ramones-Metallica-Acdc-store-i.742509212.23993725732"},
    {"title": "Camiseta Travis Scott Lollapalooza Astroworld", "price": 34.90, "original_price": None, "sold_count": 8900, "rating": 4.4, "review_count": 987, "seller_name": "Hype Store", "seller_location": "São Paulo/SP", "related_artist": None, "related_event": "Lollapalooza Brasil 2026", "category": "camiseta_festival", "search_term": "camiseta lollapalooza",
     "product_url": "https://shopee.com.br/Camiseta-Travis-Scott-Lollapalooza-Astroworld-Smiley-World-Camisa-i.328213523.22193250600"},
]


def seed_marketplace():
    init_db()
    db = SessionLocal()

    try:
        # Clear existing marketplace data
        db.query(MarketplaceProduct).delete()
        db.commit()

        for data in PRODUCTS:
            product = MarketplaceProduct(
                title=data["title"],
                price=data["price"],
                original_price=data.get("original_price"),
                sold_count=data.get("sold_count", 0),
                rating=data.get("rating"),
                review_count=data.get("review_count", 0),
                seller_name=data.get("seller_name"),
                seller_location=data.get("seller_location"),
                platform="shopee",
                category=data.get("category"),
                related_artist=data.get("related_artist"),
                related_event=data.get("related_event"),
                search_term=data.get("search_term"),
                product_url=data["product_url"],
                image_url=None,
            )
            db.add(product)

        db.commit()
        print(f"Seeded {len(PRODUCTS)} marketplace products")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_marketplace()
