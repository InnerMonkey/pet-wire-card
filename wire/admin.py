from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'department', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('role', 'department')}),
    )

# @admin.register(WireShape)
# class WireShapeAdmin(admin.ModelAdmin):
#     pass
    

# @admin.register(WireStatus)
# class  WireStatusAdmin(admin.ModelAdmin):
#     pass


@admin.register(WireType)
class WireTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(WireVariant)
class WireVariantAdmin(admin.ModelAdmin):
    pass


@admin.register(WirePiece)
class WirePeaceAdmin(admin.ModelAdmin):
    #autocomplete_fields = ['wire_variant']   # замість великого select
      
    #raw_id_fields = ['wire_variant']         # якщо autocomplete не підходить
    pass


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    pass


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    pass


@admin.register(WireTypeColor)
class WireTypeColorAdmin(admin.ModelAdmin):
    pass





