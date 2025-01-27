import yfinance as yf
import streamlit as st


class StockDataOperator:
    def __init__(self, ticker):
        self.ticker = ticker.upper() + ".NS"
        self.stock = yf.Ticker(self.ticker)
        self.info = None
        self.historical_data = None

    def fetch_data(self):
        try:
            self.info = self.stock.info
            self.historical_data = self.stock.history(period="1wk")
            return True
        except Exception as e:
            st.error(f"Data fetch failed: {e}")
            return False

    def get_all_metrics(self):
        if not self.fetch_data():
            return None

        return {
            'ticker': self.ticker,
            'current_price': self._get_current_price(),
            '52_week_high': self.info.get('fiftyTwoWeekHigh'),
            '52_week_low': self.info.get('fiftyTwoWeekLow'),
            'avg_daily_volume': self.info.get('averageVolume'),
            'weekly_volume': self._calculate_weekly_volume(),
            'pe_ratio': self.info.get('trailingPE'),
            'valuation_assessment': self._get_valuation_assessment()
        }

    def _get_current_price(self):
        return self.info.get('currentPrice') or self.info.get('regularMarketPreviousClose')

    def _calculate_weekly_volume(self):
        if self.historical_data is not None and not self.historical_data.empty:
            return self.historical_data['Volume'].sum()
        return None

    def _get_valuation_assessment(self):
        assessment = []
        pe = self.info.get('trailingPE')
        if pe:
            if pe < 15:
                assessment.append("Undervalued (P/E < 15)")
            elif pe > 35:
                assessment.append("Overvalued (P/E > 35)")
            else:
                assessment.append("Fair Valuation")
        if self._near_52_week_high():
            assessment.append("Near 52-week High")
        if self._near_52_week_low():
            assessment.append("Near 52-week Low")
        return assessment if assessment else ["No significant alerts"]

    def _near_52_week_high(self, threshold=0.95):
        high = self.info.get('fiftyTwoWeekHigh')
        current = self._get_current_price()
        return current and high and current >= high * threshold

    def _near_52_week_low(self, threshold=1.05):
        low = self.info.get('fiftyTwoWeekLow')
        current = self._get_current_price()
        return current and low and current <= low * threshold


@st.cache_data
def fetch_all_nse_tickers():
    """Return a static list of NSE tickers."""
    return [
        "WELCORP",
        "FORTIS",
        "BEL",
        "TDPOWERSYS",
        "ANANTRAJ",
        "TARIL",
        "KAYNES",
        "SOUTHBANK",
        "OLECTRA",
        "JWL",
        "PREMEXPLN",
        "FEDERALBNK"
        "AAVAS",
        "MANKIND",
        "BLS",
        "ARVINDFASN",
        "POLYMED",
        "REDTAPE",
        "SJS",
        "APTUS",
        "MEDANTA",
        "IDFCFIRSTB",
        "BIKAJI",
        "PNGJL",
        "BSOFT",
        "THOMASCOOK",
        "BAJFINANCE",
        "NH",
        "EMUDHRA",
        "SBFC",
        "VBL",
        "SHRIRAMFIN",
        "TATAELXSI",
        "BECTORFOOD",
        "ABCAPITAL",
        "KAJARIACER",
        "TATAMOTORS"
    ]


def display_results(data):
    st.subheader(f"{data['ticker']} Stock Analysis")
    st.write("### Price Information")
    st.metric("Current Price", f"₹{data['current_price']:.2f}")
    st.metric("52-Week High", f"₹{data['52_week_high']:.2f}")
    st.metric("52-Week Low", f"₹{data['52_week_low']:.2f}")

    st.write("### Valuation Metrics")
    st.write(f"**P/E Ratio:** {data['pe_ratio'] or 'N/A'}")
    st.write(f"**Average Daily Volume:** {data['avg_daily_volume']:,}" if data['avg_daily_volume'] else "N/A")
    st.write(f"**Weekly Volume:** {data['weekly_volume']:,}" if data['weekly_volume'] else "N/A")

    st.write("### Valuation Alerts")
    for alert in data['valuation_assessment']:
        if "Overvalued" in alert or "High" in alert:
            st.error(f"• {alert}")
        else:
            st.success(f"• {alert}")


def main():
    st.title("NSE Stock Analyzer")
    st.sidebar.header("Select Stock")

    # Use the static NSE tickers
    nse_tickers = fetch_all_nse_tickers()

    # Dropdown for selecting a stock
    selected_ticker = st.sidebar.selectbox("Choose a stock symbol:", nse_tickers)

    if selected_ticker:
        st.write(f"### Selected Stock: {selected_ticker}")
        analyzer = StockDataOperator(selected_ticker)
        data = analyzer.get_all_metrics()

        if data:
            display_results(data)
        else:
            st.error(f"Could not retrieve data for {selected_ticker}")


if __name__ == "__main__":
    main()
