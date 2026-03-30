import pytest
from decimal import Decimal

from apps.investments.services import ProfitCalculationService


class TestSimpleInterestCalculation:
    #Tests for simple interest calculation.
    
    def test_simple_interest_basic(self):
        #Test basic simple interest calculation.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=1000.00,
            annual_rate=0.08,
            months=12
        )
        
        assert result['principal'] == 1000.00
        assert result['annual_rate'] == 0.08
        assert result['months'] == 12
        # Interest = 1000 * 0.08 * 1 = 80
        assert result['total_interest'] == 80.00
        assert result['total_amount'] == 1080.00
    
    def test_simple_interest_six_months(self):
        #Test simple interest for 6 months.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=5000.00,
            annual_rate=0.10,
            months=6
        )
        
        # Interest = 5000 * 0.10 * 0.5 = 250
        assert result['total_interest'] == 250.00
        assert result['total_amount'] == 5250.00
    
    def test_simple_interest_zero_months(self):
        #Test simple interest with zero months.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=1000.00,
            annual_rate=0.08,
            months=0
        )
        
        assert result['total_interest'] == 0.00
        assert result['total_amount'] == 1000.00
    
    def test_simple_interest_high_rate(self):
        #Test simple interest with high rate.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=10000.00,
            annual_rate=0.25,
            months=24
        )
        
        # Interest = 10000 * 0.25 * 2 = 5000
        assert result['total_interest'] == 5000.00
        assert result['total_amount'] == 15000.00
    
    def test_simple_interest_monthly_breakdown(self):
        #Test monthly breakdown in simple interest.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=1200.00,
            annual_rate=0.12,
            months=12
        )
        
        # Monthly interest = 144 / 12 = 12
        assert len(result['monthly_breakdown']) == 12
        assert result['monthly_breakdown'][0]['interest_earned'] == 12.00
        assert result['monthly_breakdown'][11]['running_total'] == 1344.00


class TestCompoundInterestCalculation:
    #Tests for compound interest calculation.
    
    def test_compound_interest_basic(self):
        #Test basic compound interest calculation
        result = ProfitCalculationService.calculate_compound_interest(
            principal=1000.00,
            annual_rate=0.08,
            months=12
        )
        
        assert result['principal'] == 1000.00
        assert result['annual_rate'] == 0.08
        assert result['months'] == 12
        # A = 1000 * (1 + 0.08/12)^12 ≈ 1083.00
        assert result['total_amount'] > 1080.00  # More than simple interest
        assert result['total_interest'] > 80.00
    
    def test_compound_interest_long_term(self):
        #Test compound interest over multiple years.
        result = ProfitCalculationService.calculate_compound_interest(
            principal=10000.00,
            annual_rate=0.08,
            months=60,  # 5 years
            compounds_per_year=12
        )
        
        # A = 10000 * (1 + 0.08/12)^60 ≈ 14898.46
        assert result['total_amount'] > 14000.00
        assert result['total_interest'] > 4000.00
    
    def test_compound_vs_simple_interest(self):
        #Test that compound interest is greater than simple interest.
        principal = 10000.00
        rate = 0.10
        months = 24
        
        simple = ProfitCalculationService.calculate_simple_interest(
            principal, rate, months
        )
        compound = ProfitCalculationService.calculate_compound_interest(
            principal, rate, months
        )
        
        assert compound['total_interest'] > simple['total_interest']
        assert compound['total_amount'] > simple['total_amount']
    
    def test_compound_interest_monthly_breakdown(self):
        #Test monthly breakdown in compound interest.
        result = ProfitCalculationService.calculate_compound_interest(
            principal=1000.00,
            annual_rate=0.12,
            months=12
        )
        
        assert len(result['monthly_breakdown']) == 12
        # Each month should have increasing interest
        first_month = result['monthly_breakdown'][0]['interest_earned']
        last_month = result['monthly_breakdown'][11]['interest_earned']
        assert last_month > first_month


