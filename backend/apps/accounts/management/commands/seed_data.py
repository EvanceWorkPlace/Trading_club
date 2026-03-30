from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal

from apps.accounts.models import User, Wallet
from apps.groups.models import InvestmentGroup, GroupMembership
from apps.investments.models import Contribution, ProfitDistribution
from apps.transactions.models import Transaction


class Command(BaseCommand):
    #Seed database with sample data for testing.
    
    help = 'Seed database with sample data'
    
    def handle(self, *args, **kwargs):
        #Execute the command.
        self.stdout.write('Seeding database...')
        
        with transaction.atomic():
            self.create_users()
            self.create_groups()
            self.create_contributions()
            self.create_transactions()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
    
    def create_users(self):
        #Create sample users.
        self.stdout.write('Creating users...')
        
        users_data = [
            {
                'email': 'admin@investclub.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'john@example.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'email': 'jane@example.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith'
            },
            {
                'email': 'mike@example.com',
                'password': 'password123',
                'first_name': 'Mike',
                'last_name': 'Johnson'
            },
            {
                'email': 'sarah@example.com',
                'password': 'password123',
                'first_name': 'Sarah',
                'last_name': 'Williams'
            },
        ]
        
        self.users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': data.get('is_staff', False),
                    'is_superuser': data.get('is_superuser', False)
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                
                # Add initial balance to wallet
                wallet = user.wallet
                wallet.deposit(Decimal('5000.00'))
                
                self.stdout.write(f'  Created user: {user.email}')
            else:
                self.stdout.write(f'  User exists: {user.email}')
            
            self.users.append(user)
    
    def create_groups(self):
        #Create sample investment groups.
        self.stdout.write('Creating investment groups...')
        
        groups_data = [
            {
                'name': 'Tech Startup Fund',
                'description': 'Investment group focused on tech startups',
                'target_amount': Decimal('10000.00'),
                'interest_rate': Decimal('0.1200'),
                'duration_months': 12,
                'status': 'ACTIVE',
                'created_by': self.users[0]
            },
            {
                'name': 'Real Estate Collective',
                'description': 'Group investment in real estate projects',
                'target_amount': Decimal('25000.00'),
                'interest_rate': Decimal('0.0800'),
                'duration_months': 24,
                'status': 'PENDING',
                'created_by': self.users[1]
            },
            {
                'name': 'Green Energy Fund',
                'description': 'Sustainable energy investments',
                'target_amount': Decimal('15000.00'),
                'interest_rate': Decimal('0.1000'),
                'duration_months': 18,
                'status': 'PENDING',
                'created_by': self.users[2]
            },
            {
                'name': 'Crypto Ventures',
                'description': 'Cryptocurrency and blockchain investments',
                'target_amount': Decimal('5000.00'),
                'interest_rate': Decimal('0.1500'),
                'duration_months': 6,
                'status': 'COMPLETED',
                'created_by': self.users[0]
            },
        ]
        
        self.groups = []
        for data in groups_data:
            group, created = InvestmentGroup.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'target_amount': data['target_amount'],
                    'interest_rate': data['interest_rate'],
                    'duration_months': data['duration_months'],
                    'status': data['status'],
                    'created_by': data['created_by']
                }
            )
            if created:
                self.stdout.write(f'  Created group: {group.name}')
            else:
                self.stdout.write(f'  Group exists: {group.name}')
            
            self.groups.append(group)
            
            # Add creator as admin member
            GroupMembership.objects.get_or_create(
                group=group,
                user=data['created_by'],
                defaults={'role': 'ADMIN', 'is_active': True}
            )
    
    def create_contributions(self):
        #Create sample contributions.
        self.stdout.write('Creating contributions...')
        
        contributions_data = [
            # Tech Startup Fund contributions
            {'group': self.groups[0], 'user': self.users[0], 'amount': Decimal('3000.00')},
            {'group': self.groups[0], 'user': self.users[1], 'amount': Decimal('2500.00')},
            {'group': self.groups[0], 'user': self.users[2], 'amount': Decimal('2000.00')},
            {'group': self.groups[0], 'user': self.users[3], 'amount': Decimal('1500.00')},
            {'group': self.groups[0], 'user': self.users[4], 'amount': Decimal('1000.00')},
            
            # Real Estate Collective contributions
            {'group': self.groups[1], 'user': self.users[1], 'amount': Decimal('5000.00')},
            {'group': self.groups[1], 'user': self.users[2], 'amount': Decimal('4000.00')},
            {'group': self.groups[1], 'user': self.users[3], 'amount': Decimal('3000.00')},
            
            # Green Energy Fund contributions
            {'group': self.groups[2], 'user': self.users[2], 'amount': Decimal('3500.00')},
            {'group': self.groups[2], 'user': self.users[3], 'amount': Decimal('2500.00')},
            
            # Crypto Ventures contributions (completed group)
            {'group': self.groups[3], 'user': self.users[0], 'amount': Decimal('1500.00')},
            {'group': self.groups[3], 'user': self.users[1], 'amount': Decimal('1500.00')},
            {'group': self.groups[3], 'user': self.users[2], 'amount': Decimal('1000.00')},
            {'group': self.groups[3], 'user': self.users[3], 'amount': Decimal('1000.00')},
        ]
        
        for data in contributions_data:
            # Check if user has sufficient balance
            wallet = data['user'].wallet
            if wallet.balance >= data['amount']:
                # Deduct from wallet
                wallet.contribute(data['amount'])
                
                # Create contribution
                contribution, created = Contribution.objects.get_or_create(
                    group=data['group'],
                    user=data['user'],
                    amount=data['amount'],
                    defaults={'status': 'COMPLETED'}
                )
                
                if created:
                    self.stdout.write(f'  Created contribution: {data["user"].email} - ${data["amount"]}')
                    
                    # Add member to group if not already
                    GroupMembership.objects.get_or_create(
                        group=data['group'],
                        user=data['user'],
                        defaults={'role': 'MEMBER', 'is_active': True}
                    )
            else:
                self.stdout.write(f'  Skipped contribution (insufficient balance): {data["user"].email}')
        
        # Update group amounts
        for group in self.groups:
            group.update_current_amount()
            group.update_member_count()
            
            # Activate fully funded groups
            if group.is_fully_funded and group.status == 'PENDING':
                group.activate()
                self.stdout.write(f'  Activated group: {group.name}')
    
    def create_transactions(self):
        #Create sample transactions.
        self.stdout.write('Creating transactions...')
        
        # Create deposit transactions for initial wallet funding
        for user in self.users:
            Transaction.objects.get_or_create(
                user=user,
                transaction_type='DEPOSIT',
                amount=Decimal('5000.00'),
                defaults={
                    'status': 'COMPLETED',
                    'description': 'Initial deposit'
                }
            )
        
        # Create contribution transactions
        contributions = Contribution.objects.filter(status='COMPLETED')
        for contribution in contributions:
            Transaction.objects.get_or_create(
                user=contribution.user,
                transaction_type='CONTRIBUTION',
                amount=contribution.amount,
                defaults={
                    'status': 'COMPLETED',
                    'description': f'Contribution to {contribution.group.name}',
                    'group_id': contribution.group.id
                }
            )
        
        self.stdout.write(f'  Created {Transaction.objects.count()} transactions')
