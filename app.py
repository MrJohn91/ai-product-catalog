import streamlit as st
import json
import os
from openai import OpenAI
import re
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Product Catalog",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.product-card {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    margin-bottom: 1.5rem;
    border-left: 4px solid #4299e1;
    border: 1px solid #4a5568;
}
.product-title {
    font-size: 1.4rem;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 0.8rem;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.product-price {
    font-size: 1.5rem;
    font-weight: bold;
    color: #48bb78;
    margin-bottom: 0.8rem;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.product-category {
    background: linear-gradient(135deg, #4299e1, #3182ce);
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    color: #ffffff;
    display: inline-block;
    margin-bottom: 0.8rem;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.product-description {
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 0.8rem;
}
.product-rating {
    color: #fed7d7;
    font-size: 0.9rem;
    font-weight: 500;
}
.search-hint {
    background: linear-gradient(135deg, #1a365d 0%, #2a4a6b 100%);
    padding: 1.2rem;
    border-radius: 10px;
    border-left: 4px solid #4299e1;
    margin-bottom: 1.5rem;
    color: #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.search-hint strong {
    color: #90cdf4;
}
.filter-summary {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    padding: 1.2rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    border: 1px solid #4a5568;
    color: #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.filter-summary strong {
    color: #4299e1;
}
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    openai_available = True
except:
    openai_available = False
    st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")



# Load product data
@st.cache_data
def load_products():
    with open("products.json", "r") as f:
        return json.load(f)

products = load_products()

# AI-powered filter extraction
def extract_filters_with_ai(query):
    if not openai_available:
        return None
    
    prompt = f"""
    Analyze this product search query and extract relevant filters in JSON format:
    
    Query: "{query}"
    
    Extract:
    - category: product category/type (e.g., "shoes", "electronics", "clothing")
    - max_price: maximum price if mentioned (number only)
    - min_price: minimum price if mentioned (number only) 
    - min_rating: minimum rating if mentioned (1-5 scale)
    - keywords: important product features or brands mentioned
    
    Return valid JSON only:
    {{
        "category": "category_name or null",
        "max_price": number_or_null,
        "min_price": number_or_null,
        "min_rating": number_or_null,
        "keywords": ["keyword1", "keyword2"] or null
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        
        content = response.choices[0].message.content.strip()
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        st.error(f"processing error: {str(e)}")
    
    return None

# Enhanced filtering function
def filter_products(products, filters, query=""):
    if not filters:
        # Fallback to simple text search
        if query:
            query_lower = query.lower()
            return [p for p in products if 
                   query_lower in p.get('name', '').lower() or 
                   query_lower in p.get('description', '').lower() or
                   query_lower in p.get('category', '').lower()]
        return products
    
    filtered = products.copy()
    
    # Category filter
    if filters.get('category'):
        category = filters['category'].lower()
        filtered = [p for p in filtered if category in p.get('category', '').lower()]
    
    # Price filters
    if filters.get('max_price') is not None:
        filtered = [p for p in filtered if p.get('price', 0) <= filters['max_price']]
    
    if filters.get('min_price') is not None:
        filtered = [p for p in filtered if p.get('price', 0) >= filters['min_price']]
    
    # Rating filter
    if filters.get('min_rating') is not None:
        filtered = [p for p in filtered if p.get('rating', 0) >= filters['min_rating']]
    
    # Keywords filter
    if filters.get('keywords'):
        for keyword in filters['keywords']:
            keyword = keyword.lower()
            filtered = [p for p in filtered if 
                       keyword in p.get('name', '').lower() or 
                       keyword in p.get('description', '').lower()]
    
    return filtered

def display_product_card(product):
    with st.container():
        st.markdown(f"""
        <div class="product-card">
            <div class="product-title">{product.get('name', 'Unknown Product')}</div>
            <div class="product-price">${product.get('price', 0):.2f}</div>
            <span class="product-category">{product.get('category', 'Uncategorized')}</span>
            <div class="product-rating"><strong>Rating:</strong> {'⭐' * int(product.get('rating', 0))} ({product.get('rating', 0)}/5)</div>
            <p class="product-description">{product.get('description', 'No description available')}</p>
        </div>
        """, unsafe_allow_html=True)

# Main App
st.title("Product Catalog")

# Sidebar for traditional filters
with st.sidebar:
    st.header("Filters")
    
    # Traditional filters
    categories = list(set([p.get('category', 'Unknown') for p in products]))
    selected_category = st.selectbox("Category", ["All"] + sorted(categories))
    
    price_range = st.slider("Price Range", 0, 1000, (0, 1000))
    min_rating = st.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.1)

# Main search interface
search_query = st.text_input("🔍 Search products")

# Search button
if st.button("Search", type="primary") or search_query:
    if search_query and openai_available:
        with st.spinner("🤖 Processing your request with AI..."):
            ai_filters = extract_filters_with_ai(search_query)
            
        if ai_filters:
            # Display extracted filters
            st.markdown("""
            <div class="filter-summary">
            """, unsafe_allow_html=True)
            
            filter_parts = []
            if ai_filters.get('category'): filter_parts.append(f"Category: {ai_filters['category']}")
            if ai_filters.get('max_price'): filter_parts.append(f"Max Price: ${ai_filters['max_price']}")
            if ai_filters.get('min_price'): filter_parts.append(f"Min Price: ${ai_filters['min_price']}")
            if ai_filters.get('min_rating'): filter_parts.append(f"Min Rating: {ai_filters['min_rating']} stars")
            if ai_filters.get('keywords'): filter_parts.append(f"Keywords: {', '.join(ai_filters['keywords'])}")
            
            st.write(" | ".join(filter_parts) if filter_parts else "General search")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Apply AI filters
            filtered_products = filter_products(products, ai_filters, search_query)
        else:
            filtered_products = filter_products(products, None, search_query)
    else:
        # Apply traditional filters
        filtered_products = products.copy()
        
        if selected_category != "All":
            filtered_products = [p for p in filtered_products if p.get('category') == selected_category]
        
        filtered_products = [p for p in filtered_products if 
                           price_range[0] <= p.get('price', 0) <= price_range[1] and
                           p.get('rating', 0) >= min_rating]

    # Display results
    st.header(f"📋 Results ({len(filtered_products)} found)")
    
    if filtered_products:
        # Display in columns for better layout
        for i in range(0, len(filtered_products), 2):
            cols = st.columns(2)
            
            with cols[0]:
                display_product_card(filtered_products[i])
            
            if i + 1 < len(filtered_products):
                with cols[1]:
                    display_product_card(filtered_products[i + 1])
    else:
        st.warning("😔 No products found matching your criteria. Try adjusting your search.")
        
        # Suggestions
        st.info("💡 **Suggestions:**\n"
                "- Try broader search terms\n" 
                "- Check available categories in the sidebar\n"
                "- Adjust price range or rating filters")