class TestProfitDistribution:
    #Tests for profit distribution calculation.
    
    @pytest.fixture
    def mock_group(self):
        #Create a mock group for testing.
        class MockGroup:
            def __init__(self):
                self.current_amount = Decimal('10000.00')
                self.target_amount = Decimal('10000.00')
                self.interest_rate = Decimal('0.08')
                self.duration_months = 12
                self.status = 'ACTIVE'
        
        return MockGroup()
    
    @pytest.fixture
    def mock_memberships(self):
        #Create mock memberships for testing.
        class MockMembership:
            def __init__(self, user_id, contribution):
                self.user_id = user_id
                self.total_contributed = Decimal(str(contribution))
                self.profit_share = Decimal('0')
        
        return [
            MockMembership('user1', 5000.00),  # 50%
            MockMembership('user2', 3000.00),  # 30%
            MockMembership('user3', 2000.00),  # 20%
        ]
    
    def test_calculate_profit_distribution(self, mock_group, mock_memberships, monkeypatch):
        #Test profit distribution calculation
        # Mock the GroupMembership query
        class MockQuerySet:
            def filter(self, **kwargs):
                return self
            def __iter__(self):
                return iter(mock_memberships)
        
        monkeypatch.setattr(
            'apps.groups.models.GroupMembership.objects',
            MockQuerySet()
        )
        
        distributions = ProfitCalculationService.calculate_profit_distribution(
            mock_group,
            calculation_method='simple'
        )
        
        # Total profit should be 800 (8% of 10000)
        total_profit = sum(d['profit_share'] for d in distributions)
        assert abs(float(total_profit) - 800.00) < 0.01
        
        # Check percentages
        assert abs(float(distributions[0]['contribution_percentage']) - 50.0) < 0.01
        assert abs(float(distributions[1]['contribution_percentage']) - 30.0) < 0.01
        assert abs(float(distributions[2]['contribution_percentage']) - 20.0) < 0.01
        
        # Check profit shares
        assert abs(float(distributions[0]['profit_share']) - 400.00) < 0.01  # 50% of 800
        assert abs(float(distributions[1]['profit_share']) - 240.00) < 0.01  # 30% of 800
        assert abs(float(distributions[2]['profit_share']) - 160.00) < 0.01  # 20% of 800


class TestMemberROI:
    #Tests for member ROI calculation.    
    @pytest.fixture
    def mock_wallet(self):
        #Create a mock wallet for testing.
        class MockWallet:
            def __init__(self, contributed, earned):
                self.total_contributed = Decimal(str(contributed))
                self.total_earned = Decimal(str(earned))
        
        return MockWallet
    
    def test_roi_positive(self, mock_wallet):
        #Test positive ROI calculation.
        class MockUser:
            wallet = mock_wallet(1000.00, 1200.00)
        
        roi_data = ProfitCalculationService.get_member_roi(MockUser())
        
        assert roi_data['total_contributed'] == 1000.00
        assert roi_data['total_earned'] == 1200.00
        assert roi_data['net_profit'] == 200.00
        # ROI = (1200 - 1000) / 1000 * 100 = 20%
        assert roi_data['roi_percentage'] == 20.00
    
    def test_roi_negative(self, mock_wallet):
        #Test negative ROI calculation.
        class MockUser:
            wallet = mock_wallet(1000.00, 800.00)
        
        roi_data = ProfitCalculationService.get_member_roi(MockUser())
        
        assert roi_data['net_profit'] == -200.00
        # ROI = (800 - 1000) / 1000 * 100 = -20%
        assert roi_data['roi_percentage'] == -20.00
    
    def test_roi_zero_contribution(self, mock_wallet):
        #Test ROI with zero contribution.
        class MockUser:
            wallet = mock_wallet(0.00, 0.00)
        
        roi_data = ProfitCalculationService.get_member_roi(MockUser())
        
        assert roi_data['total_contributed'] == 0.00
        assert roi_data['total_earned'] == 0.00
        assert roi_data['roi_percentage'] == 0.00
    
    def test_roi_break_even(self, mock_wallet):
        #Test ROI at break-even point.
        class MockUser:
            wallet = mock_wallet(1000.00, 1000.00)
        
        roi_data = ProfitCalculationService.get_member_roi(MockUser())
        
        assert roi_data['net_profit'] == 0.00
        assert roi_data['roi_percentage'] == 0.00


class TestEdgeCases:
    #Tests for edge cases.
    
    def test_very_small_principal(self):
        #Test with very small principal amount
        result = ProfitCalculationService.calculate_simple_interest(
            principal=0.01,
            annual_rate=0.08,
            months=12
        )
        
        assert result['principal'] == 0.01
        assert result['total_interest'] >= 0
    
    def test_very_large_principal(self):
        #Test with very large principal amount
        result = ProfitCalculationService.calculate_simple_interest(
            principal=1000000000.00,
            annual_rate=0.05,
            months=12
        )
        
        assert result['principal'] == 1000000000.00
        assert result['total_interest'] == 50000000.00
    
    def test_zero_interest_rate(self):
        #Test with zero interest rate.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=1000.00,
            annual_rate=0.00,
            months=12
        )
        
        assert result['total_interest'] == 0.00
        assert result['total_amount'] == 1000.00
    
    def test_very_high_interest_rate(self):
        #Test with very high interest rate.
        result = ProfitCalculationService.calculate_simple_interest(
            principal=1000.00,
            annual_rate=1.00,  # 100%
            months=12
        )
        
        assert result['total_interest'] == 1000.00
        assert result['total_amount'] == 2000.00
