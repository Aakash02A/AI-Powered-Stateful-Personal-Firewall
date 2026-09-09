# Agent Development Guide

This file contains project-specific information for AI agents and developers working on this codebase.

## Project Overview

AI-Powered Stateful Personal Firewall - A Next-Generation Personal Firewall (NGFW) built in Python with stateful packet inspection, rule-based filtering, signature-based IDS, ML anomaly detection, and a React dashboard.

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Database**: SQLite (with SQLAlchemy ORM)
- **Packet Capture**: Scapy (Linux), pydivert (Windows)
- **ML**: scikit-learn (Isolation Forest)
- **Task Queue**: Custom Python Queue-based implementation
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Frontend
- **Framework**: React 19 with Vite
- **UI Library**: Tailwind CSS v4
- **Charts**: Recharts
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Testing**: Vitest, React Testing Library

## Essential Commands

### Development

**Start Backend API**:
```bash
cd backend
python -m api.main
```

**Start Frontend (Development)**:
```bash
cd frontend
npm run dev
```

**Start Firewall CLI**:
```bash
cd backend
python -m firewall.cli start
```

### Testing

**Run All Tests**:
```bash
cd backend
pytest tests/ -v
```

**Run Specific Test**:
```bash
cd backend
pytest tests/test_api.py::test_get_stats -v
```

**Run Tests with Coverage**:
```bash
cd backend
pytest tests/ --cov=. --cov-report=html
```

**Frontend Tests**:
```bash
cd frontend
npm test
```

### Build & Deployment

**Build Frontend for Production**:
```bash
cd frontend
npm run build
```

**Build Desktop Application (Windows)**:
```bash
python scripts/build_desktop.py
```

**Database Migration**:
```bash
cd backend
python -m alembic upgrade head
```

**Create New Migration**:
```bash
cd backend
python -m alembic revision --autogenerate -m "description"
```

### Code Quality

**Lint Python Code**:
```bash
cd backend
flake8 .
black .
isort .
```

**Lint Frontend Code**:
```bash
cd frontend
npm run lint
```

**Security Audit**:
```bash
pip-audit
bandit -r .
```

## Project Structure

```
AI-Powered-Stateful-Personal-Firewall/
├── api/                    # FastAPI backend
│   ├── routes/            # API endpoints
│   ├── config.py          # Configuration management
│   ├── security.py       # Authentication
│   └── main.py           # Application entry point
├── firewall/             # Core firewall logic
│   ├── config/           # Rules and IDS configuration
│   ├── cli.py           # Command-line interface
│   ├── firewall.py      # Main firewall engine
│   ├── ids_engine.py    # Intrusion detection
│   ├── packet_capture.py # Packet capture
│   └── database.py      # Database operations
├── analytics/           # Traffic analysis
│   ├── flow_engine.py   # Connection tracking
│   ├── threat_scoring.py # Threat intelligence
│   └── metrics_engine.py # Performance metrics
├── ml/                  # Machine learning
│   ├── ml_detector.py   # Anomaly detection
│   ├── train_model.py   # Model training
│   └── models/          # Trained models
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/      # Page components
│   │   ├── hooks/      # Custom hooks
│   │   └── api/        # API client
│   └── package.json
├── tests/               # Test suite
│   ├── test_api.py
│   ├── test_ids_engine.py
│   └── attack_validation/
├── scripts/             # Utility scripts
├── alembic/            # Database migrations
└── data/               # Runtime data (logs, database)
```

## Configuration Management

### Environment Variables

**Backend (.env)**:
- `API_KEY`: Required for API authentication
- `HOST`: API server host (default: 127.0.0.1)
- `PORT`: API server port (default: 8000)
- `DATABASE_URL`: Database connection string
- `MONITOR_ONLY`: Safety mode (true = log only, false = active blocking)
- `CORS_ORIGINS`: Allowed CORS origins
- `ABUSEIPDB_API_KEY`: Optional threat intelligence API key

**Frontend (frontend/.env)**:
- `VITE_API_BASE_URL`: Backend API URL
- `VITE_WS_URL`: WebSocket URL
- `VITE_API_KEY`: API authentication key (must match backend)

### Setup Process

The project includes an automated setup script:
```bash
python setup.py
```

This script:
- Creates necessary directories
- Generates secure API keys
- Creates .env configuration files
- Initializes the database

## Key Architecture Patterns

### Asynchronous Queue Processing

