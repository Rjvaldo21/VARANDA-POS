# Enhanced Permission System for VARANDA-POS

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

class PermissionConstants:
    """Define all available permissions in the system"""
    
    # User Management
    USERS_VIEW = 'users.view'
    USERS_CREATE = 'users.create'
    USERS_EDIT = 'users.edit'
    USERS_DELETE = 'users.delete'
    USERS_MANAGE_ROLES = 'users.manage_roles'
    
    # Product Management
    PRODUCTS_VIEW = 'products.view'
    PRODUCTS_CREATE = 'products.create'
    PRODUCTS_EDIT = 'products.edit'
    PRODUCTS_DELETE = 'products.delete'
    PRODUCTS_MANAGE_CATEGORIES = 'products.manage_categories'
    PRODUCTS_MANAGE_SUPPLIERS = 'products.manage_suppliers'
    
    # Sales & Transactions
    SALES_VIEW = 'sales.view'
    SALES_CREATE = 'sales.create'
    SALES_PROCESS = 'sales.process'
    SALES_REFUND = 'sales.refund'
    SALES_DISCOUNT = 'sales.discount'
    
    # Inventory Management
    INVENTORY_VIEW = 'inventory.view'
    INVENTORY_ADJUST = 'inventory.adjust'
    INVENTORY_TRANSFER = 'inventory.transfer'
    INVENTORY_COUNT = 'inventory.count'
    
    # Customer Management
    CUSTOMERS_VIEW = 'customers.view'
    CUSTOMERS_CREATE = 'customers.create'
    CUSTOMERS_EDIT = 'customers.edit'
    CUSTOMERS_DELETE = 'customers.delete'
    CUSTOMERS_POINTS = 'customers.points'
    
    # Financial & Reports
    REPORTS_SALES = 'reports.sales'
    REPORTS_INVENTORY = 'reports.inventory'
    REPORTS_FINANCIAL = 'reports.financial'
    REPORTS_ANALYTICS = 'reports.analytics'
    
    # Settings & Configuration
    SETTINGS_GENERAL = 'settings.general'
    SETTINGS_PAYMENT = 'settings.payment'
    SETTINGS_BACKUP = 'settings.backup'
    SETTINGS_SYSTEM = 'settings.system'
    
    # Purchase & Procurement
    PURCHASES_VIEW = 'purchases.view'
    PURCHASES_CREATE = 'purchases.create'
    PURCHASES_APPROVE = 'purchases.approve'
    PURCHASES_RETURN = 'purchases.return'

