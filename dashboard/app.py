import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.review_scraper import BankReviewScraper
from models.sentiment_analyzer import SentimentAnalyzer

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Page configuration
st.set_page_config(
    page_title="BankWatch Africa | Banking Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme definitions
LIGHT_THEME = {
    'bg': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
    'card': '#ffffff',
    'text': '#1f2937',
    'text_secondary': '#6b7280',
    'header': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
    'border': '#e5e7eb',
    'alert_bg': 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)',
    'alert_border': '#ef4444',
    'metric_cards': {
        'total': '#3b82f6',
        'positive': '#10b981',
        'negative': '#ef4444',
        'neutral': '#f59e0b'
    }
}

DARK_THEME = {
    'bg': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    'card': '#1f2937',
    'text': '#f9fafb',
    'text_secondary': '#9ca3af',
    'header': 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%)',
    'border': '#374151',
    'alert_bg': 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)',
    'alert_border': '#ef4444',
    'metric_cards': {
        'total': '#60a5fa',
        'positive': '#34d399',
        'negative': '#f87171',
        'neutral': '#fbbf24'
    }
}

# Get current theme
theme = LIGHT_THEME if st.session_state.theme == 'light' else DARK_THEME

# Custom CSS with theme support
st.markdown(f"""
<style>
    .main {{
        background: {theme['bg']};
        color: {theme['text']};
    }}
    .header-container {{
        background: {theme['header']};
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }}
    .header-title {{
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
    }}
    .header-subtitle {{
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
    }}
    .theme-toggle {{
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: rgba(255,255,255,0.2);
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        color: white;
        cursor: pointer;
        font-size: 0.9rem;
    }}
    .metric-card {{
        background: {theme['card']};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 5px solid;
        transition: transform 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    }}
    .metric-card.positive {{ border-left-color: {theme['metric_cards']['positive']}; }}
    .metric-card.negative {{ border-left-color: {theme['metric_cards']['negative']}; }}
    .metric-card.neutral {{ border-left-color: {theme['metric_cards']['neutral']}; }}
    .metric-card.total {{ border-left-color: {theme['metric_cards']['total']}; }}
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {theme['text']};
        margin: 0;
    }}
    .metric-label {{
        font-size: 0.85rem;
        color: {theme['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }}
    .chart-container {{
        background: {theme['card']};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }}
    .chart-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {theme['text']};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {theme['border']};
    }}
    .filter-section {{
        background: {theme['card']};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }}
    .alert-section {{
        background: {theme['alert_bg']};
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 2px solid {theme['alert_border']};
    }}
    .alert-title {{
        color: {theme['alert_border']};
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }}
    .alert-item {{
        background: {theme['card']};
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid {theme['alert_border']};
    }}
    .data-table {{
        background: {theme['card']};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    .footer {{
        text-align: center;
        padding: 2rem;
        color: {theme['text_secondary']};
        font-size: 0.9rem;
    }}
    .stButton>button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }}
    .stButton>button:hover {{
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }}
    div[data-testid="stSidebarNav"] {{
        background-color: {theme['card']};
    }}
    .stSlider label, .stMultiSelect label, .stDateInput label {{
        color: {theme['text']} !important;
        font-weight: 600 !important;
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    scraper = BankReviewScraper()
    latest = scraper.get_latest_file()
    
    if latest and os.path.exists(latest):
        df = pd.read_csv(latest)
    else:
        with st.spinner("Loading reviews..."):
            df = scraper.scrape_all_banks(count=200, days_back=365)
    
    if df.empty:
        return pd.DataFrame()
    
    df['at'] = pd.to_datetime(df['at'])
    
    analyzer = SentimentAnalyzer()
    if not analyzer.load():
        with st.spinner("Training ML model..."):
            analyzer.train(df)
    df = analyzer.analyze_df(df)
    
    return df

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.rerun()

# Load data
df = load_data()

if df.empty:
    st.error("No data available. Please check your internet connection.")
    st.stop()

# Header with theme toggle
col_header, col_toggle = st.columns([6, 1])
with col_header:
    st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">🏦 BankWatch Africa</h1>
        <p class="header-subtitle">Real-Time Banking Intelligence & Sentiment Analytics</p>
    </div>
    """, unsafe_allow_html=True)

with col_toggle:
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_label = "Dark" if st.session_state.theme == 'light' else "Light"
    if st.button(f"{theme_icon} {theme_label}", key="theme_toggle"):
        toggle_theme()

