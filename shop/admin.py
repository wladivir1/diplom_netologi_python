from django.contrib import admin

from . import models


@admin.register(models.OrderItem)
# Register your models here.
class OrderItemAdmin(admin.ModelAdmin):
    pass
    

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass
    

@admin.register(models.Category)    
class CategoryAdmin(admin.ModelAdmin):
    pass
    
    

@admin.register(models.Product)    
class ProductAdmin(admin.ModelAdmin):
    pass
    

@admin.register(models.ProductInfo)    
class ProductInfoAdmin(admin.ModelAdmin):
    pass
 
    
@admin.register(models.Shop)   
class ShopAdmin(admin.ModelAdmin):
    pass
                

@admin.register(models.Parameter)
class ParmetersAdmin(admin.ModelAdmin):
    pass
    

@admin.register(models.ProductParameter)    
class ProductParametersAdmin(admin.ModelAdmin):
    pass