class RoleDefinition:
    """Define roles with their associated permissions"""
    
    SUPER_ADMIN = {
        'name': 'Super Admin',
        'description': 'Full system access with all permissions',
        'permissions': ['*']  # All permissions
    }
    
    ADMIN = {
        'name': 'Admin', 
        'description': 'Administrative access to most features',
        'permissions': [
            # User Management
            PermissionConstants.USERS_VIEW,
            PermissionConstants.USERS_CREATE,
            PermissionConstants.USERS_EDIT,
            PermissionConstants.USERS_MANAGE_ROLES,
            
            # Product Management
            PermissionConstants.PRODUCTS_VIEW,
            PermissionConstants.PRODUCTS_CREATE,
            PermissionConstants.PRODUCTS_EDIT,
            PermissionConstants.PRODUCTS_DELETE,
            PermissionConstants.PRODUCTS_MANAGE_CATEGORIES,
            PermissionConstants.PRODUCTS_MANAGE_SUPPLIERS,
            
            # Sales & Transactions
            PermissionConstants.SALES_VIEW,
            PermissionConstants.SALES_CREATE,
            PermissionConstants.SALES_PROCESS,
            PermissionConstants.SALES_REFUND,
            PermissionConstants.SALES_DISCOUNT,
            
            # Inventory
            PermissionConstants.INVENTORY_VIEW,
            PermissionConstants.INVENTORY_ADJUST,
            PermissionConstants.INVENTORY_TRANSFER,
            PermissionConstants.INVENTORY_COUNT,
            
            # Customer Management
            PermissionConstants.CUSTOMERS_VIEW,
            PermissionConstants.CUSTOMERS_CREATE,
            PermissionConstants.CUSTOMERS_EDIT,
            PermissionConstants.CUSTOMERS_POINTS,
            
            # Reports
            PermissionConstants.REPORTS_SALES,
            PermissionConstants.REPORTS_INVENTORY,
            PermissionConstants.REPORTS_FINANCIAL,
            PermissionConstants.REPORTS_ANALYTICS,
            
            # Purchases
            PermissionConstants.PURCHASES_VIEW,
            PermissionConstants.PURCHASES_CREATE,
            PermissionConstants.PURCHASES_APPROVE,
            PermissionConstants.PURCHASES_RETURN,
            
            # Settings
            PermissionConstants.SETTINGS_GENERAL,
            PermissionConstants.SETTINGS_PAYMENT,
            PermissionConstants.SETTINGS_BACKUP,
        ]
    }
    
    MANAGER = {
        'name': 'Manager',
        'description': 'Store manager with operational permissions',
        'permissions': [
            # Product Management (limited)
            PermissionConstants.PRODUCTS_VIEW,
            PermissionConstants.PRODUCTS_EDIT,
            PermissionConstants.PRODUCTS_MANAGE_CATEGORIES,
            
            # Sales & Transactions
            PermissionConstants.SALES_VIEW,
            PermissionConstants.SALES_CREATE,
            PermissionConstants.SALES_PROCESS,
            PermissionConstants.SALES_REFUND,
            PermissionConstants.SALES_DISCOUNT,
            
            # Inventory
            PermissionConstants.INVENTORY_VIEW,
            PermissionConstants.INVENTORY_ADJUST,
            PermissionConstants.INVENTORY_COUNT,
            
            # Customer Management
            PermissionConstants.CUSTOMERS_VIEW,
            PermissionConstants.CUSTOMERS_CREATE,
            PermissionConstants.CUSTOMERS_EDIT,
            PermissionConstants.CUSTOMERS_POINTS,
            
            # Reports (operational)
            PermissionConstants.REPORTS_SALES,
            PermissionConstants.REPORTS_INVENTORY,
            
            # Purchases (limited)
            PermissionConstants.PURCHASES_VIEW,
            PermissionConstants.PURCHASES_CREATE,
        ]
    }
    
    SUPERVISOR = {
        'name': 'Supervisor',
        'description': 'Shift supervisor with sales and customer focus',
        'permissions': [
            # Product Management (view only)
            PermissionConstants.PRODUCTS_VIEW,
            
            # Sales & Transactions
            PermissionConstants.SALES_VIEW,
            PermissionConstants.SALES_CREATE,
            PermissionConstants.SALES_PROCESS,
            PermissionConstants.SALES_DISCOUNT,
            
            # Inventory (view only)
            PermissionConstants.INVENTORY_VIEW,
            
            # Customer Management
            PermissionConstants.CUSTOMERS_VIEW,
            PermissionConstants.CUSTOMERS_CREATE,
            PermissionConstants.CUSTOMERS_EDIT,
            PermissionConstants.CUSTOMERS_POINTS,
            
            # Reports (limited)
            PermissionConstants.REPORTS_SALES,
        ]
    }
    
    CASHIER = {
        'name': 'Cashier',
        'description': 'Basic cashier operations',
        'permissions': [
            # Product Management (view only)
            PermissionConstants.PRODUCTS_VIEW,
            
            # Sales & Transactions (basic)
            PermissionConstants.SALES_VIEW,
            PermissionConstants.SALES_CREATE,
            PermissionConstants.SALES_PROCESS,
            
            # Inventory (view only)
            PermissionConstants.INVENTORY_VIEW,
            
            # Customer Management (basic)
            PermissionConstants.CUSTOMERS_VIEW,
            PermissionConstants.CUSTOMERS_CREATE,
            PermissionConstants.CUSTOMERS_POINTS,
        ]
    }
    
    INVENTORY_CLERK = {
        'name': 'Inventory Clerk',
        'description': 'Inventory and stock management specialist',
        'permissions': [
            # Product Management
            PermissionConstants.PRODUCTS_VIEW,
            PermissionConstants.PRODUCTS_EDIT,
            PermissionConstants.PRODUCTS_MANAGE_CATEGORIES,
            
            # Inventory (full access)
            PermissionConstants.INVENTORY_VIEW,
            PermissionConstants.INVENTORY_ADJUST,
            PermissionConstants.INVENTORY_TRANSFER,
            PermissionConstants.INVENTORY_COUNT,
            
            # Purchases
            PermissionConstants.PURCHASES_VIEW,
            PermissionConstants.PURCHASES_CREATE,
            
            # Reports (inventory focused)
            PermissionConstants.REPORTS_INVENTORY,
        ]
    }
    
    @classmethod
    def get_all_roles(cls):
        return {
            'super_admin': cls.SUPER_ADMIN,
            'admin': cls.ADMIN,
            'manager': cls.MANAGER,
            'supervisor': cls.SUPERVISOR,
            'cashier': cls.CASHIER,
            'inventory_clerk': cls.INVENTORY_CLERK,
        }

