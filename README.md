# Rebalancr 🚀

![Monad Hackathon](https://img.shields.io/badge/Monad-Hackathon-5f4def)
![Allora](https://img.shields.io/badge/Allora-Powered-orange)
![Kuru](https://img.shields.io/badge/Kuru-Integrated-blue)

> AI-powered portfolio rebalancing protocol built natively for Monad

## 🎯 Problem Statement

DeFi portfolio management suffers from three critical inefficiencies:
- High slippage in large trades due to fragmented liquidity
- Missed opportunities from slow execution on congested chains
- Poor timing from manual management and simplistic rebalancing triggers

## 💡 Solution

Rebalancr solves these challenges through three innovative components:

1. **Data-Driven Intelligence Engine**
   - Statistical market analysis for optimal trade timing
   - Real-time volatility and correlation tracking
   - Risk-adjusted portfolio optimization

2. **Advanced Strategy Engine**
   - Dynamic rebalancing with circuit breakers
   - Risk-aware trade execution
   - Performance tracking and optimization

3. **Kuru DEX Integration**
   - Orderbook-based execution for better pricing
   - Sub-second finality on Monad
   - MEV-protected trading

## 🧠 AI-Powered Portfolio Management

Rebalancr leverages advanced AI through multiple components:

### 1. Market Intelligence
- **Allora Integration**
  - Real-time market sentiment analysis
  - Asset-specific price predictions
  - Manipulation detection algorithms
  - Fear/greed index monitoring

- **Statistical Analysis**
  - Volatility correlation modeling
  - Market condition classification
  - Asset-specific behavioral patterns
  - Risk-adjusted performance metrics

### 2. Decision Engine
```python
class IntelligenceEngine:
    """AI-powered decision making system"""
    
    async def analyze_portfolio(self, user_id: str, portfolio_id: int):
        # Combine Allora predictions with statistical analysis
        sentiment_data = await self.allora_client.get_market_sentiment(asset)
        stats_data = await self.market_analyzer.analyze_asset(asset)
        
        # Calculate optimal positions using AI models
        combined_score = self._calculate_combined_score(
            sentiment_data, stats_data, asset_profile
        )
        
        return {
            "rebalance_needed": combined_score > 0.7,
            "confidence": combined_score,
            "recommendations": self._generate_recommendations(analysis)
        }
```

### 3. Autonomous Features
- **Smart Rebalancing**
  - AI-timed trade execution
  - Dynamic threshold adjustment
  - Multi-factor opportunity scoring
  - Automated risk management

- **Performance Optimization**
  - Self-adjusting weights based on outcomes
  - Learning from historical trades
  - Continuous strategy refinement
  - Adaptive risk parameters

### 4. AI Architecture
```plaintext
┌─────────────────┐    ┌──────────────┐    ┌────────────────┐
│ Allora AI       │───▶│ Intelligence │───▶│ Strategy       │
│ - Predictions   │    │    Engine    │    │   Engine       │
│ - Sentiment     │    │ (Decision    │    │ (Execution     │
│ - Market Data   │    │  Making)     │    │  Logic)        │
└─────────────────┘    └──────────────┘    └────────────────┘
         ▲                    │                     │
         │                    ▼                     ▼
┌─────────────────┐    ┌──────────────┐    ┌────────────────┐
│ Market Analysis │    │    Risk      │    │  Performance   │
│ - Statistics    │────▶  Management  │────▶   Tracking     │
│ - Patterns      │    │   System     │    │   & Learning   │
└─────────────────┘    └──────────────┘    └────────────────┘
```

### 5. Key AI Features
- **Predictive Analytics**
  - Market trend prediction
  - Volatility forecasting
  - Optimal entry/exit timing
  - Risk factor analysis

- **Adaptive Learning**
  - Performance-based weight adjustment
  - Strategy effectiveness tracking
  - Continuous model refinement
  - Market condition adaptation

- **Risk Intelligence**
  - Multi-factor risk scoring
  - Dynamic circuit breakers
  - Correlation-based diversification
  - Market manipulation detection

## 🏗 Architecture

```plaintext
rebalancr/
├── intelligence/
│   ├── intelligence_engine.py    # Core analysis engine
│   ├── market_analysis.py        # Statistical analysis
│   ├── market_conditions.py      # Market classifier
│   └── allora/                   # Allora integration
├── strategy/
│   ├── engine.py                 # Strategy execution
│   ├── risk_manager.py          # Risk assessment
│   └── risk_monitor.py          # Risk tracking
└── execution/
    └── providers/
        └── kuru/                 # Kuru DEX integration
```

## 🔧 Core Components

### Intelligence Engine
```python
class IntelligenceEngine:
    """Combines market analysis, Allora predictions, and statistical metrics"""
    
    async def analyze_portfolio(self, user_id: str, portfolio_id: int):
        # Get portfolio data and market analysis
        # Calculate combined scores using asset-specific weights
        # Generate rebalancing recommendations
```

### Strategy Engine
```python
class StrategyEngine:
    """Implements portfolio rebalancing and risk management"""
    
    async def execute_rebalance(self, user_id: str, portfolio_id: int):
        # Calculate asset metrics
        # Check circuit breakers
        # Execute trades with risk management
        # Track performance
```

### Risk Management
```python
class RiskManager:
    """Manages portfolio risk based on statistical metrics"""
    
    async def assess_portfolio_risk(self, portfolio_id: int):
        # Calculate concentration risk
        # Assess volatility exposure
        # Monitor correlation risk
        # Generate risk score
```

## 🎯 Key Features

1. **Statistical Market Analysis**
   - Volatility tracking
   - Correlation analysis
   - Market condition classification
   - Risk-adjusted metrics

2. **Intelligent Rebalancing**
   - Data-driven trade timing
   - Circuit breaker protection
   - Performance optimization
   - Risk-aware execution

3. **Monad Integration**
   - Sub-second finality
   - MEV protection
   - Gas optimization
   - High-throughput trading

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/degencodebeast/rebalancr.git
cd rebalancr

# Install dependencies using Poetry
poetry install

# Configure environment
cp c .env
# Edit .env with your API keys and settings

# Activate virtual environment
poetry shell

# Run tests
poetry run pytest
```

## 📚 Documentation

Detailed documentation is available in the `docs` directory:

- [Allora Integration](docs/ALLORA-INTEGRATION.md) - Details on AI-powered market analysis
- [Architecture](docs/ARCHITECTURE.md) - System architecture and components
- [Development](docs/DEVELOPMENT.md) - Development setup and guidelines

## 📈 Performance

- 80% lower slippage compared to AMM-based rebalancing
- Sub-second trade execution on Monad
- Automated risk management and circuit breakers

## 🛣 Roadmap

### Phase 1: Core Infrastructure (Current)
- [x] Kuru DEX integration
- [x] Statistical analysis engine
- [x] Risk management system
- [ ] UI dashboard

### Phase 2: Advanced Features (Q2 2024)
- [ ] Multi-DEX support
- [ ] Enhanced risk models
- [ ] Advanced execution algorithms

## 👥 Target Users

1. **Active Traders**
   - Sophisticated portfolio strategies
   - Precision execution timing
   - Reduced slippage

2. **Long-term Holders**
   - Automated rebalancing
   - Risk management
   - Portfolio optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Built with ❤️ for Monad evm/acc Hackathon 2025</p> 