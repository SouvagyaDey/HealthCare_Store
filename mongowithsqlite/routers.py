# class ProductRouter:
#     """
#     Route DB operations for 'products' app to MongoDB,
#     but disable migrations on Mongo.
#     """
#     route_app_labels = {'products'}

#     def db_for_read(self, model, **hints):
#         if model._meta.app_label in self.route_app_labels:
#             return 'products'
#         return None

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label in self.route_app_labels:
#             return 'products'
#         return None

#     def allow_relation(self, obj1, obj2, **hints):
#         if (
#             obj1._meta.app_label in self.route_app_labels or
#             obj2._meta.app_label in self.route_app_labels
#         ):
#             return True
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         """
#         Disable migrations for MongoDB.
#         Only run migrations for SQLite (default).
#         """
#         if app_label in self.route_app_labels:
#             return False
        
#         return db == 'default'


class ProductRouter:
    """
    Route DB operations:
    - Product model → MongoDB (no migrations)
    - ProductStore & ProductReview → default (SQLite)
    """
    def db_for_read(self, model, **hints):
        if model.__name__ == "Product":
            return "products"  # Mongo
        return "default"      # SQLite

    def db_for_write(self, model, **hints):
        if model.__name__ == "Product":
            return "products"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True  # allow all relations (though cross-DB FKs won’t work)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Disable migrations for Product (Mongo)
        if model_name == "product":
            return False  
        # Allow migrations for ProductStore and ProductReview in default (SQLite)
        if model_name in ["productstore", "productreview"]:
            return db == "default"
        return None