class PermissionChecker:
    """Helper class to check user permissions"""
    
    @staticmethod
    def has_permission(user, permission):
        """Check if user has a specific permission"""
        if not user or not user.is_authenticated:
            return False
            
        # Superusers have all permissions
        if user.is_superuser:
            return True
            
        try:
            profile = user.profile
            role_data = RoleDefinition.get_all_roles().get(profile.role)
            
            if not role_data:
                return False
                
            # Check if role has all permissions (*)
            if '*' in role_data['permissions']:
                return True
                
            return permission in role_data['permissions']
            
        except AttributeError:
            return False
    
    @staticmethod
    def has_any_permission(user, permissions):
        """Check if user has any of the given permissions"""
        return any(PermissionChecker.has_permission(user, perm) for perm in permissions)
    
    @staticmethod
    def has_all_permissions(user, permissions):
        """Check if user has all of the given permissions"""
        return all(PermissionChecker.has_permission(user, perm) for perm in permissions)
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user"""
        if not user or not user.is_authenticated:
            return []
            
        if user.is_superuser:
            # Return all available permissions
            return [getattr(PermissionConstants, attr) for attr in dir(PermissionConstants) 
                   if not attr.startswith('_')]
            
        try:
            profile = user.profile
            role_data = RoleDefinition.get_all_roles().get(profile.role)
            
            if not role_data:
                return []
                
            if '*' in role_data['permissions']:
                return [getattr(PermissionConstants, attr) for attr in dir(PermissionConstants) 
                       if not attr.startswith('_')]
                
            return role_data['permissions']
            
        except AttributeError:
            return []

class RoleBasedPermissionMixin:
    """Mixin for Django views to add role-based permission checking"""
    
    required_permissions = []
    require_all_permissions = True  # If True, user must have ALL permissions. If False, ANY permission is enough
    
    def dispatch(self, request, *args, **kwargs):
        if not self.check_permissions(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this resource.")
        return super().dispatch(request, *args, **kwargs)
    
    def check_permissions(self, user):
        if not self.required_permissions:
            return True
            
        if self.require_all_permissions:
            return PermissionChecker.has_all_permissions(user, self.required_permissions)
        else:
            return PermissionChecker.has_any_permission(user, self.required_permissions)

# Decorator for function-based views
def require_permissions(permissions, require_all=True):
    """Decorator to require specific permissions for function-based views"""
    from functools import wraps
    from django.core.exceptions import PermissionDenied
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if require_all:
                has_permission = PermissionChecker.has_all_permissions(request.user, permissions)
            else:
                has_permission = PermissionChecker.has_any_permission(request.user, permissions)
                
            if not has_permission:
                raise PermissionDenied("You don't have permission to access this resource.")
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator