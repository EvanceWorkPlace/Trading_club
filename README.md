# InvestClub - Collaborative Investment Platform

InvestClub is a production-ready MVP web application for collaborative investment tracking. Users can create or join investment groups, contribute virtual funds, track pooled investments, and receive profit shares based on their contributions.

## Features

### Core Features
- **User Authentication**: JWT-based authentication with Google OAuth support
- **Virtual Wallet**: Manage funds with deposit and contribution capabilities
- **Investment Groups**: Create or join collaborative investment groups
- **Contribution Tracking**: Track individual and group contributions
- **Profit Calculation**: Automatic profit distribution based on contribution percentage
- **ROI Analytics**: Dashboard with portfolio performance metrics
- **Transaction History**: Complete audit trail of all financial activities

### System Rules
1. Each user has a virtual wallet balance
2. Users can deposit funds (simulated payment success)
3. Contributions reduce wallet balance
4. At group maturity, profits are distributed proportionally
5. Group status changes to COMPLETED after profit distribution

## Tech Stack

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt) + Google OAuth (django-allauth)
- **Caching**: Redis
- **Task Queue**: Celery (configured for future use)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **State Management**: React Context API
- **Forms**: React Hook Form

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (configured for production)

## Project Structure

```
investclub/
├── backend/                    # Django backend
│   ├── investclub/            # Main Django project
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py            # URL configuration
│   │   └── wsgi.py            # WSGI entry point
│   ├── apps/                  # Django apps
│   │   ├── accounts/          # User & Wallet management
│   │   ├── groups/            # Investment groups
│   │   ├── investments/       # Contributions & profit calculations
│   │   └── transactions/      # Transaction history
│   ├── tests/                 # Unit tests
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend Docker image
│   └── .env.example           # Environment variables template
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js app router
│   ├── components/            # React components
│   ├── contexts/              # React contexts (Auth, etc.)
│   ├── lib/                   # Utility functions & API client
│   ├── types/                 # TypeScript type definitions
│   ├── package.json           # Node dependencies
│   ├── Dockerfile             # Frontend Docker image
│   └── .env.local.example     # Environment variables template
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd investclub
```

2. Create environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

3. Update environment variables in both `.env` files with your configuration.

4. Build and start the services:
```bash
docker-compose up --build
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

6. Seed the database with sample data:
```bash
docker-compose exec backend python manage.py seed_data
```

### Default Test Users

After seeding, you can log in with these accounts:

| Email | Password | Role |
|-------|----------|------|
| admin@investclub.com | admin123 | Superuser |
| john@example.com | password123 | Regular user |
| jane@example.com | password123 | Regular user |
| mike@example.com | password123 | Regular user |
| sarah@example.com | password123 | Regular user |

## API Endpoints

### Authentication
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/register/` - User registration
- `POST /api/auth/google/` - Google OAuth login
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/update/` - Update profile
- `POST /api/auth/password/change/` - Change password

### Wallet
- `GET /api/auth/wallet/` - Get wallet details
- `POST /api/auth/wallet/deposit/` - Deposit funds
- `GET /api/auth/dashboard/` - Get dashboard stats

### Groups
- `GET /api/groups/` - List user's groups
- `POST /api/groups/` - Create new group
- `GET /api/groups/:id/` - Get group details
- `PATCH /api/groups/:id/` - Update group
- `POST /api/groups/:id/join/` - Join group
- `POST /api/groups/:id/leave/` - Leave group
- `POST /api/groups/:id/invite/` - Invite member
- `GET /api/groups/:id/members/` - Get group members
- `GET /api/groups/my_groups/` - Get all my groups
- `GET /api/groups/discover/` - Discover public groups

### Contributions
- `GET /api/investments/contributions/` - List contributions
- `POST /api/investments/contributions/` - Create contribution
- `GET /api/investments/contributions/my_contributions/` - My contributions
- `GET /api/investments/contributions/group_contributions/` - Group contributions

### Profit & Analytics
- `GET /api/investments/profits/my_distributions/` - My profit distributions
- `POST /api/investments/simulations/calculate/` - Calculate investment projection
- `GET /api/investments/analytics/roi/` - Get ROI statistics
- `GET /api/investments/analytics/portfolio_summary/` - Portfolio summary

### Transactions
- `GET /api/transactions/history/` - Transaction history
- `GET /api/transactions/summary/` - Transaction summary
- `GET /api/transactions/recent/` - Recent transactions
- `GET /api/transactions/stats/monthly_breakdown/` - Monthly breakdown

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Key Features Implementation

### Profit Calculation Service
The profit calculation service supports both simple and compound interest calculations:

```python
from apps.investments.services import ProfitCalculationService

# Simple interest
result = ProfitCalculationService.calculate_simple_interest(
    principal=10000.00,
    annual_rate=0.08,
    months=12
)

# Compound interest
result = ProfitCalculationService.calculate_compound_interest(
    principal=10000.00,
    annual_rate=0.08,
    months=12,
    compounds_per_year=12
)

# Distribute profits
ProfitCalculationService.distribute_profits(group)
```

### Authentication Flow
1. User registers/logs in via email/password or Google OAuth
2. Backend returns JWT access and refresh tokens
3. Frontend stores tokens in localStorage
4. API client automatically attaches tokens to requests
5. Token refresh happens automatically on 401 responses

### Contribution Flow
1. User deposits funds to wallet (simulated)
2. User selects a group and contributes amount
3. System validates sufficient balance
4. Wallet balance is reduced
5. Contribution record is created
6. Group totals are updated
7. If target reached, group becomes ACTIVE

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@db:5432/investclub
REDIS_URL=redis://redis:6379/0
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## Security Considerations

- JWT tokens with short expiration (1 hour access, 7 days refresh)
- Password validation (minimum 8 characters)
- CORS configured for frontend origin
- CSRF protection enabled
- Secure password hashing (Django default)
- Input validation on all endpoints

## Future Enhancements

- [ ] Real payment gateway integration (Stripe/PayPal)
- [ ] Email notifications
- [ ] Real-time updates with WebSockets
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and reporting
- [ ] Multi-currency support
- [ ] KYC/AML verification
- [ ] Two-factor authentication

## License

MIT License

## Support

For support, email support@investclub.com or open an issue on GitHub.
# Trading_club
# Trading_club