The firewall uses a producer-consumer pattern with Python Queue:
- **Producer**: Packet capture thread pushes packets to queue
- **Consumer**: Database writer thread processes queue in batches
- **Thread Safety**: Lock-free queue operations for performance

### Stateful Packet Inspection

Connection tracking via `FlowEngine`:
- Tracks TCP connection states (SYN_SENT, ESTABLISHED, etc.)
- Maintains connection timeouts
- Calculates flow metrics (duration, bytes, packets)

### ML Anomaly Detection

Isolation Forest model:
- Trained on normal traffic patterns
- 8 features: duration, packets, bytes, rates, etc.
- Configurable contamination rate (default: 0.05)
- Auto-mitigation when anomaly score exceeds threshold

## Important Notes for Development

### API Key Management

- Never hard-code API keys in source code
- Always use environment variables
- The application will fail to start without a valid API_KEY
- Test configuration uses "test_api_key_for_testing"

### Database Handling

- Tests use temporary in-memory databases
- Production uses SQLite in `data/firewall.db`
- Always run migrations after schema changes
- Database files are gitignored

### Frontend Development

- API client is configured in `frontend/src/api/client.ts`
- WebSocket connection in `frontend/src/hooks/useWebSocket.ts`
- Environment variables must be prefixed with `VITE_`
- Development server runs on port 5173

### ML Model Management

- Trained models are stored in `ml/models/`
- Model version: v1.0
- Feature schema: `ml/models/feature_schema.json`
- Retraining required for new traffic patterns

### Security Considerations

- All API endpoints require authentication except health endpoints
- Rate limiting is enabled (default: 100/minute)
- CORS is configurable (wildcard in development)
- Input validation via Pydantic models
- SQL injection prevention via SQLAlchemy ORM

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external dependencies
- Fast execution

### Integration Tests
- API endpoint testing
- Database integration
- WebSocket communication

### Attack Validation Tests
- Simulated attack scenarios
- Port scans, SYN floods, ICMP floods
- Validates IDS detection accuracy

### Test Data
- Generated synthetic traffic
- No real user data in tests
- Temporary databases for isolation

## Common Development Tasks

### Adding New API Endpoint

1. Create route in `api/routes/`
2. Add authentication dependency: `Depends(get_api_key)`
3. Add router to `api/main.py`
4. Write tests in `tests/test_api.py`
5. Update API documentation

### Adding New Firewall Rule

1. Edit `firewall/config/rules.json`
2. Define rule properties: protocol, ports, action, priority
3. Test with `python -m firewall.cli rules`
4. Update rule engine tests if needed

### Modifying ML Features

1. Update feature extraction in analytics/
2. Retrain model: `python ml/train_model.py`
3. Update feature schema in `ml/models/feature_schema.json`
4. Test with synthetic traffic
5. Update model version

### Database Schema Changes

1. Modify SQLAlchemy models in `firewall/models.py`
2. Create migration: `python -m alembic revision --autogenerate -m "description"`
3. Review migration file
4. Apply migration: `python -m alembic upgrade head`
5. Update database tests

## Performance Considerations

### Bottlenecks
- Packet capture I/O
- Database write operations
- ML model inference

### Optimizations
- Batch database writes (Queue manager)
- Asynchronous API operations
- Connection pooling
- ML model caching

### Monitoring
- Prometheus metrics at `/metrics`
- Health endpoints at `/health/`
- Log levels configurable via LOG_LEVEL

## Troubleshooting Common Issues

### Import Errors
- Ensure you're in the project root
- Check Python path includes project directory
- Verify dependencies installed: `pip install -r requirements.txt`

### Database Locks
- Close all database connections
- Check for long-running transactions
- Verify file permissions on data directory

### ML Model Loading Errors
- Check scikit-learn version compatibility
- Verify model files exist in `ml/models/`
- Review feature schema matches training data

### Frontend Build Failures
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (requires 18.x+)
- Verify environment variables are set

## Deployment Checklist

- [ ] Set strong API keys in environment variables
- [ ] Configure appropriate CORS origins
- [ ] Set `MONITOR_ONLY=false` for active blocking
- [ ] Build frontend: `npm run build`
- [ ] Run database migrations
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Test failover procedures
- [ ] Review security settings
- [ ] Backup configuration and database

## Contact & Support

- GitHub Issues: https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall/issues
- Documentation: See README.md and ARCHITECTURE.md
- Security: See SECURITY.md for vulnerability reporting