# Sidebar filters
with st.sidebar:
    st.markdown(f"### 🎛️ Filters & Controls")
    
    # Theme indicator in sidebar
    st.markdown(f"**Current Theme:** {st.session_state.theme.title()} Mode")
    st.markdown("---")
    
    # Bank filter with search
    st.markdown("**🏦 Select Banks**")
    all_banks = sorted(df['bank_name'].unique())
    selected_banks = st.multiselect(
        "Search and select banks",
        options=all_banks,
        default=all_banks,
        help="Type to search for specific banks"
    )
    
    st.markdown("---")
    
    # Date range filter
    st.markdown("**📅 Date Range**")
    
    min_date = df['at'].min().date()
    max_date = df['at'].max().date()
    
    date_option = st.radio(
        "Select date range type",
        ["Last X Days", "Custom Date Range"],
        help="Choose quick select or custom dates"
    )
    
    if date_option == "Last X Days":
        days = st.slider("Last N Days", 1, 365, 30, help="Select number of days to look back")
        start_date = max_date - timedelta(days=days)
        end_date = max_date
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("To", max_date, min_value=min_date, max_value=max_date)
    
    st.markdown("---")
    
    # Sentiment filter
    st.markdown("**💭 Sentiment Filter**")
    sentiment_options = st.multiselect(
        "Show sentiments",
        ["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"]
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.markdown("**📊 Quick Stats**")
    st.info(f"""
    • Total Reviews: {len(df):,}
    • Date Range: {df['at'].min().strftime('%b %d')} - {df['at'].max().strftime('%b %d, %Y')}
    • Banks: {len(df['bank_name'].unique())}
    """)
    
    st.markdown("---")
    st.markdown("### 🔄 Actions")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Apply filters
df_filtered = df.copy()

# Bank filter
if selected_banks:
    df_filtered = df_filtered[df_filtered['bank_name'].isin(selected_banks)]

# Date filter
df_filtered = df_filtered[
    (df_filtered['at'].dt.date >= start_date) & 
    (df_filtered['at'].dt.date <= end_date)
]

# Sentiment filter
if sentiment_options:
    df_filtered = df_filtered[df_filtered['sentiment'].isin(sentiment_options)]

if df_filtered.empty:
    st.warning("⚠️ No data matches your filters. Try adjusting the date range or bank selection.")
    st.stop()

# Metrics Section
st.markdown(f"### 📈 Key Metrics")

total_reviews = len(df_filtered)
avg_rating = df_filtered['score'].mean()
negative_pct = (df_filtered['sentiment'] == 'Negative').mean() * 100 if 'Negative' in sentiment_options else 0
positive_pct = (df_filtered['sentiment'] == 'Positive').mean() * 100 if 'Positive' in sentiment_options else 0
neutral_pct = (df_filtered['sentiment'] == 'Neutral').mean() * 100 if 'Neutral' in sentiment_options else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card total">
        <div class="metric-value">{total_reviews:,}</div>
        <div class="metric-label">Total Reviews</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card neutral">
        <div class="metric-value">{avg_rating:.1f}⭐</div>
        <div class="metric-label">Average Rating</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card negative">
        <div class="metric-value">{negative_pct:.1f}%</div>
        <div class="metric-label">Negative</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card positive">
        <div class="metric-value">{positive_pct:.1f}%</div>
        <div class="metric-label">Positive</div>
    </div>
    """, unsafe_allow_html=True)

# Active filters display
st.markdown(f"""
<div style="background: {theme['card']}; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; border-left: 4px solid #667eea;">
    <strong>🔍 Active Filters:</strong> {len(selected_banks)} banks | {start_date} to {end_date} | {', '.join(sentiment_options)} sentiments
</div>
""", unsafe_allow_html=True)

# Charts Section
st.markdown(f"### 📊 Analytics Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="chart-container">
        <div class="chart-title">Sentiment Distribution by Bank</div>
    """, unsafe_allow_html=True)
    
    if not df_filtered.empty:
        sentiment_counts = df_filtered.groupby(['bank_name', 'sentiment']).size().reset_index(name='count')
        
        colors = {'Negative': '#ef4444', 'Neutral': '#f59e0b', 'Positive': '#10b981'}
        
        fig = px.bar(
            sentiment_counts,
            x='bank_name',
            y='count',
            color='sentiment',
            color_discrete_map=colors,
            barmode='group',
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
            height=400
        )
        fig.update_layout(
            xaxis_title="Bank",
            yaxis_title="Number of Reviews",
            font=dict(color=theme['text']),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="chart-container">
        <div class="chart-title">Rating Distribution</div>
    """, unsafe_allow_html=True)
    
    if not df_filtered.empty:
        fig = px.histogram(
            df_filtered,
            x='score',
            color='bank_name',
            nbins=5,
            barmode='group',
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
            height=400,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            xaxis_title="Star Rating",
            yaxis_title="Count",
            font=dict(color=theme['text']),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            bargap=0.1
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Trends Row
st.markdown(f"### 📈 Trends Over Time")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="chart-container">
        <div class="chart-title">Daily Sentiment Trend</div>
    """, unsafe_allow_html=True)
    
    if not df_filtered.empty:
        df_filtered['date'] = df_filtered['at'].dt.date
        daily_sentiment = df_filtered.groupby(['date', 'sentiment']).size().reset_index(name='count')
        
        colors = {'Negative': '#ef4444', 'Neutral': '#f59e0b', 'Positive': '#10b981'}
        
        fig = px.line(
            daily_sentiment,
            x='date',
            y='count',
            color='sentiment',
            color_discrete_map=colors,
            markers=True,
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
            height=400
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Reviews",
            font=dict(color=theme['text']),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="chart-container">
        <div class="chart-title">Review Volume Distribution</div>
    """, unsafe_allow_html=True)
    
    if not df_filtered.empty:
        volume = df_filtered['bank_name'].value_counts().reset_index()
        volume.columns = ['bank_name', 'count']
        
        fig = px.pie(
            volume,
            values='count',
            names='bank_name',
            hole=0.5,
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
            height=400,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            font=dict(color=theme['text']),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            annotations=[dict(text=f'Total<br>{len(df_filtered):,}', x=0.5, y=0.5, 
                            font_size=18, showarrow=False, font_color=theme['text'])]
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Negative Reviews Section
if 'Negative' in sentiment_options:
    st.markdown(f"### 🚨 Negative Reviews Requiring Attention")
    
    negative_reviews = df_filtered[df_filtered['sentiment'] == 'Negative'].nlargest(10, 'at')
    
    if not negative_reviews.empty:
        st.markdown(f"""
        <div class="alert-section">
            <div class="alert-title">⚠️ Recent Negative Feedback</div>
        """, unsafe_allow_html=True)
        
        for _, row in negative_reviews.iterrows():
            st.markdown(f"""
            <div class="alert-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong style="color: {theme['text']}; font-size: 1.1rem;">{row['bank_name']}</strong>
                    <span style="background: #ef4444; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.85rem;">⭐ {row['score']}/5</span>
                </div>
                <div style="color: {theme['text_secondary']}; margin-bottom: 0.5rem; line-height: 1.5;">
                    {row['content'][:200]}{'...' if len(row['content']) > 200 else ''}
                </div>
                <div style="color: {theme['text_secondary']}; font-size: 0.8rem; display: flex; gap: 1rem;">
                    <span>📅 {pd.to_datetime(row['at']).strftime('%B %d, %Y')}</span>
                    <span>👍 {row.get('thumbsUpCount', 0)} helpful</span>
                    <span>📱 v{row.get('appVersion', 'N/A')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("✅ No negative reviews match your current filters!")

# Data Table Section
st.markdown(f"### 📋 Detailed Review Data")

with st.expander("🔍 View All Filtered Reviews"):
    st.dataframe(
        df_filtered[['at', 'bank_name', 'userName', 'score', 'sentiment', 'content', 'thumbsUpCount']].sort_values('at', ascending=False),
        use_container_width=True,
        height=400
    )

# Export Section
st.markdown(f"### 💾 Export Data")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"bankwatch_{st.session_state.theme}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    json_data = df_filtered.to_json(orient='records', date_format='iso')
    st.download_button(
        label="📥 Download as JSON",
        data=json_data,
        file_name=f"bankwatch_{st.session_state.theme}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True
    )

with col3:
    st.metric("Filtered Records", f"{len(df_filtered):,}")

# Footer
st.markdown(f"""
<div class="footer">
    <p>🏦 <strong>BankWatch Africa</strong> | Real-Time Banking Intelligence</p>
    <p>Built for African Banks | {len(df):,} total reviews analyzed | Theme: {st.session_state.theme.title()} Mode</p>
</div>
""", unsafe_allow_html=True)
